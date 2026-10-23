"""Téléchargement des installations sportives."""

import requests
from config import INSTALLATIONS_CSV, INSTALLATIONS_URL, DATABASE_PATH
import sqlite3
import pandas as pd



def telecharger_installations() -> None:
    """Télécharge les installations sportives au format CSV."""
    INSTALLATIONS_CSV.parent.mkdir(parents=True, exist_ok=True)

    print("Téléchargement des installations sportives...")

    with requests.get(
        INSTALLATIONS_URL,
        stream=True,
        timeout=120,
    ) as response:
        response.raise_for_status()

        with INSTALLATIONS_CSV.open("wb") as fichier:
            for bloc in response.iter_content(
                chunk_size=1024 * 1024
            ):
                if bloc:
                    fichier.write(bloc)

    print("Téléchargement terminé !")


def importer_installation_sqlite()-> None : 
    """ Enregistre les données brutes utiles dans SQLite """
    colonnes= ["numero", "nom", "insee", "com_name", "dep_code",
        "dep_nom", "reg_nom", "dens_lib", "coordonnees"]

    DATABASE_PATH.parent.mkdir(parents=True, exist_ok=True)

    with sqlite3.connect(DATABASE_PATH) as connexion :
        # dtype=str : on garde les valeurs brutes, sans conversion
        donnees= pd.read_csv(INSTALLATIONS_CSV,sep=";", usecols=colonnes , dtype="str")
        donnees.to_sql("raw_installations", connexion, if_exists="replace", index=False)

    print("Importation SQLite des installations terminée.") 


if __name__ == "__main__":
    telecharger_installations()
    importer_installation_sqlite()