"""Nettoyage des données sportives pour le dashboard SportÉgalité."""

import sqlite3
import pandas as pd
from config import DATABASE_PATH
from contextlib import closing


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

COLONNES_INSTALLATIONS = {
    "numero": "numero_installation",
    "nom": "nom_installation",
    "insee": "code_insee",
    "com_name": "commune",
    "dep_code": "code_departement",
    "dep_nom": "departement",
    "reg_nom": "region",
    "dens_lib": "type_territoire",
}

def separer_coordonnees(donnees: pd.DataFrame) -> pd.DataFrame:
    """Découpe la colonne texte "lat, lon" en deux colonnes numériques."""

    morceaux = donnees["coordonnees"].str.split(",", n=1, expand=True)
    donnees["latitude"] = pd.to_numeric(morceaux[0], errors="coerce")
    donnees["longitude"] = pd.to_numeric(morceaux[1], errors="coerce")
    return donnees.drop(columns="coordonnees")


def filtrer_coordonnees_valides(donnees: pd.DataFrame) -> pd.DataFrame:
    
    """Retire les installations sans position ou avec une position impossible."""
    latitude_ok = donnees["latitude"].between(-90, 90)
    longitude_ok = donnees["longitude"].between(-180, 180)
    # Le point (0, 0) est dans l'océan Atlantique : c'est une valeur par défaut
    pas_zero = ~((donnees["latitude"] == 0) & (donnees["longitude"] == 0))
    return donnees[latitude_ok & longitude_ok & pas_zero]

def nettoyer_installations() -> None:
    """Nettoie les installations et crée la table SQLite cleaned_installations."""
    with closing(sqlite3.connect(DATABASE_PATH)) as connexion:
        donnees = pd.read_sql_query('SELECT * FROM "raw_installations"', connexion)
        nombre_brut = len(donnees)

        # Une installation ne doit apparaître qu'une seule fois
        donnees = donnees.drop_duplicates(subset="numero")

        donnees = separer_coordonnees(donnees)
        donnees = filtrer_coordonnees_valides(donnees)

        # La source écrit "2" au lieu de "02" : on remet le zéro manquant
        donnees["dep_code"] = donnees["dep_code"].str.zfill(2)

        donnees = donnees.rename(columns=COLONNES_INSTALLATIONS)
        donnees.to_sql(
            "cleaned_installations", connexion, if_exists="replace", index=False
        )

    print(
        f"Installations : {nombre_brut} brutes, {len(donnees)} conservées, "
        f"{nombre_brut - len(donnees)} exclues."
    )


if __name__ == "__main__":
    nettoyer_equipements()