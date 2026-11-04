"""Tests du nettoyage des équipements sportifs."""

import sqlite3
from contextlib import closing
from pathlib import Path

import pandas as pd
import pytest

from src.utils import clean_data


@pytest.fixture
def base_temporaire(tmp_path, monkeypatch):
    """Crée une petite base SQLite uniquement pour les tests."""
    chemin = tmp_path / "test.sqlite"

    donnees = pd.DataFrame(
        {
            "Surface de l'aire d'évolution": [
                "100",
                "0",
                "-50",
                "250",
                None,
                "inconnue",
            ],
            "Nature de l'équipement sportif": [
                "Intérieur",
                "Découvert",
                "Intérieur",
                "Découvert",
                "Intérieur",
                "Découvert",
            ],
        }
    )

    with sqlite3.connect(chemin) as connexion:
        donnees.to_sql("raw", connexion, index=False)

    monkeypatch.setattr(clean_data, "DATABASE_PATH", chemin)
    return chemin


def test_nettoyage_surfaces(base_temporaire):
    """Vérifie le traitement des surfaces valides et invalides."""
    clean_data.nettoyer_equipements()

    with sqlite3.connect(base_temporaire) as connexion:
        surfaces = pd.read_sql_query(
            "SELECT surface_m2 FROM cleaned",
            connexion,
        )["surface_m2"]

    assert surfaces.iloc[0] == 100
    assert pd.isna(surfaces.iloc[1])
    assert pd.isna(surfaces.iloc[2])
    assert surfaces.iloc[3] == 250
    assert pd.isna(surfaces.iloc[4])
    assert pd.isna(surfaces.iloc[5])


def test_nombre_lignes(base_temporaire):
    """Vérifie que le nettoyage conserve toutes les lignes."""
    clean_data.nettoyer_equipements()

    with sqlite3.connect(base_temporaire) as connexion:
        nombre_raw = connexion.execute('SELECT COUNT(*) FROM "raw"').fetchone()[0]

        nombre_cleaned = connexion.execute('SELECT COUNT(*) FROM "cleaned"').fetchone()[
            0
        ]

    assert nombre_raw == nombre_cleaned == 6


def test_nettoyer_population(tmp_path: Path, monkeypatch: pytest.MonkeyPatch) -> None:
    """Le nettoyage renomme les colonnes, garde les populations valides et sans doublon."""
    base_test = tmp_path / "test.sqlite"
    monkeypatch.setattr(clean_data, "DATABASE_PATH", base_test)

    brut = pd.DataFrame(
        {
            "code": ["35238", "59350", "35238", "99999", "88888"],
            "nom": ["Rennes", "Lille", "Rennes", "Sans population", "Vide"],
            "population": ["227830", "236710", "227830", "0", None],
            "codeDepartement": ["35", "59", "35", "99", "88"],
            "codeRegion": ["53", "32", "53", "00", "00"],
            "region.nom": ["Bretagne", "Hauts-de-France", "Bretagne", "X", "Y"],
        }
    )
    with closing(sqlite3.connect(base_test)) as connexion:
        brut.to_sql("raw_population", connexion, index=False)

    clean_data.nettoyer_population()

    with closing(sqlite3.connect(base_test)) as connexion:
        propre = pd.read_sql_query("SELECT * FROM cleaned_population", connexion)

    assert list(propre.columns) == [
        "code_commune",
        "nom_commune",
        "population",
        "code_departement",
        "code_region",
        "nom_region",
    ]
    assert sorted(propre["nom_commune"]) == ["Lille", "Rennes"]
    assert propre.set_index("code_commune").loc["35238", "population"] == 227830
