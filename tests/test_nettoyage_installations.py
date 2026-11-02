"""Tests des fonctions de nettoyage des installations sportives."""

import pandas as pd

from src.utils.clean_data import (
    filtrer_coordonnees_valides,
    regrouper_arrondissements,
    separer_coordonnees,
)


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
