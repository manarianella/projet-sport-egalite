"""Comparaison des équipements et installations entre communes."""

import sqlite3
from contextlib import closing

import pandas as pd
import plotly.express as px
import plotly.graph_objects as go


from config import DATABASE_PATH, TOUTE_LA_FRANCE


def creer_graphique_inegalites(
    region: str | None = None,
    mode: str = "equipements",
) -> go.Figure:
    """Affiche les dix communes les plus équipées ou les plus dotées en installations."""

    parametres: list[str] = []
    filtre_region = ""

    if region not in (None, TOUTE_LA_FRANCE):
        filtre_region = " AND region = ?"
        parametres.append(region)

    if mode == "installations":
        requete = f"""
            SELECT
                code_commune AS code_insee,
                MAX(nom_commune) AS commune,
                COUNT(DISTINCT numero_installation) AS nombre
            FROM cleaned_installations
            WHERE code_commune IS NOT NULL
              AND TRIM(code_commune) != ''
              AND numero_installation IS NOT NULL
              {filtre_region}
            GROUP BY code_commune
            ORDER BY nombre DESC, commune ASC
            LIMIT 10
        """

        libelle = "Nombre d'installations sportives"
        couleur = "#F0A35B"

    else:
        requete = f"""
            SELECT
                code_commune AS code_insee,
                MAX(nom_commune) AS commune,
                COUNT(DISTINCT "Numéro de l'équipement sportif") AS nombre
            FROM cleaned
            WHERE code_commune IS NOT NULL
              AND TRIM(code_commune) != ''
              {filtre_region}
            GROUP BY code_commune
            ORDER BY nombre DESC, commune ASC
            LIMIT 10
        """

        libelle = "Nombre d'équipements sportifs"
        couleur = "#16A6A1"

    with closing(sqlite3.connect(DATABASE_PATH)) as connexion:
        donnees = pd.read_sql_query(
            requete,
            connexion,
            params=parametres,
        )

    if donnees.empty:
        figure = go.Figure()
        figure.add_annotation(
            text="Aucune donnée disponible pour cette région.",
            x=0.5,
            y=0.5,
            xref="paper",
            yref="paper",
            showarrow=False,
            font={"size": 14, "color": "#61748F"},
        )
    else:
        donnees = donnees.sort_values(
            ["nombre", "commune"],
            ascending=[True, False],
        )

        figure = px.bar(
            donnees,
            x="nombre",
            y="commune",
            orientation="h",
            labels={
                "nombre": libelle,
                "commune": "Commune",
            },
            custom_data=["code_insee"],
        )

        figure.update_traces(
            marker_color=couleur,
            hovertemplate=(
                "<b>%{y}</b>"
                "<br>Code INSEE : %{customdata[0]}"
                "<br>Nombre : %{x:,.0f}"
                "<extra></extra>"
            ),
        )

        figure.update_yaxes(
            title=None,
            automargin=True,
        )

    figure.update_layout(
        height=510,
        margin={"l": 15, "r": 15, "t": 20, "b": 65},
        paper_bgcolor="#FFFFFF",
        plot_bgcolor="#FFFFFF",
        font={
            "family": "Arial",
            "color": "#142D4E",
            "size": 12,
        },
        showlegend=False,
        bargap=0.28,
        xaxis={
            "title": libelle,
            "gridcolor": "#E2EAF5",
            "automargin": True,
        },
    )

    return figure
