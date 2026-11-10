"""Histogramme des surfaces des équipements sportifs."""

import sqlite3
from contextlib import closing
from functools import lru_cache

import numpy as np
import pandas as pd
import plotly.graph_objects as go
from plotly.graph_objects import Figure

from config import DATABASE_PATH

COULEURS_NATURE = {
    "Tous": "#4387D2",
    "Intérieur": "#16A6A1",
    "Découvert": "#4387D2",
    "Extérieur couvert": "#F0A35B",
}

SURFACE_MAX_FIXE = 10800


@lru_cache(maxsize=4)
def calculer_maximum_y(surface_max: float) -> int:
    """Calcule une échelle Y fixe à partir des données nationales."""

    with closing(sqlite3.connect(DATABASE_PATH)) as connexion:
        donnees = pd.read_sql_query(
            """
            SELECT surface_m2
            FROM cleaned
            WHERE surface_m2 > 0
              AND surface_m2 <= ?
            """,
            connexion,
            params=[surface_max],
        )

    effectifs, _ = np.histogram(
        donnees["surface_m2"],
        bins=50,
        range=(0, surface_max),
    )

    return max(1, int(effectifs.max() * 1.10) + 1)


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
    surface_max: float = SURFACE_MAX_FIXE,
) -> Figure:
    """Crée un histogramme avec des informations détaillées au survol."""

    filtres, parametres = construire_filtres(nature, region)

    with closing(sqlite3.connect(DATABASE_PATH)) as connexion:
        # Récupérer les surfaces et les types d'équipements.
        requete = f"""
            SELECT
                surface_m2,
                "Type d'équipement sportif" AS type_equipement
            FROM cleaned
            WHERE surface_m2 > 0
              AND surface_m2 <= ?
              {filtres}
        """

        donnees = pd.read_sql_query(
            requete,
            connexion,
            params=[surface_max, *parametres],
        )

        # Récupérer la population du territoire sélectionné.
        if region is None:
            population = connexion.execute(
                """
                SELECT SUM(CAST(population AS INTEGER))
                FROM cleaned_population
                """
            ).fetchone()[0]
        else:
            population = connexion.execute(
                """
                SELECT SUM(CAST(population AS INTEGER))
                FROM cleaned_population
                WHERE nom_region = ?
                """,
                (region,),
            ).fetchone()[0]

    # Créer 50 intervalles identiques.
    nombre_intervalles = 50
    largeur = surface_max / nombre_intervalles

    effectifs, bornes = np.histogram(
        donnees["surface_m2"],
        bins=nombre_intervalles,
        range=(0, surface_max),
    )

    # Associer chaque équipement à son intervalle.
    donnees["intervalle"] = (
        np.searchsorted(
            bornes,
            donnees["surface_m2"],
            side="right",
        )
        - 1
    )

    donnees["intervalle"] = donnees["intervalle"].clip(0, nombre_intervalles - 1)

    # Préparer les informations affichées au survol.
    informations = []

    nom_region = region if region is not None else "Toute la France"

    for i in range(nombre_intervalles):
        minimum = bornes[i]
        maximum = bornes[i + 1]
        nombre = int(effectifs[i])

        groupe = donnees[donnees["intervalle"] == i]

        types = groupe["type_equipement"].fillna("Non renseigné").value_counts().head(3)

        if types.empty:
            types_texte = "Aucun équipement"
        else:
            types_texte = "<br>".join(
                f"{rang}. {nom} : {effectif:,}".replace(",", " ")
                for rang, (nom, effectif) in enumerate(types.items(), start=1)
            )

        if population is not None and population > 0:
            ratio = nombre / population * 10000
            population_texte = f"{population:,}".replace(",", " ")
            ratio_texte = f"{ratio:.2f}".replace(".", ",")
        else:
            population_texte = "Non disponible"
            ratio_texte = "Non disponible"

        informations.append(
            [
                f"{minimum:,.0f}".replace(",", " "),
                f"{maximum:,.0f}".replace(",", " "),
                nom_region,
                types_texte,
                population_texte,
                ratio_texte,
            ]
        )

    # Dessiner les barres à partir des effectifs calculés.
    figure = go.Figure()

    figure.add_trace(
        go.Bar(
            x=(bornes[:-1] + bornes[1:]) / 2,
            y=effectifs,
            width=largeur * 0.95,
            customdata=informations,
            marker_color=COULEURS_NATURE.get(nature, "#4387D2"),
            marker_line_color="#FFFFFF",
            marker_line_width=0.5,
            opacity=0.9,
            hovertemplate=(
                "<b>Surface : %{customdata[0]} à "
                "%{customdata[1]} m²</b>"
                "<br>Territoire : %{customdata[2]}"
                "<br>Nombre d'équipements : %{y:,.0f}"
                "<br><br><b>Types majoritaires :</b>"
                "<br>%{customdata[3]}"
                "<br><br>Population : %{customdata[4]} habitants"
                "<br><b>Équipements / 10 000 hab. : "
                "%{customdata[5]}</b>"
                "<extra></extra>"
            ),
        )
    )

    # Axe horizontal : identique pour tous les territoires.
    figure.update_xaxes(
        title_text="Surface de l'aire de pratique (m²)",
        range=[0, surface_max],
        fixedrange=True,
    )

    # Axe vertical : fixe entre les régions.
    if region is None:
        figure.update_yaxes(
            title_text="Nombre d'équipements",
            range=[0, calculer_maximum_y(surface_max)],
            fixedrange=True,
        )
    else:
        figure.update_yaxes(
            title_text="Nombre d'équipements",
            range=[0, 7500],
            dtick=1500,
            fixedrange=True,
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
            "font_size": 12,
            "align": "left",
        },
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
