"""Point d'entrée du dashboard SportÉgalité."""

from dash import Dash, html

app = Dash(__name__)

app.layout = html.Div(
    children=[
        html.H1("SportÉgalité"),
        html.H2("Projet Python 2 - Anella et Zelal"),
        html.P(
            "Les installations sportives sont-elles "
            "réparties équitablement entre les communes françaises ?"
        ),
        html.P("Notre dashboard est en cours de construction."),
    ]
)

if __name__ == "__main__":
    app.run(debug=True)