"""Histogramme des surfaces des équipements sportifs."""

import sqlite3

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


def creer_histogramme(
    nature: str = "Tous",
    surface_max: float = 10800,
) -> Figure:
    """Crée un histogramme des surfaces selon les filtres choisis."""

    # Sélectionner la catégorie directement dans SQLite.
    filtre_nature = ""
    parametres = []

    if nature != "Tous":
        filtre_nature = " AND nature_equipement = ?"
        parametres.append(nature)

    with sqlite3.connect(DATABASE_PATH) as connexion:
        # Calculer les effectifs sans charger toutes les surfaces.
        requete_effectifs = f"""
            SELECT
                COUNT(*) AS nombre_total,
                SUM(
                    CASE WHEN surface_m2 > ? THEN 1 ELSE 0 END
                ) AS nombre_hors_plage
            FROM cleaned
            WHERE surface_m2 > 0 {filtre_nature}
        """

        effectifs = pd.read_sql_query(
            requete_effectifs,
            connexion,
            params=[surface_max, *parametres],
        )

        nombre_total = int(effectifs.loc[0, "nombre_total"])
        nombre_hors_plage = int(effectifs.loc[0, "nombre_hors_plage"] or 0)

        # Charger uniquement les surfaces visibles.
        requete_surfaces = f"""
            SELECT surface_m2
            FROM cleaned
            WHERE surface_m2 > 0
              AND surface_m2 <= ? {filtre_nature}
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
        title=f"Distribution des surfaces — {nature}",
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
    )

    figure.update_xaxes(range=[0, surface_max])

    figure.update_layout(
        paper_bgcolor="#FFFFFF",
        plot_bgcolor="#FFFFFF",
        font={"family": "Arial", "color": "#142D4E", "size": 13},
        title_font={"size": 20, "color": "#142D4E"},
        hoverlabel={
            "bgcolor": "#142D4E",
            "font_color": "#FFFFFF",
        },
        yaxis_title="Nombre d'équipements",
        bargap=0.05,
        template="plotly_white",
        annotations=[
            {
                "text": (
                    f"{nombre_total:,} surfaces valides | "
                    f"{nombre_hors_plage:,} hors de la plage affichée"
                ).replace(",", " "),
                "xref": "paper",
                "yref": "paper",
                "x": 0,
                "y": -0.25,
                "showarrow": False,
                "font": {"size": 12},
            }
        ],
        margin={"b": 110},
    )

    return figure
