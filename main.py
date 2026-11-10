"""Application principale du dashboard SportÉgalité."""

import sqlite3

from dash import Dash, Input, Output, callback, dcc, html
from plotly.graph_objects import Figure

from config import DATABASE_PATH, TOUTE_LA_FRANCE
from src.components.histogram_layout import (
    creer_filtres_histogramme,
    creer_graphique_histogramme,
)
from src.components.inegalites_chart import creer_graphique_inegalites
from src.components.map_layout import (
    creer_filtre_region,
    creer_graphique_carte,
)
from src.utils.prepare_database import preparer_base


def creer_statistique(
    identifiant: str,
    nom: str,
    explication: str,
    identifiant_ratio: str | None = None,
) -> html.Div:
    """Crée une carte statistique avec une aide au survol."""

    contenu: list[html.Div | html.Span] = [
        html.Div(
            "—",
            id=identifiant,
            className="valeur-statistique",
        ),
        html.Div(
            nom,
            className="nom-statistique",
        ),
    ]

    if identifiant_ratio is not None:
        contenu.append(
            html.Div(
                "— pour 10 000 habitants",
                id=identifiant_ratio,
                className="ratio-statistique",
            )
        )

    contenu.extend(
        [
            html.Span(
                "ⓘ",
                className="stat-info-icon",
                tabIndex=0,
                role="img",
                title="Informations sur cette statistique",
            ),
            html.Div(
                explication,
                className="stat-tooltip",
            ),
        ]
    )

    return html.Div(
        contenu,
        className="carte-statistique",
    )


preparer_base()

app = Dash(__name__)
app.title = "SportÉgalité"

app.layout = html.Div(
    [
        html.Aside(
            [
                html.Div(
                    "SportÉgalité",
                    className="sidebar-logo",
                ),
                html.P(
                    "Analyse des inégalités sportives",
                    className="sidebar-titre",
                ),
                html.Div(
                    [
                        html.Div(
                            "01 — TERRITOIRE",
                            className="sidebar-section-titre",
                        ),
                        creer_filtre_region(),
                        html.P(
                            "La région sélectionnée actualise les "
                            "statistiques, la carte, l'histogramme "
                            "et les classements des communes.",
                            className="sidebar-aide",
                        ),
                    ],
                    className="sidebar-section",
                ),
                html.Div(
                    [
                        html.Div(
                            "02 — SURFACES SPORTIVES",
                            className="sidebar-section-titre",
                        ),
                        creer_filtres_histogramme(),
                        html.P(
                            "La nature de l'équipement permet de filtrer "
                            "l'histogramme des surfaces. Les échelles restent "
                            "fixes pour faciliter les comparaisons entre régions.",
                            className="sidebar-aide",
                        ),
                    ],
                    className="sidebar-section",
                ),
            ],
            className="sidebar",
        ),
        html.Main(
            [
                html.Div(
                    [
                        html.P(
                            "ÉTUDE TERRITORIALE • FRANCE",
                            className="entete-categorie",
                        ),
                        html.H3(
                            "Toutes les communes françaises disposent-elles "
                            "du même accès aux installations sportives ?",
                            className="entete-problematique",
                        ),
                        html.P(
                            "Ce dashboard explore la répartition des installations et des équipements sportifs en France. "
                            "Il permet d’observer les écarts entre territoires, "
                            "d’analyser les surfaces sportives et de comparer les communes"
                            " en tenant compte de leur population.",
                            className="entete-introduction",
                        ),
                        html.Div(
                            [
                                html.A(
                                    "01 — Explorer le territoire",
                                    href="#section-territoire",
                                    className="hero-badge hero-link",
                                ),
                                html.A(
                                    "02 — Analyser les surfaces",
                                    href="#section-surfaces",
                                    className="hero-badge hero-link",
                                ),
                                html.A(
                                    "03 — Comparer les communes",
                                    href="#section-comparaison",
                                    className="hero-badge hero-link",
                                ),
                            ],
                            className="hero-badges",
                        ),
                    ],
                    className="entete-dashboard",
                ),
                html.Div(
                    [
                        creer_statistique(
                            "stat-equipements",
                            "Équipements sportifs",
                            "Un équipement est un espace de pratique sportive, "
                            "comme un terrain de football, une piscine ou un court "
                            "de tennis. Une installation peut contenir plusieurs "
                            "équipements.",
                            "stat-ratio-equipements",
                        ),
                        creer_statistique(
                            "stat-installations",
                            "Installations sportives",
                            "Une installation est un lieu regroupant un ou plusieurs "
                            "équipements sportifs. Par exemple, un complexe sportif "
                            "peut contenir un gymnase et plusieurs terrains.",
                            "stat-ratio-installations",
                        ),
                        creer_statistique(
                            "stat-communes",
                            "Communes représentées",
                            "Nombre de communes distinctes disposant d'au moins "
                            "un équipement recensé dans le territoire sélectionné. "
                            "Cela ne correspond pas forcément à toutes les communes "
                            "du territoire.",
                        ),
                    ],
                    className="grille-statistiques",
                ),
                html.Section(
                    [
                        html.P("01 — TERRITOIRE", className="bloc-section-label"),
                        html.H2(
                            " Répartition géographique des installations sportives",
                        ),
                        html.P("CARTE INTERACTIVE", className="type-visualisation"),
                        creer_graphique_carte(),
                    ],
                    id="section-territoire",
                    className="carte-graphique section-principale",
                ),
                html.Div(
                    [
                        html.Section(
                            [
                                html.P(
                                    "02 - SURFACES SPORTIVES",
                                    className="bloc-section-label",
                                ),
                                html.H2(
                                    " Distribution des surfaces sportives",
                                ),
                                html.Div(
                                    id="resume-filtres-surfaces",
                                    className="resume-filtres-surfaces",
                                ),
                                html.P("HISTOGRAMME", className="type-visualisation"),
                                creer_graphique_histogramme(),
                            ],
                            id="section-surfaces",
                            className="carte-graphique section-secondaire",
                        ),
                        html.Section(
                            [
                                html.P(
                                    "03 — COMPARAISON", className="bloc-section-label"
                                ),
                                html.H2(
                                    " Comparaison entre communes",
                                ),
                                html.P(
                                    "DIAGRAMME EN BARRES",
                                    className="type-visualisation",
                                ),
                                dcc.Graph(
                                    id="graphique-inegalites",
                                    config={"displaylogo": False},
                                ),
                            ],
                            id="section-comparaison",
                            className="carte-graphique section-comparaison",
                        ),
                    ],
                    className="grille-analyses",
                ),
            ],
            className="contenu-principal",
        ),
    ],
    className="dashboard",
)


@callback(
    Output("stat-equipements", "children"),
    Output("stat-installations", "children"),
    Output("stat-communes", "children"),
    Output("stat-ratio-equipements", "children"),
    Output("stat-ratio-installations", "children"),
    Input("filtre-region", "value"),
)
def actualiser_statistiques(
    region: str | None,
) -> tuple[str, str, str, str, str]:
    """Actualise les statistiques et les ratios par habitant."""

    toutes_regions = region in (None, TOUTE_LA_FRANCE)

    with sqlite3.connect(DATABASE_PATH) as connexion:
        if toutes_regions:
            nb_equipements = connexion.execute(
                'SELECT COUNT(*) FROM "cleaned"'
            ).fetchone()[0]

            nb_installations = connexion.execute(
                'SELECT COUNT(*) FROM "cleaned_installations"'
            ).fetchone()[0]

            nb_communes = connexion.execute(
                'SELECT COUNT(DISTINCT code_commune) FROM "cleaned"'
            ).fetchone()[0]

            population = connexion.execute(
                """
                SELECT SUM(CAST(population AS INTEGER))
                FROM cleaned_population
                WHERE population IS NOT NULL
                """
            ).fetchone()[0]

        else:
            nb_equipements = connexion.execute(
                'SELECT COUNT(*) FROM "cleaned" WHERE region = ?',
                (region,),
            ).fetchone()[0]

            nb_installations = connexion.execute(
                """
                SELECT COUNT(*)
                FROM cleaned_installations
                WHERE region = ?
                """,
                (region,),
            ).fetchone()[0]

            nb_communes = connexion.execute(
                """
                SELECT COUNT(DISTINCT code_commune)
                FROM cleaned
                WHERE region = ?
                """,
                (region,),
            ).fetchone()[0]

            population = connexion.execute(
                """
                SELECT SUM(CAST(population AS INTEGER))
                FROM cleaned_population
                WHERE nom_region = ?
                """,
                (region,),
            ).fetchone()[0]

    def formater_nombre(nombre: int) -> str:
        return f"{nombre:,}".replace(",", " ")

    def formater_ratio(nombre: int, habitants: int | None) -> str:
        if not habitants or habitants <= 0:
            return "Population indisponible"

        ratio = nombre / habitants * 10000
        valeur = f"{ratio:,.1f}"
        valeur = valeur.replace(",", " ").replace(".", ",")

        return f"{valeur} pour 10 000 habitants"

    return (
        formater_nombre(nb_equipements),
        formater_nombre(nb_installations),
        formater_nombre(nb_communes),
        formater_ratio(nb_equipements, population),
        formater_ratio(nb_installations, population),
    )


@callback(
    Output("graphique-inegalites", "figure"),
    Input("filtre-region", "value"),
)
def actualiser_inegalites(region: str | None) -> Figure:
    """Actualise la comparaison selon la région sélectionnée."""
    return creer_graphique_inegalites(region=region)


@callback(
    Output("resume-filtres-surfaces", "children"),
    Input("filtre-region", "value"),
    Input("filtre-nature", "value"),
)
def afficher_filtres_surfaces(
    region: str | None,
    nature: str,
) -> list:
    """Affiche les filtres actifs de l'histogramme."""

    nom_region = "Toute la France" if region in (None, TOUTE_LA_FRANCE) else region

    nom_nature = "Tous les équipements" if nature == "Tous" else nature

    return [
        html.Span(nom_region, className="filtre-indicateur"),
        html.Span(nom_nature, className="filtre-indicateur"),
        html.Span(
            "Surfaces : 0 à 10 800 m²",
            className="filtre-indicateur",
        ),
    ]


if __name__ == "__main__":
    app.run(debug=False, port=8050)
