"""Tests automatiques de l'histogramme SportÉgalité."""

import sqlite3

import pytest

from config import DATABASE_PATH
from src.components.histogram import creer_histogramme


@pytest.mark.parametrize(
    "nature",
    ["Tous", "Intérieur", "Découvert", "Extérieur couvert"],
)
def test_histogramme_categories(nature):
    """Vérifie que chaque nature produit un diagramme en barres."""
    figure = creer_histogramme(nature=nature)

    assert len(figure.data) == 1
    assert figure.data[0].type == "bar"
    assert len(figure.data[0].x) == 50
    assert len(figure.data[0].y) == 50


def test_histogramme_intervalles():
    """Vérifie que les 50 intervalles de surfaces sont fixes."""
    figure = creer_histogramme(nature="Intérieur")
    barres = figure.data[0]

    assert len(barres.x) == 50
    assert barres.x[0] == pytest.approx(108)
    assert barres.x[-1] == pytest.approx(10692)
    assert barres.width == pytest.approx(205.2)

    assert list(figure.layout.xaxis.range) == [0, 10800]
    assert figure.layout.xaxis.fixedrange is True


def test_histogramme_echelle_regionale():
    """Vérifie que les régions conservent la même échelle Y."""
    figure_bretagne = creer_histogramme(region="Bretagne")
    figure_normandie = creer_histogramme(region="Normandie")

    assert list(figure_bretagne.layout.yaxis.range) == [0, 7500]
    assert list(figure_normandie.layout.yaxis.range) == [0, 7500]


def test_histogramme_effectifs():
    """Vérifie que le total des barres correspond aux données SQLite."""
    figure = creer_histogramme(nature="Tous")

    with sqlite3.connect(DATABASE_PATH) as connexion:
        total = connexion.execute(
            """
            SELECT COUNT(*)
            FROM cleaned
            WHERE surface_m2 > 0
              AND surface_m2 <= 10800
            """
        ).fetchone()[0]

    assert sum(figure.data[0].y) == total


def test_histogramme_infobulles():
    """Vérifie la présence des informations détaillées au survol."""
    figure = creer_histogramme(region="Bretagne")
    barres = figure.data[0]

    assert len(barres.customdata) == 50

    assert "Types majoritaires" in barres.hovertemplate
    assert "Population" in barres.hovertemplate
    assert "10 000 hab." in barres.hovertemplate

    assert len(barres.customdata[0]) == 6


def test_histogramme_sans_annotation():
    """Vérifie que le graphique ne contient pas d'annotation inutile."""
    figure = creer_histogramme()

    assert not figure.layout.annotations
    assert figure.data[0].type == "bar"
