"""Carte des installations sportives regroupées en bulles selon le zoom."""

import sqlite3
from contextlib import closing
from functools import lru_cache

import pandas as pd
import plotly.graph_objects as go

from config import DATABASE_PATH

# Colonne de regroupement et nom affiché, pour chaque niveau de zoom
CLES_NIVEAUX = {"region": "region", "departement": "code_departement", "commune": "code_commune"}
NOMS_NIVEAUX = {"region": "region", "departement": "departement", "commune": "nom_commune"}
# Vue de départ : la France entière, ou une région
CENTRE_FRANCE = {"lat": 46.6, "lon": 2.5}
ZOOM_FRANCE = 4.6
ZOOM_REGION = 6.5

# Vue France : régions, puis départements, puis communes quand on zoome
SEUIL_REGIONS = 6.0
SEUIL_DEPARTEMENTS = 8.0

# Communes affichées au départ d'une région ; le nombre double à chaque zoom
COMMUNES_VUE_REGION = 40
MAX_COMMUNES = 1500

STYLE_CARTE = "carto-positron"
ECHELLE_COULEURS = ["#9CC3EA", "#5A9BD8", "#2F7BC4", "#1A4F8B", "#0B2545"]
COULEUR_SANS_POPULATION = "#B8C2CC"


def charger_donnees() -> tuple[pd.DataFrame, pd.DataFrame, pd.DataFrame]:
    """Charge installations, équipements et population depuis la base."""
    with closing(sqlite3.connect(DATABASE_PATH)) as connexion:
        installations = pd.read_sql_query(
            "SELECT region, code_departement, departement, code_commune, nom_commune, "
            "latitude, longitude FROM cleaned_installations",
            connexion,
        )
        equipements = pd.read_sql_query(
            "SELECT region, code_departement, code_commune, "
            "\"Type d'équipement sportif\" AS type_equipement FROM cleaned",
            connexion,
        )
        population = pd.read_sql_query(
            "SELECT code_commune, code_departement, population FROM cleaned_population",
            connexion,
        )
    # On donne sa région à chaque commune grâce à son département
    regions = installations.groupby("code_departement")["region"].first()
    population["region"] = population["code_departement"].map(regions)
    return installations, equipements, population


def types_principaux(equipements: pd.DataFrame, cle: str) -> pd.Series:
    """Liste les 3 types d'équipements les plus présents dans chaque territoire."""
    comptes = equipements.groupby([cle, "type_equipement"]).size().rename("total").reset_index()
    comptes = comptes.sort_values([cle, "total"], ascending=[True, False])
    premiers = comptes.groupby(cle).head(3)
    libelles = premiers["type_equipement"] + " (" + premiers["total"].astype(str) + ")"
    return libelles.groupby(premiers[cle]).agg(", ".join)


def compter_par_niveau(
    installations: pd.DataFrame,
    equipements: pd.DataFrame,
    population: pd.DataFrame,
    niveau: str,
) -> pd.DataFrame:
    """Calcule une bulle par territoire : position, nombres, population et ratio."""
    cle = CLES_NIVEAUX[niveau]
    bulles = installations.groupby(cle).agg(
        nom=(NOMS_NIVEAUX[niveau], "first"),
        nom_region=("region", "first"),
        latitude=("latitude", "mean"),
        longitude=("longitude", "mean"),
        installations=("latitude", "size"),
    )
    bulles["equipements"] = equipements.groupby(cle).size()
    bulles["types"] = types_principaux(equipements, cle)
    bulles["population"] = population.groupby(cle)["population"].sum()
    bulles["pour_10000"] = bulles["installations"] / bulles["population"] * 10_000
    return bulles.fillna({"equipements": 0, "types": "aucun"}).reset_index()


@lru_cache(maxsize=1)
def preparer_niveaux() -> dict[str, pd.DataFrame]:
    """Calcule une seule fois les bulles des trois niveaux de zoom."""
    installations, equipements, population = charger_donnees()
    return {
        niveau: compter_par_niveau(installations, equipements, population, niveau)
        for niveau in CLES_NIVEAUX
    }

def choisir_niveau(zoom: float) -> str:
    """Choisit le niveau de regroupement de la vue France selon le zoom."""
    if zoom < SEUIL_REGIONS:
        return "region"
    if zoom < SEUIL_DEPARTEMENTS:
        return "departement"
    return "commune"


def filtrer_vue(bulles: pd.DataFrame, centre: dict[str, float], zoom: float) -> pd.DataFrame:
    """Garde les communes visibles à l'écran, les plus équipées en priorité."""
    demi_largeur = 720 / 2**zoom  # taille approximative de l'écran, en degrés
    visibles = bulles[
        bulles["longitude"].between(centre["lon"] - demi_largeur, centre["lon"] + demi_largeur)
        & bulles["latitude"].between(centre["lat"] - demi_largeur * 0.7, centre["lat"] + demi_largeur * 0.7)
    ]
    nombre = COMMUNES_VUE_REGION * 2 ** max(0.0, zoom - ZOOM_REGION)
    return visibles.nlargest(min(int(nombre), MAX_COMMUNES), "installations")

def tailles_bulles(installations: pd.Series) -> pd.Series:
    """Calcule la taille des bulles : la surface est proportionnelle au nombre."""
    maximum = installations.max() if len(installations) else 1
    return 18 + 42 * (installations / maximum) ** 0.5


def formater(nombre: float) -> str:
    """Écrit un nombre avec une espace comme séparateur de milliers."""
    if pd.isna(nombre):
        return "non disponible"
    return f"{nombre:,.0f}".replace(",", " ")


def formater_ratio(ratio: float) -> str:
    """Écrit le ratio pour 10 000 habitants avec une décimale."""
    if pd.isna(ratio):
        return "non disponible"
    return f"{ratio:.1f}".replace(".", ",")


def textes_survol(bulles: pd.DataFrame) -> list[str]:
    """Construit le texte affiché au survol de chaque bulle."""
    return [
        f"<b>{ligne.nom}</b><br>"
        f"Population : {formater(ligne.population)} habitants<br>"
        f"Installations sportives : {formater(ligne.installations)}<br>"
        f"Équipements sportifs : {formater(ligne.equipements)}<br>"
        f"Installations pour 10 000 habitants : {formater_ratio(ligne.pour_10000)}<br>"
        f"Équipements les plus présents : {ligne.types}"
        for ligne in bulles.itertuples()
    ]

def trace_bulles(bulles: pd.DataFrame, marqueur: dict) -> go.Scattermap:
    """Crée une couche de bulles avec le ratio pour 10 000 habitants écrit dedans."""
    marqueur["size"] = tailles_bulles(bulles["installations"])
    return go.Scattermap(
        lat=bulles["latitude"],
        lon=bulles["longitude"],
        mode="markers+text",
        marker=marqueur,
        text=[formater_ratio(ratio) for ratio in bulles["pour_10000"]],
        textfont={"color": "white", "size": 11, "weight": "bold"},
        hovertext=textes_survol(bulles),
        hoverinfo="text",
        name="",
    )


def creer_carte_bulles(
    bulles: pd.DataFrame,
    centre: dict[str, float],
    zoom: float,
    cle_vue: str,
    echelle: tuple[float, float],
) -> go.Figure:
    """Crée la carte : une bulle par territoire, colorée selon son ratio."""
    sans_population = bulles["pour_10000"].isna()
    avec_population = bulles[~sans_population]
    couleurs = {
        "color": avec_population["pour_10000"],
        "colorscale": ECHELLE_COULEURS,
        "cmin": echelle[0],
        "cmax": echelle[1],
        "opacity": 0.9,
        "colorbar": {"title": {"text": "Installations<br>pour 10 000 hab."}, "thickness": 12, "len": 0.6},
    }
    figure = go.Figure(
        [
            trace_bulles(bulles[sans_population], {"color": COULEUR_SANS_POPULATION}),
            trace_bulles(avec_population, couleurs),
        ]
    )
    figure.update_layout(
        map={"style": STYLE_CARTE, "center": centre, "zoom": zoom},
        margin={"l": 0, "r": 0, "t": 0, "b": 0},
        height=590,
        showlegend=False,
        uirevision=cle_vue,  # garde le zoom de l'utilisateur quand la carte est redessinée
    )
    return figure

