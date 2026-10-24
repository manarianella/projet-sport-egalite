"""Histogramme des surfaces des équipements sportifs."""

import sqlite3
from contextlib import closing

import pandas as pd
import plotly.express as px
from plotly.graph_objects import Figure

from config import DATABASE_PATH

COULEURS_NATURE = {
    "Tous": "#4387D2",
    "Intérieur": "#16A6A1",
    "Découvert": "#4387D2",
    "Extérieur couvert": "#F0A35B",
}


def construire_filtres(nature: str, region: str | None) -> tuple[str, list[str]]:
    """Construit les filtres SQL selon la nature et la région."""

    filtres = ""
    parametres: list[str] = []

    if nature != "Tous":
        filtres += " AND nature_equipement = ?"
        parametres.append(nature)

    if region is not None:
        filtres += " AND region = ?"
        parametres.append(region)

    return filtres, parametres


def creer_histogramme(
    nature: str = "Tous",
    region: str | None = None,
    surface_max: float = 10800,
) -> Figure:
    """Crée un histogramme des surfaces des équipements sportifs."""

    filtres, parametres = construire_filtres(nature, region)

    with closing(sqlite3.connect(DATABASE_PATH)) as connexion:
        requete_surfaces = f"""
            SELECT surface_m2
            FROM cleaned
            WHERE surface_m2 > 0
              AND surface_m2 <= ? {filtres}
        """

        donnees = pd.read_sql_query(
            requete_surfaces,
            connexion,
            params=[surface_max, *parametres],
        )

    figure = px.histogram(
        donnees,
        x="surface_m2",
        nbins=50,
        title=None,
        labels={"surface_m2": "Surface de l'aire de pratique (m²)"},
    )

    figure.update_traces(
        xbins={
            "start": 0,
            "end": surface_max,
            "size": surface_max / 50,
        },
        marker_color=COULEURS_NATURE.get(nature, "#4387D2"),
        marker_line_color="#FFFFFF",
        marker_line_width=0.5,
        opacity=0.9,
        hovertemplate=(
            "<b>Équipements sportifs</b>"
            "<br>Surface : %{x}"
            "<br>Nombre d'équipements : %{y}"
            "<extra></extra>"
        ),
    )

    figure.update_xaxes(
        range=[0, surface_max],
    )

    figure.update_layout(
        paper_bgcolor="#FFFFFF",
        plot_bgcolor="#FFFFFF",
        font={
            "family": "Arial",
            "color": "#142D4E",
            "size": 13,
        },
        hoverlabel={
            "bgcolor": "#142D4E",
            "font_color": "#FFFFFF",
            "font_size": 13,
        },
        yaxis_title="Nombre d'équipements",
        bargap=0.05,
        template="plotly_white",
        margin={
            "l": 45,
            "r": 20,
            "t": 20,
            "b": 55,
        },
    )

    return figure
