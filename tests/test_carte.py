"""Tests de la carte à bulles des installations sportives."""

import pandas as pd
import pytest

from src.components.map_chart import (
    choisir_niveau,
    compter_par_niveau,
    creer_carte_bulles,
    filtrer_vue,
    types_principaux,
)


@pytest.fixture(name="installations")
def fixture_installations() -> pd.DataFrame:
    """Trois installations à Rennes et deux à Lille."""
    return pd.DataFrame(
        {
            "region": ["Bretagne"] * 3 + ["Hauts-de-France"] * 2,
            "code_departement": ["35"] * 3 + ["59"] * 2,
            "departement": ["Ille-et-Vilaine"] * 3 + ["Nord"] * 2,
            "code_commune": ["35238"] * 3 + ["59350"] * 2,
            "nom_commune": ["Rennes"] * 3 + ["Lille"] * 2,
            "latitude": [48.10, 48.12, 48.11, 50.63, 50.64],
            "longitude": [-1.68, -1.66, -1.67, 3.06, 3.07],
        }
    )


@pytest.fixture(name="equipements")
def fixture_equipements() -> pd.DataFrame:
    """Trois équipements à Rennes et deux à Lille."""
    return pd.DataFrame(
        {
            "region": ["Bretagne"] * 3 + ["Hauts-de-France"] * 2,
            "code_departement": ["35"] * 3 + ["59"] * 2,
            "code_commune": ["35238"] * 3 + ["59350"] * 2,
            "type_equipement": [
                "Court de tennis",
                "Court de tennis",
                "Terrain de football",
                "Boulodrome",
                "Boulodrome",
            ],
        }
    )


@pytest.fixture(name="population")
def fixture_population() -> pd.DataFrame:
    """Population de Rennes et de Lille."""
    return pd.DataFrame(
        {
            "code_commune": ["35238", "59350"],
            "code_departement": ["35", "59"],
            "region": ["Bretagne", "Hauts-de-France"],
            "population": [300_000, 200_000],
        }
    )


def test_compter_par_commune(
    installations: pd.DataFrame, equipements: pd.DataFrame, population: pd.DataFrame
) -> None:
    """Chaque commune devient une bulle avec ses nombres et sa population."""
    bulles = compter_par_niveau(installations, equipements, population, "commune")
    rennes = bulles.set_index("code_commune").loc["35238"]

    assert len(bulles) == 2
    assert rennes["nom"] == "Rennes"
    assert rennes["installations"] == 3
    assert rennes["equipements"] == 3
    assert rennes["population"] == 300_000
    assert rennes["pour_10000"] == pytest.approx(0.1)


def test_compter_par_region(
    installations: pd.DataFrame, equipements: pd.DataFrame, population: pd.DataFrame
) -> None:
    """Au niveau région, les installations et la population sont additionnées."""
    bulles = compter_par_niveau(installations, equipements, population, "region")

    assert bulles["installations"].sum() == 5
    assert bulles["population"].sum() == 500_000


def test_types_principaux(equipements: pd.DataFrame) -> None:
    """Les types les plus présents sont listés du plus au moins nombreux."""
    types = types_principaux(equipements, "code_commune")

    assert types["35238"] == "Court de tennis (2), Terrain de football (1)"
    assert types["59350"] == "Boulodrome (2)"


@pytest.mark.parametrize(
    ("zoom", "niveau"),
    [(4.6, "region"), (7.0, "departement"), (9.0, "commune")],
)
def test_choisir_niveau(zoom: float, niveau: str) -> None:
    """Plus on zoome, plus le regroupement est fin."""
    assert choisir_niveau(zoom) == niveau


def test_filtrer_vue_garde_les_communes_visibles(
    installations: pd.DataFrame, equipements: pd.DataFrame, population: pd.DataFrame
) -> None:
    """Centrée sur Rennes avec un fort zoom, la carte n'affiche pas Lille."""
    bulles = compter_par_niveau(installations, equipements, population, "commune")
    visibles = filtrer_vue(bulles, {"lat": 48.11, "lon": -1.67}, 9.0)

    assert list(visibles["nom"]) == ["Rennes"]


def test_creer_carte_bulles(
    installations: pd.DataFrame, equipements: pd.DataFrame, population: pd.DataFrame
) -> None:
    """La carte contient une bulle par commune, avec le ratio écrit dedans."""
    bulles = compter_par_niveau(installations, equipements, population, "commune")
    figure = creer_carte_bulles(bulles, {"lat": 46.6, "lon": 2.5}, 5.0, "test", (0, 1))

    assert len(figure.data[1].lat) == 2
    assert "0,1" in figure.data[1].text
