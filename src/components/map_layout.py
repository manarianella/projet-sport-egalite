"""Composant Dash interactif pour la carte des installations sportives."""
import pandas as pd
import plotly.graph_objects as go
from dash import Dash, Input, Output, callback, ctx, dcc, html

from config import TOUTE_LA_FRANCE
from src.components.map_chart import (
    CENTRE_FRANCE,
    ZOOM_FRANCE,
    ZOOM_REGION,
    choisir_niveau,
    creer_carte_bulles,
    filtrer_vue,
    preparer_niveaux,
)


def lister_regions() -> list[str]:
    """Renvoie « Toute la France » suivi des régions triées."""
    regions = sorted(preparer_niveaux()["region"]["region"].dropna().unique())
    return [TOUTE_LA_FRANCE, *regions]


def creer_filtre_region() -> html.Div:
    """Construit le filtre régional du dashboard."""
    return html.Div(
        [
            html.Label("Région - installations et équipements"),
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


def vue_initiale(region: str) -> tuple[dict[str, float], float]:
    """Renvoie le centre et le zoom de départ pour la région choisie."""
    if region == TOUTE_LA_FRANCE:
        return CENTRE_FRANCE, ZOOM_FRANCE
    regions = preparer_niveaux()["region"]
    ligne = regions[regions["region"] == region].iloc[0]
    return {"lat": ligne["latitude"], "lon": ligne["longitude"]}, ZOOM_REGION


def vue_actuelle(
    relayout: dict | None, centre: dict[str, float], zoom: float
) -> tuple[dict[str, float], float]:
    """Lit le centre et le zoom après un déplacement de l'utilisateur."""
    if not relayout:
        return centre, zoom
    return relayout.get("map.center", centre), relayout.get("map.zoom", zoom)


def bulles_a_afficher(
    region: str, centre: dict[str, float], zoom: float
) -> pd.DataFrame:
    """France : régions, départements ou communes selon le zoom. Région : ses communes."""
    niveaux = preparer_niveaux()
    if region != TOUTE_LA_FRANCE:
        communes = niveaux["commune"]
        return filtrer_vue(communes[communes["nom_region"] == region], centre, zoom)

    niveau = choisir_niveau(zoom)
    if niveau == "commune":
        return filtrer_vue(niveaux["commune"], centre, zoom)
    return niveaux[niveau]


def echelle_couleurs(bulles: pd.DataFrame) -> tuple[float, float]:
    """Fixe l'échelle de couleurs sur les valeurs courantes (5e au 95e centile)."""
    ratios = bulles["pour_10000"].dropna()
    if ratios.empty:
        return 0.0, 1.0
    return float(ratios.quantile(0.05)), float(ratios.quantile(0.95))


def construire_carte(
    region: str, relayout: dict | None, declencheur: str | None
) -> go.Figure:
    """Calcule la vue (région et zoom), puis dessine les bulles correspondantes."""
    centre, zoom = vue_initiale(region)
    # Après un changement de région, on repart de la vue de départ de cette région
    if declencheur == "carte-installations":
        centre, zoom = vue_actuelle(relayout, centre, zoom)

    bulles = bulles_a_afficher(region, centre, zoom)
    return creer_carte_bulles(
        bulles, centre, zoom, cle_vue=region, echelle=echelle_couleurs(bulles)
    )


@callback(
    Output("carte-installations", "figure"),
    Input("filtre-region", "value"),
    Input("carte-installations", "relayoutData"),
)
def actualiser_carte(region: str, relayout: dict | None) -> go.Figure:
    """Redessine la carte quand la région ou le zoom change."""
    return construire_carte(region, relayout, ctx.triggered_id)


if __name__ == "__main__":
    # Mini-application de test : affiche seulement la carte, sans toucher à main.py

    application_test = Dash(__name__)
    application_test.layout = creer_layout_carte()
    application_test.run(debug=False)
