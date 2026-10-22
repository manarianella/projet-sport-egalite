"""Récupération des données publiques du projet SportÉgalité."""
import sqlite3
import pandas as pd
import requests

from config import DATABASE_PATH, EQUIPEMENTS_CSV, EQUIPEMENTS_URL


def telecharger_equipements() -> None:
    """Télécharge le fichier CSV officiel des équipements sportifs."""

    # Créer le dossier de destination si nécessaire
    EQUIPEMENTS_CSV.parent.mkdir(parents=True, exist_ok=True)

    print("Téléchargement des équipements sportifs en cours...")

    # Télécharger les données progressivement
    with requests.get(
        EQUIPEMENTS_URL,
        stream=True,
        timeout=120,
    ) as response:
        response.raise_for_status()

        # Enregistrer les données sans les modifier
        with EQUIPEMENTS_CSV.open("wb") as fichier:
            for bloc in response.iter_content(chunk_size=1024 * 1024):
                if bloc:
                    fichier.write(bloc)

    print(f"Téléchargement terminé : {EQUIPEMENTS_CSV}")

def importer_equipements_sqlite() -> None:
    """Enregistre les données brutes utiles des équipements dans SQLite."""

    colonnes = [
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

    DATABASE_PATH.parent.mkdir(parents=True, exist_ok=True)

    with sqlite3.connect(DATABASE_PATH) as connexion:
        premier_bloc = True

        for bloc in pd.read_csv(
            EQUIPEMENTS_CSV,
            sep=";",
            usecols=colonnes,
            dtype=str,
            chunksize=10_000,
        ):
            bloc.to_sql(
                name="raw",
                con=connexion,
                if_exists="replace" if premier_bloc else "append",
                index=False,
            )

            premier_bloc = False

    print("Importation SQLite des équipements terminée.")

if __name__ == "__main__":
    telecharger_equipements()