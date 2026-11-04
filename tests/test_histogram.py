"""Tests automatiques de l'histogramme SportÉgalité."""

import sqlite3
from collections.abc import Iterator
from contextlib import closing
from pathlib import Path

import pandas as pd
import pytest

from src.components import histogram
from src.components.histogram import creer_histogramme


@pytest.fixture(name="base_test", autouse=True)
def fixture_base_test(
    tmp_path: Path, monkeypatch: pytest.MonkeyPatch
) -> Iterator[None]:
    """Crée une petite base temporaire : les tests ne lisent pas la vraie base."""
    base = tmp_path / "test.sqlite"
    equipements = pd.DataFrame(
        {
            "surface_m2": [100.0, 150.0, 500.0, 6000.0, 6100.0, 0.0, 20000.0],
            "Type d'équipement sportif": [
                "Court de tennis",
                "Court de tennis",
                "Salle multisports",
                "Terrain de football",
                "Terrain de football",
                "Boulodrome",
                "Golf",
            ],
            "nature_equipement": [
                "Découvert",
                "Découvert",
                "Intérieur",
                "Découvert",
                "Extérieur couvert",
                "Découvert",
                "Découvert",
            ],
            "region": [
                "Bretagne",
                "Bretagne",
                "Bretagne",
                "Normandie",
                "Normandie",
                "Bretagne",
                "Bretagne",
            ],
        }
    )
    population = pd.DataFrame(
        {
            "code_commune": ["35238", "14118"],
            "population": [200_000, 100_000],
            "nom_region": ["Bretagne", "Normandie"],
        }
    )
    with closing(sqlite3.connect(base)) as connexion:
        equipements.to_sql("cleaned", connexion, index=False)
        population.to_sql("cleaned_population", connexion, index=False)

    monkeypatch.setattr(histogram, "DATABASE_PATH", base)
    # L'échelle nationale est gardée en mémoire : on la recalcule pour chaque test
    histogram.calculer_maximum_y.cache_clear()
    yield
    histogram.calculer_maximum_y.cache_clear()


def test_histogramme_intervalles() -> None:
    """Les 50 intervalles de surfaces sont fixes, de 0 à 10 800 m²."""
    figure = creer_histogramme()
    barres = figure.data[0]

    assert barres.x[0] == pytest.approx(108)
    assert barres.x[-1] == pytest.approx(10692)
    assert barres.width == pytest.approx(205.2)
    assert list(figure.layout.xaxis.range) == [0, 10800]
    assert figure.layout.xaxis.fixedrange is True


def test_histogramme_effectifs() -> None:
    """Les surfaces nulles ou supérieures à 10 800 m² ne sont pas comptées."""
    figure = creer_histogramme()

    # 7 équipements, dont une surface à 0 et une à 20 000 m² exclues
    assert sum(figure.data[0].y) == 5


def test_histogramme_filtres() -> None:
    """La nature et la région réduisent le nombre d'équipements comptés."""
    assert sum(creer_histogramme(nature="Intérieur").data[0].y) == 1
    assert sum(creer_histogramme(region="Bretagne").data[0].y) == 3
    assert sum(creer_histogramme(nature="Découvert", region="Bretagne").data[0].y) == 2


def test_histogramme_echelle_regionale() -> None:
    """Toutes les régions gardent la même échelle verticale."""
    figure_bretagne = creer_histogramme(region="Bretagne")
    figure_normandie = creer_histogramme(region="Normandie")

    assert list(figure_bretagne.layout.yaxis.range) == [0, 7500]
    assert list(figure_normandie.layout.yaxis.range) == [0, 7500]


def test_histogramme_infobulles() -> None:
    """Le survol affiche les types majoritaires, la population et le ratio."""
    barres = creer_histogramme(region="Bretagne").data[0]
    premiere_barre = barres.customdata[0]

    assert len(barres.customdata) == 50
    assert premiere_barre[2] == "Bretagne"
    assert premiere_barre[3] == "1. Court de tennis : 2"
    assert premiere_barre[4] == "200 000"
    # 2 équipements pour 200 000 habitants : 0,10 pour 10 000 habitants
    assert premiere_barre[5] == "0,10"
