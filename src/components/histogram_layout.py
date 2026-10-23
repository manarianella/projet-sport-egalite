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
            dcc.Graph(
                id="histogramme-surfaces",
                figure=creer_histogramme(),
            ),
        ]
    )


@callback(
    Output("histogramme-surfaces", "figure"),
    Input("filtre-nature", "value"),
)
def actualiser_histogramme(nature: str):
    """Actualise le graphique selon la catégorie sélectionnée."""
    return creer_histogramme(nature=nature)
