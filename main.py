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


def creer_statistique(identifiant: str, nom: str) -> html.Div:
    """Crée une carte de statistique actualisable."""
    return html.Div(
        [
            html.Div(
                "—",
                id=identifiant,
                className="valeur-statistique",
            ),
            html.Div(
                nom,
                className="nom-statistique",
            ),
        ],
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
                            "La nature et la surface maximale "
                            "modifient uniquement l'histogramme "
                            "des surfaces, à gauche.",
                            className="sidebar-aide",
                        ),
                    ],
                    className="sidebar-section",
                ),
                html.Div(
                    [
                        html.Div(
                            "03 — COMPARAISON",
                            className="sidebar-section-titre",
                        ),
                        html.P(
                            "Sous la carte, choisissez Équipements "
                            "ou Installations dans le graphique "
                            "de droite pour comparer les communes.",
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
                        html.H1("SportÉgalité"),
                        html.H3(
                            "Toutes les communes françaises disposent-elles du "
                            "même accès aux installations sportives ?",
                            className="entete-problematique",
                        ),
                        html.P(
                            "Ce tableau de bord analyse la répartition des "
                            "installations et des équipements sportifs en France. "
                            "À travers une carte interactive, un histogramme des "
                            "surfaces et une comparaison entre communes, nous "
                            "cherchons à mettre en évidence les disparités "
                            "territoriales dans l'offre sportive.",
                            className="entete-introduction",
                        ),
                    ],
                    className="entete-dashboard",
                ),
                html.Div(
                    [
                        creer_statistique(
                            "stat-equipements",
                            "Équipements sportifs",
                        ),
                        creer_statistique(
                            "stat-installations",
                            "Installations sportives",
                        ),
                        creer_statistique(
                            "stat-communes",
                            "Communes représentées",
                        ),
                    ],
                    className="grille-statistiques",
                ),
                html.Section(
                    [
                        html.H2("Répartition géographique des installations sportives"),
                        html.P(
                            "Explorez la localisation et la "
                            "concentration des installations "
                            "selon la région sélectionnée.",
                            className="description-graphique",
                        ),
                        creer_graphique_carte(),
                    ],
                    className="carte-graphique",
                ),
                html.Div(
                    [
                        html.Section(
                            [
                                html.H2("Distribution des surfaces"),
                                html.Div(
                                    id="resume-filtres-surfaces",
                                    className="resume-filtres-surfaces",
                                ),
                                html.P(
                                    "Répartition des surfaces "
                                    "des équipements sportifs "
                                    "selon les filtres sélectionnés.",
                                    className="description-graphique",
                                ),
                                creer_graphique_histogramme(),
                            ],
                            className="carte-graphique",
                        ),
                        html.Section(
                            [
                                html.H2("Comparaison entre communes"),
                                html.P(
                                    "Découvrez les dix communes "
                                    "comptant le plus d'équipements "
                                    "ou d'installations sportives.",
                                    className="description-graphique",
                                ),
                                dcc.RadioItems(
                                    id="mode-inegalites",
                                    options=[
                                        {
                                            "label": "Équipements",
                                            "value": "equipements",
                                        },
                                        {
                                            "label": "Installations",
                                            "value": "installations",
                                        },
                                    ],
                                    value="equipements",
                                    inline=True,
                                    className="choix-analyse",
                                ),
                                dcc.Graph(
                                    id="graphique-inegalites",
                                    config={"displaylogo": False},
                                ),
                            ],
                            className="carte-graphique",
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
    Input("filtre-region", "value"),
)
def actualiser_statistiques(
    region: str | None,
) -> tuple[str, str, str]:
    """Actualise les chiffres clés du territoire."""

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

    return (
        f"{nb_equipements:,}".replace(",", " "),
        f"{nb_installations:,}".replace(",", " "),
        f"{nb_communes:,}".replace(",", " "),
    )


@callback(
    Output("graphique-inegalites", "figure"),
    Input("filtre-region", "value"),
    Input("mode-inegalites", "value"),
)
def actualiser_inegalites(
    region: str | None,
    mode: str,
) -> Figure:
    """Actualise la comparaison des communes."""
    return creer_graphique_inegalites(
        region=region,
        mode=mode,
    )


@callback(
    Output("resume-filtres-surfaces", "children"),
    Input("filtre-region", "value"),
    Input("filtre-nature", "value"),
    Input("filtre-surface", "value"),
)
def afficher_filtres_surfaces(
    region: str | None,
    nature: str,
    surface_max: int,
) -> list:
    """Affiche les filtres actifs sous le titre de l'histogramme."""

    nom_region = "Toute la France" if region in (None, TOUTE_LA_FRANCE) else region

    nom_nature = "Tous les équipements" if nature == "Tous" else nature

    return [
        html.Span(nom_region, className="filtre-indicateur"),
        html.Span(nom_nature, className="filtre-indicateur"),
        html.Span(
            f"Jusqu'à {surface_max:,.0f} m²".replace(",", " "),
            className="filtre-indicateur",
        ),
    ]


if __name__ == "__main__":
    app.run(debug=False, port=8050)
