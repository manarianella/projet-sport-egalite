"""Composant Dash interactif pour l'histogramme des surfaces."""

from dash import Input, Output, callback, dcc, html
from plotly.graph_objects import Figure

from src.components.histogram import creer_histogramme
from config import TOUTE_LA_FRANCE


STYLE_FILTRES = {
    "backgroundColor": "#F4F8FC",
    "border": "1px solid #DCE6EF",
    "borderRadius": "12px",
    "padding": "20px",
    "marginBottom": "20px",
}

STYLE_LABEL = {
    "color": "#142D4E",
    "fontWeight": "600",
    "marginBottom": "8px",
    "display": "block",
}

STYLE_CONTENEUR = {
    "maxWidth": "1100px",
    "margin": "30px auto",
    "padding": "20px",
    "fontFamily": "Arial, sans-serif",
}


def creer_filtres_histogramme() -> html.Div:
    """Construit les filtres de nature et de surface."""
    return html.Div(
        [
            html.Label("Nature de l'équipement"),
            dcc.Dropdown(
                id="filtre-nature",
                options=[
                    {"label": "Tous les équipements", "value": "Tous"},
                    {"label": "Intérieur", "value": "Intérieur"},
                    {"label": "Découvert", "value": "Découvert"},
                    {"label": "Extérieur couvert", "value": "Extérieur couvert"},
                ],
                value="Tous",
                clearable=False,
            ),
            html.Label("Surface maximale"),
            dcc.Dropdown(
                id="filtre-surface",
                options=[
                    {"label": "10 800 m² — 95e percentile", "value": 10800},
                    {"label": "72 000 m² — 99e percentile", "value": 72000},
                ],
                value=10800,
                clearable=False,
            ),
        ]
    )


def creer_graphique_histogramme() -> html.Div:
    """Construit uniquement le graphique des surfaces."""
    return html.Div(
        [
            dcc.Graph(
                id="histogramme-surfaces",
                figure=creer_histogramme(),
            ),
        ]
    )


def creer_layout_histogramme() -> html.Div:
    """Construit les filtres et l'histogramme interactif."""

    return html.Div(
        [
            html.H2(
                "Répartition des surfaces sportives",
                style={"color": "#142D4E"},
            ),
            html.Div(
                [
                    html.Label(
                        "Nature de l'équipement sportif :",
                        style=STYLE_LABEL,
                    ),
                    dcc.Dropdown(
                        id="filtre-nature",
                        options=[
                            {"label": "Tous les équipements", "value": "Tous"},
                            {"label": "Intérieur", "value": "Intérieur"},
                            {"label": "Découvert", "value": "Découvert"},
                            {
                                "label": "Extérieur couvert",
                                "value": "Extérieur couvert",
                            },
                        ],
                        value="Tous",
                        clearable=False,
                        style={"marginBottom": "16px"},
                    ),
                    html.Label(
                        "Surface maximale affichée :",
                        style=STYLE_LABEL,
                    ),
                    dcc.Dropdown(
                        id="filtre-surface",
                        options=[
                            {
                                "label": "Jusqu'à 10 800 m² (95e percentile)",
                                "value": 10800,
                            },
                            {
                                "label": "Jusqu'à 72 000 m² (99e percentile)",
                                "value": 72000,
                            },
                        ],
                        value=10800,
                        clearable=False,
                    ),
                    html.P(
                        "Le choix 95 % affiche les surfaces jusqu'à 10 800 m². "
                        "Le choix 99 % élargit l'affichage jusqu'à 72 000 m². "
                        "Ces seuils correspondent approximativement aux 95e et "
                        "99e percentiles calculés sur l'ensemble des équipements. "
                        "Les surfaces plus grandes restent dans la base de données.",
                        style={
                            "fontSize": "13px",
                            "color": "#60738A",
                            "marginTop": "12px",
                        },
                    ),
                ],
                style=STYLE_FILTRES,
            ),
            html.Div(
                [
                    html.H4("Comment lire cet histogramme ?"),
                    html.P(
                        "Chaque barre représente un intervalle de surfaces en m². "
                        "La hauteur indique combien d'équipements sportifs "
                        "possèdent une surface dans cet intervalle. "
                        "Plus la barre est haute, plus ces équipements sont nombreux."
                    ),
                ],
                style={
                    "backgroundColor": "#EAF4F8",
                    "padding": "16px",
                    "borderRadius": "10px",
                    "color": "#142D4E",
                    "marginBottom": "16px",
                },
            ),
            dcc.Graph(
                id="histogramme-surfaces",
                figure=creer_histogramme(),
            ),
        ],
        style=STYLE_CONTENEUR,
    )


@callback(
    Output("histogramme-surfaces", "figure"),
    Input("filtre-nature", "value"),
    Input("filtre-surface", "value"),
    Input("filtre-region", "value"),
)
def actualiser_histogramme(nature: str, surface_max: int, region: str) -> Figure:
    """Actualise l'histogramme selon les filtres sélectionnés."""
    return creer_histogramme(
        nature=nature,
        region=None if region == TOUTE_LA_FRANCE else region,
        surface_max=surface_max,
    )
