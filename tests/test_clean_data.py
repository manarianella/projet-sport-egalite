"""Tests du nettoyage des équipements sportifs."""

import sqlite3

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
