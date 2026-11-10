"""Tests du nettoyage des équipements sportifs."""

import sqlite3
from contextlib import closing
from pathlib import Path

import pandas as pd
import pytest

from src.utils import clean_data
from src.utils.clean_data import (
    filtrer_coordonnees_valides,
    regrouper_arrondissements,
    separer_coordonnees,
)


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


def test_separer_coordonnees_cree_latitude_et_longitude() -> None:
    """Le texte « lat, lon » est découpé en deux colonnes numériques."""
    donnees = pd.DataFrame({"coordonnees": ["47.197956, -0.281652"]})

    resultat = separer_coordonnees(donnees)

    assert "coordonnees" not in resultat.columns
    assert resultat.loc[0, "latitude"] == 47.197956
    assert resultat.loc[0, "longitude"] == -0.281652


def test_separer_coordonnees_valeurs_invalides() -> None:
    """Une position absente ou non numérique devient une valeur manquante."""
    donnees = pd.DataFrame({"coordonnees": [None, "abc, def"]})

    resultat = separer_coordonnees(donnees)

    assert resultat["latitude"].isna().all()
    assert resultat["longitude"].isna().all()


def test_filtrer_coordonnees_valides() -> None:
    """Seules les positions possibles et différentes de (0, 0) sont gardées."""
    donnees = pd.DataFrame(
        {
            "nom": ["valide", "zero", "hors_limites", "manquante"],
            "latitude": [48.85, 0.0, 120.0, None],
            "longitude": [2.35, 0.0, 2.0, 2.0],
        }
    )

    resultat = filtrer_coordonnees_valides(donnees)

    assert list(resultat["nom"]) == ["valide"]


def test_regrouper_arrondissements_paris_marseille_lyon() -> None:
    """Chaque arrondissement est remplacé par le code et le nom de sa ville."""
    codes = pd.Series(["75101", "75120", "13216", "69383"])
    noms = pd.Series(["Paris 1er", "Paris 20e", "Marseille 16e", "Lyon 3e"])

    codes_ville, noms_ville = regrouper_arrondissements(codes, noms)

    assert list(codes_ville) == ["75056", "75056", "13055", "69123"]
    assert list(noms_ville) == ["Paris", "Paris", "Marseille", "Lyon"]


def test_regrouper_arrondissements_autres_communes_inchangees() -> None:
    """Les autres communes, y compris en Corse, ne sont pas modifiées."""
    codes = pd.Series(["35238", "2A004", "75056"])
    noms = pd.Series(["Rennes", "Ajaccio", "Paris"])

    codes_ville, noms_ville = regrouper_arrondissements(codes, noms)

    assert list(codes_ville) == ["35238", "2A004", "75056"]
    assert list(noms_ville) == ["Rennes", "Ajaccio", "Paris"]


def test_regrouper_arrondissements_ne_modifie_pas_les_originaux() -> None:
    """Les colonnes d'origine restent intactes (on travaille sur des copies)."""
    codes = pd.Series(["75101"])
    noms = pd.Series(["Paris 1er"])

    regrouper_arrondissements(codes, noms)

    assert codes[0] == "75101"
    assert noms[0] == "Paris 1er"
