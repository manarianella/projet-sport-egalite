"""Composant Dash interactif pour l'histogramme des surfaces."""

from dash import Input, Output, callback, dcc, html
from plotly.graph_objects import Figure

from config import TOUTE_LA_FRANCE
from src.components.histogram import creer_histogramme


def creer_filtres_histogramme() -> html.Div:
    """Construit les filtres de nature et de surface."""
    return html.Div(
        [
            html.Label("Nature de l'équipement"),
            dcc.Dropdown(
                id="filtre-nature",
                options=[
                    {
                        "label": "Tous les équipements",
                        "value": "Tous",
                    },
                    {
                        "label": "Intérieur",
                        "value": "Intérieur",
                    },
                    {
                        "label": "Découvert",
                        "value": "Découvert",
                    },
                    {
                        "label": "Extérieur couvert",
                        "value": "Extérieur couvert",
                    },
                ],
                value="Tous",
                clearable=False,
            ),
        ]
    )


def creer_graphique_histogramme() -> html.Div:
    """Construit l'histogramme des surfaces."""
    return html.Div(
        [
            dcc.Graph(
                id="histogramme-surfaces",
                figure=creer_histogramme(),
                config={"displaylogo": False},
            )
        ]
    )


def creer_layout_histogramme() -> html.Div:
    """Construit une page autonome pour tester l'histogramme."""
    return html.Div(
        [
            html.H2("Répartition des surfaces sportives"),
            creer_filtres_histogramme(),
            creer_graphique_histogramme(),
        ]
    )


@callback(
    Output("histogramme-surfaces", "figure"),
    Input("filtre-nature", "value"),
    Input("filtre-region", "value"),
)
def actualiser_histogramme(
    nature: str,
    region: str | None,
) -> Figure:
    """Actualise l'histogramme avec une échelle de surfaces fixe."""

    region_selectionnee = None if region in (None, TOUTE_LA_FRANCE) else region

    return creer_histogramme(
        nature=nature,
        region=region_selectionnee,
    )
