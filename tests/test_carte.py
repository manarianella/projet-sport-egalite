"""Tests de la carte des installations sportives (sans base de données)."""

import pandas as pd
import plotly.graph_objects as go
import pytest

from config import TOUTE_LA_FRANCE
from src.components import map_layout
from src.components.map_chart import (
    agreger_par_grille,
    creer_carte,
    creer_carte_densite,
)


@pytest.fixture(name="installations")
def fixture_installations() -> pd.DataFrame:
    """Petit jeu d'installations fictives réparties dans deux régions."""
    return pd.DataFrame(
        {
            "nom_installation": ["Gymnase A", "Stade B", "Piscine C"],
            "commune": ["Rennes", "Rennes", "Lille"],
            "departement": ["Ille-et-Vilaine", "Ille-et-Vilaine", "Nord"],
            "region": ["Bretagne", "Bretagne", "Hauts-de-France"],
            "type_territoire": ["Grands centres urbains"] * 3,
            "latitude": [48.111, 48.112, 50.63],
            "longitude": [-1.680, -1.681, 3.06],
        }
    )


def test_agreger_par_grille_conserve_le_total(installations: pd.DataFrame) -> None:
    """Le regroupement par cases ne perd ni n'ajoute aucune installation."""
    grille = agreger_par_grille(installations)

    assert grille["nombre"].sum() == len(installations)


def test_agreger_par_grille_regroupe_les_points_proches(
    installations: pd.DataFrame,
) -> None:
    """Deux installations très proches tombent dans la même case."""
    grille = agreger_par_grille(installations)

    # Les deux installations de Rennes ne forment qu'une case, Lille une autre
    assert len(grille) == 2
    assert sorted(grille["nombre"]) == [1, 2]


def test_creer_carte_renvoie_une_carte_de_points(installations: pd.DataFrame) -> None:
    """La carte régionale affiche un point par installation."""
    figure = creer_carte(installations)

    assert isinstance(figure, go.Figure)
    assert isinstance(figure.data[0], go.Scattermap)
    assert len(figure.data[0].lat) == len(installations)


def test_creer_carte_densite_renvoie_une_carte_de_densite(
    installations: pd.DataFrame,
) -> None:
    """La vue nationale est une carte de densité."""
    figure = creer_carte_densite(installations)

    assert isinstance(figure.data[0], go.Densitymap)


def test_lister_regions_commence_par_toute_la_france(
    installations: pd.DataFrame, monkeypatch: pytest.MonkeyPatch
) -> None:
    """Le menu propose « Toute la France » puis les régions triées."""
    # On remplace la lecture de la base par le jeu de test
    monkeypatch.setattr(map_layout, "charger_installations", lambda: installations)

    regions = map_layout.lister_regions()

    assert regions == [TOUTE_LA_FRANCE, "Bretagne", "Hauts-de-France"]


def test_actualiser_carte_toute_la_france(
    installations: pd.DataFrame, monkeypatch: pytest.MonkeyPatch
) -> None:
    """« Toute la France » affiche la carte de densité."""
    monkeypatch.setattr(map_layout, "charger_installations", lambda: installations)

    figure = map_layout.actualiser_carte(TOUTE_LA_FRANCE)

    assert isinstance(figure.data[0], go.Densitymap)


def test_actualiser_carte_une_region(
    installations: pd.DataFrame, monkeypatch: pytest.MonkeyPatch
) -> None:
    """Une région n'affiche que ses propres installations."""
    monkeypatch.setattr(map_layout, "charger_installations", lambda: installations)

    figure = map_layout.actualiser_carte("Bretagne")

    assert isinstance(figure.data[0], go.Scattermap)
    assert len(figure.data[0].lat) == 2
