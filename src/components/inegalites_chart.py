"""Comparaison des communes selon les équipements et installations par habitant."""

import sqlite3
from contextlib import closing

import pandas as pd
import plotly.graph_objects as go

from config import DATABASE_PATH, TOUTE_LA_FRANCE

POPULATION_MINIMALE = 1000


def recuperer_details_communes(connexion, codes_communes: list[str]) -> dict:
    """Récupère les types d'équipements et les noms d'installations."""

    details = {}

    for code in codes_communes:
        # Les trois types d'équipements les plus fréquents.
        types = connexion.execute(
            """
            SELECT
                "Type d'équipement sportif",
                COUNT(DISTINCT "Numéro de l'équipement sportif")
            FROM cleaned
            WHERE code_commune = ?
              AND "Type d'équipement sportif" IS NOT NULL
            GROUP BY "Type d'équipement sportif"
            ORDER BY 2 DESC
            LIMIT 3
            """,
            (code,),
        ).fetchall()

        # Quelques noms d'installations de la commune.
        installations = connexion.execute(
            """
            SELECT nom_installation
            FROM cleaned_installations
            WHERE code_commune = ?
              AND nom_installation IS NOT NULL
            GROUP BY numero_installation
            ORDER BY nom_installation
            LIMIT 3
            """,
            (code,),
        ).fetchall()

        details[code] = {
            "types": "<br>".join(f"{nom} : {nombre}" for nom, nombre in types)
            or "Aucun type renseigné",
            "installations": "<br>".join(nom for (nom,) in installations)
            or "Aucune installation renseignée",
        }

    return details


def creer_graphique_inegalites(
    region: str | None = None,
    mode: str = "equipements",
) -> go.Figure:
    """Réunit les top 5 des équipements et installations pour 10 000 habitants."""

    # Conservé pour la compatibilité avec d'anciens appels.
    _ = mode

    filtre_region = ""
    parametres: list[int | str] = [POPULATION_MINIMALE]

    if region not in (None, TOUTE_LA_FRANCE):
        filtre_region = "AND p.nom_region = ?"
        parametres.append(region)

    requete = f"""
        WITH equipements AS (
            SELECT
                code_commune,
                COUNT(DISTINCT "Numéro de l'équipement sportif")
                    AS nombre_equipements
            FROM cleaned
            WHERE code_commune IS NOT NULL
            GROUP BY code_commune
        ),
        installations AS (
            SELECT
                code_commune,
                COUNT(DISTINCT numero_installation)
                    AS nombre_installations
            FROM cleaned_installations
            WHERE code_commune IS NOT NULL
            GROUP BY code_commune
        )
        SELECT
            p.code_commune AS code_insee,
            p.nom_commune AS commune,
            CAST(p.population AS INTEGER) AS population,
            COALESCE(e.nombre_equipements, 0) AS equipements,
            COALESCE(i.nombre_installations, 0) AS installations
        FROM cleaned_population AS p
        LEFT JOIN equipements AS e
            ON p.code_commune = e.code_commune
        LEFT JOIN installations AS i
            ON p.code_commune = i.code_commune
        WHERE CAST(p.population AS INTEGER) >= ?
          {filtre_region}
    """

    with closing(sqlite3.connect(DATABASE_PATH)) as connexion:
        donnees = pd.read_sql_query(
            requete,
            connexion,
            params=parametres,
        )

    figure = go.Figure()

    if not donnees.empty:
        # Calcul des deux ratios pour 10 000 habitants.
        donnees["ratio_equipements"] = (
            donnees["equipements"] / donnees["population"] * 10000
        )
        donnees["ratio_installations"] = (
            donnees["installations"] / donnees["population"] * 10000
        )

        # On écarte les communes sans infrastructure recensée.
        donnees = donnees[
            (donnees["equipements"] > 0) | (donnees["installations"] > 0)
        ].copy()

    if donnees.empty:
        figure.add_annotation(
            text="Aucune donnée disponible pour ce territoire.",
            x=0.5,
            y=0.5,
            xref="paper",
            yref="paper",
            showarrow=False,
        )
    else:
        # Les cinq meilleures communes pour les équipements.
        top_equipements = donnees.sort_values(
            ["ratio_equipements", "commune", "code_insee"],
            ascending=[False, True, True],
        ).head(5)

        # Les cinq meilleures communes pour les installations.
        top_installations = donnees.sort_values(
            ["ratio_installations", "commune", "code_insee"],
            ascending=[False, True, True],
        ).head(5)

        # Regroupement des deux tops, sans doublon.
        classement = pd.concat(
            [top_equipements, top_installations],
            ignore_index=True,
        ).drop_duplicates(subset="code_insee")

        # Classement selon le meilleur des deux ratios.
        classement = classement.copy()
        classement["ratio_max"] = classement[
            ["ratio_equipements", "ratio_installations"]
        ].max(axis=1)

        classement = classement.sort_values(
            ["ratio_max", "commune"],
            ascending=[True, False],
        )

        # Conserver des étiquettes uniques si deux communes ont le même nom.
        classement["etiquette"] = classement["commune"]
        doublons = classement["commune"].duplicated(keep=False)
        classement.loc[doublons, "etiquette"] = (
            classement.loc[doublons, "commune"]
            + " ("
            + classement.loc[doublons, "code_insee"]
            + ")"
        )

        # Récupérer les détails des communes du classement.
        codes = classement["code_insee"].tolist()

        with closing(sqlite3.connect(DATABASE_PATH)) as connexion:
            details = recuperer_details_communes(connexion, codes)

        # Informations spécifiques aux équipements.
        infos_equipements = [
            [
                ligne.code_insee,
                ligne.population,
                ligne.equipements,
                details[ligne.code_insee]["types"],
            ]
            for ligne in classement.itertuples()
        ]

        # Informations spécifiques aux installations.
        infos_installations = [
            [
                ligne.code_insee,
                ligne.population,
                ligne.installations,
                details[ligne.code_insee]["installations"],
            ]
            for ligne in classement.itertuples()
        ]

        # Première série : équipements.
        figure.add_trace(
            go.Bar(
                y=classement["etiquette"],
                x=classement["ratio_equipements"],
                name="Équipements",
                orientation="h",
                marker_color="#16A6A1",
                customdata=infos_equipements,
                hovertemplate=(
                    "<b>%{y}</b>"
                    "<br>Code INSEE : %{customdata[0]}"
                    "<br>Population : %{customdata[1]:,.0f} habitants"
                    "<br>Équipements : %{customdata[2]:,.0f}"
                    "<br><b>Équipements / 10 000 hab. : %{x:.2f}</b>"
                    "<br><br><b>Types d'équipements majoritaires :</b>"
                    "<br>%{customdata[3]}"
                    "<extra></extra>"
                ),
            )
        )

        # Deuxième série : installations.
        figure.add_trace(
            go.Bar(
                y=classement["etiquette"],
                x=classement["ratio_installations"],
                name="Installations",
                orientation="h",
                marker_color="#F0A35B",
                customdata=infos_installations,
                hovertemplate=(
                    "<b>%{y}</b>"
                    "<br>Code INSEE : %{customdata[0]}"
                    "<br>Population : %{customdata[1]:,.0f} habitants"
                    "<br>Installations : %{customdata[2]:,.0f}"
                    "<br><b>Installations / 10 000 hab. : %{x:.2f}</b>"
                    "<br><br><b>Exemples d'installations :</b>"
                    "<br>%{customdata[3]}"
                    "<extra></extra>"
                ),
            )
        )

    figure.update_layout(
        barmode="group",
        height=560,
        margin={"l": 15, "r": 15, "t": 45, "b": 65},
        paper_bgcolor="#FFFFFF",
        plot_bgcolor="#FFFFFF",
        font={
            "family": "Arial",
            "color": "#142D4E",
            "size": 12,
        },
        xaxis={
            "title": "Nombre pour 10 000 habitants",
            "gridcolor": "#E2EAF5",
            "rangemode": "tozero",
            "automargin": True,
        },
        yaxis={
            "title": None,
            "automargin": True,
        },
        legend={
            "orientation": "h",
            "yanchor": "bottom",
            "y": 1.02,
            "xanchor": "left",
            "x": 0,
        },
        hoverlabel={
            "bgcolor": "#142D4E",
            "font_color": "#FFFFFF",
            "font_size": 12,
            "align": "left",
        },
        bargap=0.25,
    )

    return figure
