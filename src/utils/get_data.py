"""Récupération des données publiques du projet SportÉgalité.

Deux sources sont téléchargées, puis enregistrées sans modification
dans data/raw/ et dans une table « raw » SQLite par source :

- les équipements sportifs -> table raw ;
- les installations sportives -> table raw_installations.
"""
import json
import sqlite3
from contextlib import closing
from pathlib import Path

import pandas as pd
import requests

from config import (
    DATABASE_PATH,
    EQUIPEMENTS_CSV,
    EQUIPEMENTS_URL,
    INSTALLATIONS_CSV,
    INSTALLATIONS_URL,
    POPULATION_JSON,
    POPULATION_URL,
)

# Colonnes brutes conservées pour chaque source
COLONNES_EQUIPEMENTS = [
    "Numéro de l'équipement sportif",
    "Numéro de l'installation sportive",
    "Nom de l'équipement sportif",
    "Type d'équipement sportif",
    "Nature de l'équipement sportif",
    "Surface de l'aire d'évolution",
    "Commune INSEE",
    "Commune nom",
    "Longitude",
    "Latitude",
]
COLONNES_INSTALLATIONS = [
    "numero",
    "nom",
    "insee",
    "com_name",
    "dep_code",
    "dep_nom",
    "reg_nom",
    "dens_lib",
    "coordonnees",
]


def telecharger_fichier(url: str, destination: Path) -> None:
    """Télécharge un fichier CSV officiel, sans le modifier."""

    # Créer le dossier de destination si nécessaire
    destination.parent.mkdir(parents=True, exist_ok=True)

    print(f"Téléchargement de {destination.name} en cours...")

    # Télécharger les données progressivement
    with requests.get(url, stream=True, timeout=120) as response:
        response.raise_for_status()

        # Enregistrer les données sans les modifier
        with destination.open("wb") as fichier:
            for bloc in response.iter_content(chunk_size=1024 * 1024):
                if bloc:
                    fichier.write(bloc)

    print(f"Téléchargement terminé : {destination}")


def telecharger_equipements() -> None:
    """Télécharge le fichier CSV officiel des équipements sportifs."""
    telecharger_fichier(EQUIPEMENTS_URL, EQUIPEMENTS_CSV)


def telecharger_installations() -> None:
    """Télécharge le fichier CSV officiel des installations sportives."""
    telecharger_fichier(INSTALLATIONS_URL, INSTALLATIONS_CSV)


def importer_equipements_sqlite() -> None:
    """Enregistre les données brutes utiles des équipements dans la table raw."""

    DATABASE_PATH.parent.mkdir(parents=True, exist_ok=True)

    with closing(sqlite3.connect(DATABASE_PATH)) as connexion:
        # Lecture par blocs : le fichier complet est trop lourd pour la mémoire
        blocs = pd.read_csv(
            EQUIPEMENTS_CSV,
            sep=";",
            usecols=COLONNES_EQUIPEMENTS,
            dtype=str,
            chunksize=10_000,
        )
        for numero_bloc, bloc in enumerate(blocs):
            bloc.to_sql(
                name="raw",
                con=connexion,
                if_exists="replace" if numero_bloc == 0 else "append",
                index=False,
            )
        connexion.commit()

    print("Importation SQLite des équipements terminée.")


def importer_installations_sqlite() -> None:
    """Enregistre les données brutes utiles des installations dans raw_installations."""

    DATABASE_PATH.parent.mkdir(parents=True, exist_ok=True)

    # dtype=str : les valeurs brutes sont conservées sans conversion
    donnees = pd.read_csv(
        INSTALLATIONS_CSV,
        sep=";",
        usecols=COLONNES_INSTALLATIONS,
        dtype=str,
    )

    with closing(sqlite3.connect(DATABASE_PATH)) as connexion:
        donnees.to_sql(
            name="raw_installations",
            con=connexion,
            if_exists="replace",
            index=False,
        )
        connexion.commit()

    print("Importation SQLite des installations terminée.")

def telecharger_population() -> None:
    """Télécharge la population des communes depuis l'API Découpage administratif."""
    telecharger_fichier(POPULATION_URL, POPULATION_JSON)

def importer_population_sqlite() -> None:
    """Enregistre la population brute des communes dans la table raw_population."""

    DATABASE_PATH.parent.mkdir(parents=True, exist_ok=True)

    # parse_int=str : les nombres restent en texte, exactement comme dans le fichier
    with POPULATION_JSON.open(encoding="utf-8") as fichier:
        communes = json.load(fichier, parse_int=str, parse_float=str)

    # json_normalize transforme la région imbriquée {"code": ..., "nom": ...}
    # en deux colonnes : region.code et region.nom
    donnees = pd.json_normalize(communes)

    with closing(sqlite3.connect(DATABASE_PATH)) as connexion:
        donnees.to_sql(
            name="raw_population",
            con=connexion,
            if_exists="replace",
            index=False,
        )
        connexion.commit()

    print("Importation SQLite de la population terminée.")

if __name__ == "__main__":
    telecharger_equipements()
    importer_equipements_sqlite()
    telecharger_installations()
    importer_installations_sqlite()
    telecharger_population()
    importer_population_sqlite()
