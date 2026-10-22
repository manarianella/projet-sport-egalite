"""Histogramme des surfaces des équipements sportifs."""

import sqlite3

import pandas as pd
import plotly.express as px
from plotly.graph_objects import Figure

from config import DATABASE_PATH


def creer_histogramme(
    nature: str = "Tous",
    surface_max: float = 10800,
) -> Figure:
    """Crée un histogramme des surfaces selon la nature choisie."""

    with sqlite3.connect(DATABASE_PATH) as connexion:
        donnees = pd.read_sql_query(
            """
            SELECT surface_m2, nature_equipement
            FROM cleaned
            WHERE surface_m2 > 0
            """,
            connexion,
        )

    # Filtrer les équipements selon leur nature.
    if nature != "Tous":
        donnees = donnees[donnees["nature_equipement"] == nature]

    # Limiter uniquement l'affichage, pas les données stockées.
    donnees = donnees[donnees["surface_m2"] <= surface_max]

    figure = px.histogram(
        donnees,
        x="surface_m2",
        nbins=50,
        title=f"Distribution des surfaces — {nature}",
        labels={"surface_m2": "Surface de l'aire de pratique (m²)"},
    )

    # Conserver les mêmes intervalles pour toutes les catégories
    figure.update_traces(
        xbins={
            "start": 0,
            "end": surface_max,
            "size": surface_max / 50,
        }
    )

    # Conserver la même plage sur l'axe horizontal
    figure.update_xaxes(range=[0, surface_max])

    figure.update_layout(
        yaxis_title="Nombre d'équipements",
        bargap=0.05,
        template="plotly_white",
    )

    return figure
