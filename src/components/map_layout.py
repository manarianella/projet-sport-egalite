"""Composant Dash interactif pour la carte des installations sportives."""

import plotly.graph_objects as go
from dash import Dash, Input, Output, callback, dcc, html

from config import TOUTE_LA_FRANCE
from src.components.map_chart import (
    charger_installations,
    creer_carte,
    creer_carte_densite,
)


def lister_regions() -> list[str]:
    """Renvoie « Toute la France » suivi des régions triées."""
    regions = sorted(charger_installations()["region"].dropna().unique())
    return [TOUTE_LA_FRANCE, *regions]


def creer_filtre_region() -> html.Div:
    """Construit le filtre régional du dashboard."""
    return html.Div(
        [
            html.Label("Région"),
            dcc.Dropdown(
                id="filtre-region",
                options=lister_regions(),
                value=TOUTE_LA_FRANCE,
                clearable=False,
            ),
        ]
    )


def creer_graphique_carte() -> html.Div:
    """Construit uniquement la carte des installations."""
    return html.Div(
        [
            dcc.Graph(id="carte-installations"),
        ]
    )


def creer_layout_carte() -> html.Div:
    """Construit le menu des régions et la carte des installations."""
    return html.Div(
        [
            html.H2("Où se trouvent les installations sportives ?"),
            html.Label("Région :", htmlFor="filtre-region"),
            dcc.Dropdown(
                id="filtre-region",
                options=lister_regions(),
                value=TOUTE_LA_FRANCE,
                clearable=False,
            ),
            dcc.Graph(id="carte-installations"),
        ]
    )


@callback(
    Output("carte-installations", "figure"),
    Input("filtre-region", "value"),
)
def actualiser_carte(region: str) -> go.Figure:
    """Affiche la densité nationale, ou les installations de la région choisie."""
    installations = charger_installations()
    if region == TOUTE_LA_FRANCE:
        return creer_carte_densite(installations)
    installations_region = installations[installations["region"] == region]
    return creer_carte(installations_region)


if __name__ == "__main__":
    # Mini-application de test : affiche seulement la carte, sans toucher à main.py

    application_test = Dash(__name__)
    application_test.layout = creer_layout_carte()
    application_test.run(debug=False)
