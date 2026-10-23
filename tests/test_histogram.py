"""Tests automatiques de l'histogramme SportÉgalité."""

import pytest

from src.components.histogram import creer_histogramme


@pytest.mark.parametrize(
    "nature",
    ["Tous", "Intérieur", "Découvert", "Extérieur couvert"],
)
def test_histogramme_categories(nature):
    """Vérifie que chaque catégorie produit un graphique."""
    figure = creer_histogramme(nature=nature)

    assert len(figure.data) == 1
    assert figure.data[0].type == "histogram"


def test_histogramme_intervalles():
    """Vérifie que les intervalles de surface restent fixes."""
    figure = creer_histogramme(nature="Intérieur")

    assert figure.data[0].xbins.start == 0
    assert figure.data[0].xbins.end == 10800
    assert figure.data[0].xbins.size == 216


def test_histogramme_annotation():
    """Vérifie que les effectifs sont indiqués."""
    figure = creer_histogramme()

    assert len(figure.layout.annotations) > 0
    assert "surfaces valides" in figure.layout.annotations[0].text
