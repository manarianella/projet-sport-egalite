"""Carte des installations sportives (points par région, densité nationale)."""

import sqlite3
from contextlib import closing

import pandas as pd
import plotly.express as px
import plotly.graph_objects as go

from config import DATABASE_PATH

# Vue d'ensemble : centre de la France métropolitaine
CENTRE_FRANCE = {"lat": 46.6, "lon": 2.5}

# Taille d'une case de la grille (en degrés, environ 5 km) pour alléger la carte
PAS_GRILLE = 0.05


def agreger_par_grille(installations: pd.DataFrame) -> pd.DataFrame:
    """Regroupe les installations par case de grille et compte chaque case."""
    grille = pd.DataFrame(
        {
            "latitude": (installations["latitude"] / PAS_GRILLE).round() * PAS_GRILLE,
            "longitude": (installations["longitude"] / PAS_GRILLE).round() * PAS_GRILLE,
        }
    )
    return grille.value_counts().reset_index(name="nombre")



def charger_installations() -> pd.DataFrame:
    """Charge les installations nettoyées utiles à la carte."""
    requete = """
        SELECT nom_installation, commune, departement, region,
               type_territoire, latitude, longitude
        FROM cleaned_installations
    """
    with closing(sqlite3.connect(DATABASE_PATH)) as connexion:
        return pd.read_sql_query(requete, connexion)


def creer_carte(installations: pd.DataFrame) -> go.Figure:
    """Crée une carte où chaque point est une installation sportive."""
    figure = px.scatter_map(
        installations,
        lat="latitude",
        lon="longitude",
        hover_name="nom_installation",
        hover_data={
            "commune": True,
            "departement": True,
            "latitude": False,
            "longitude": False,
        },
        center={
            "lat": installations["latitude"].mean(),
            "lon": installations["longitude"].mean(),
        },
        zoom=6,
        map_style="carto-positron",
    )
    figure.update_traces(marker={"size": 4, "opacity": 0.6})
    figure.update_layout(margin={"l": 0, "r": 0, "t": 0, "b": 0})
    return figure


def creer_carte_densite(installations: pd.DataFrame) -> go.Figure:
    """Carte de densité des installations sportives sur toute la France."""
    figure = px.density_map(
        agreger_par_grille(installations),
        lat="latitude",
        lon="longitude",
        z="nombre",
        radius=8,
        # Échelle élargie : sans elle, la carte est saturée
        range_color=[0, 30],
        center=CENTRE_FRANCE,
        zoom=4.3,
        map_style="carto-positron",
        color_continuous_scale=[
            [0.0, "rgba(232, 243, 255, 0)"],
            [0.25, "#B8D7F5"],
            [0.55, "#4387D2"],
            [0.80, "#21569A"],
            [1.0, "#102747"],
        ],
    )

    # Le survol n'apporte rien ici : la vue détaillée se fait par région
    figure.update_traces(hoverinfo="skip", hovertemplate=None)

    figure.update_layout(
        height=590,
        margin={"l": 0, "r": 0, "t": 0, "b": 0},
        paper_bgcolor="#FFFFFF",
        font={"family": "Arial", "color": "#142D4E"},
        coloraxis_colorbar={
            "title": "Densité relative",
            "thickness": 12,
            "len": 0.65,
            "outlinewidth": 0,
        },
    )
    return figure


if __name__ == "__main__":
    installations = charger_installations()
    # Test sur un échantillon : 144 000 points ralentiraient le navigateur
    echantillon = installations.sample(n=5000, random_state=0)
    figure = creer_carte(echantillon)
    figure.write_html("carte_test.html")
    print("Carte enregistrée dans carte_test.html")
