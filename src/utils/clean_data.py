"""Nettoyage des données sportives pour le dashboard SportÉgalité."""

import sqlite3

import pandas as pd

from config import DATABASE_PATH


def nettoyer_equipements() -> None:
    """Nettoie les surfaces et crée la table SQLite cleaned."""

    with sqlite3.connect(DATABASE_PATH) as connexion:
        # Lire les équipements présents dans la table brute
        donnees = pd.read_sql_query(
            'SELECT * FROM "raw"',
            connexion,
        )

        # Convertir les surfaces en valeurs numériques
        surfaces = pd.to_numeric(
            donnees["Surface de l'aire d'évolution"],
            errors="coerce",
        )

        # Une surface nulle ou négative n'est pas exploitable
        donnees["surface_m2"] = surfaces.where(surfaces > 0)

        # Ajouter la catégorie d'origine sans la modifier
        donnees["nature_equipement"] = (
            donnees["Nature de l'équipement sportif"]
        )

        # Enregistrer la version nettoyée
        donnees.to_sql(
            "cleaned",
            connexion,
            if_exists="replace",
            index=False,
        )

    print("Nettoyage terminé : table cleaned créée.")


if __name__ == "__main__":
    nettoyer_equipements()