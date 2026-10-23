"""Application principale du dashboard SportÉgalité."""

from dash import Dash, html

from src.components.histogram_layout import creer_layout_histogramme
from src.components.map_layout import creer_layout_carte

# Création de l'application Dash
app = Dash(__name__)
app.title = "SportÉgalité"

STYLE_PAGE = {
    "maxWidth": "1200px",
    "margin": "0 auto",
    "padding": "30px",
    "fontFamily": "Arial, sans-serif",
    "backgroundColor": "#FFFFFF",
    "color": "#142D4E",
}

STYLE_ENTETE = {
    "backgroundColor": "#142D4E",
    "color": "#FFFFFF",
    "padding": "30px",
    "borderRadius": "12px",
    "marginBottom": "25px",
}

# Construction de la page principale
app.layout = html.Div(
    [
        # Présentation du projet
        html.Div(
            [
                html.H1(
                    "SportÉgalité",
                    style={"marginTop": "0"},
                ),
                html.P(
                    "Toutes les communes françaises disposent-elles "
                    "du même accès aux installations sportives ?",
                    style={"fontSize": "17px"},
                ),
                html.P(
                    "Explorez la répartition géographique des installations "
                    "et les surfaces des équipements sportifs en France."
                ),
            ],
            style=STYLE_ENTETE,
        ),
        # Carte interactive développée par Zelal
        html.Div(
            creer_layout_carte(),
            style={"marginBottom": "35px"},
        ),
        # Histogramme interactif développé par Anella
        html.Div(
            creer_layout_histogramme(),
            style={"marginBottom": "35px"},
        ),
        # Informations sur l'analyse
        html.Div(
            [
                html.H3("Comprendre les résultats"),
                html.P(
                    "La carte permet d'observer où se trouvent les "
                    "installations sportives. L'histogramme montre comment "
                    "se répartissent les surfaces des équipements. "
                    "Ces deux visualisations permettent de comparer "
                    "plusieurs caractéristiques du territoire français."
                ),
                html.P(
                    "La présence d'une installation ne garantit pas "
                    "nécessairement son accessibilité à tous les habitants."
                ),
            ],
            style={
                "backgroundColor": "#F4F8FC",
                "padding": "20px",
                "borderRadius": "12px",
            },
        ),
    ],
    style=STYLE_PAGE,
)

if __name__ == "__main__":
    app.run(debug=False, port=8050)
