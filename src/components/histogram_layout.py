"""Composant Dash interactif pour l'histogramme des surfaces."""

from dash import Input, Output, callback, dcc, html

from src.components.histogram import creer_histogramme


def creer_layout_histogramme() -> html.Div:
    """Construit le menu de filtrage et le graphique."""

    return html.Div(
        [
            html.H2("Répartition des surfaces sportives"),
            html.Label("Nature de l'équipement sportif :"),
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
            ),
            html.Label("Surface maximale affichée :"),
            dcc.Dropdown(
                id="filtre-surface",
                options=[
                    {"label": "Jusqu'à 10 800 m² (95 %)", "value": 10800},
                    {"label": "Jusqu'à 72 000 m² (99 %)", "value": 72000},
                ],
                value=10800,
                clearable=False,
            ),
            dcc.Graph(
                id="histogramme-surfaces",
                figure=creer_histogramme(),
            ),
        ]
    )


@callback(
    Output("histogramme-surfaces", "figure"),
    Input("filtre-nature", "value"),
    Input("filtre-surface", "value"),
)
def actualiser_histogramme(nature: str, surface_max: int):
    """Actualise le graphique selon les deux filtres."""
    return creer_histogramme(
        nature=nature,
        surface_max=surface_max,
    )
