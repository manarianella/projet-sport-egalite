"""Application principale du dashboard SportÉgalité."""

import sqlite3

from dash import Dash, html

from config import DATABASE_PATH
from src.components.histogram_layout import (
    creer_filtres_histogramme,
    creer_graphique_histogramme,
)
from src.components.map_layout import (
    creer_filtre_region,
    creer_graphique_carte,
)
from src.utils.prepare_database import preparer_base


def charger_statistiques() -> tuple[int, int, float]:
    """Charge les chiffres clés depuis SQLite."""
    with sqlite3.connect(DATABASE_PATH) as connexion:
        equipements = connexion.execute('SELECT COUNT(*) FROM "cleaned"').fetchone()[0]

        installations = connexion.execute(
            'SELECT COUNT(*) FROM "cleaned_installations"'
        ).fetchone()[0]

        rattaches = connexion.execute('SELECT COUNT(region) FROM "cleaned"').fetchone()[
            0
        ]

    pourcentage = 100 * rattaches / equipements if equipements else 0
    return equipements, installations, pourcentage


def creer_statistique(valeur: str, nom: str) -> html.Div:
    """Crée une carte de statistique."""
    return html.Div(
        [
            html.Div(valeur, className="valeur-statistique"),
            html.Div(nom, className="nom-statistique"),
        ],
        className="carte-statistique",
    )


preparer_base()

nombre_equipements, nombre_installations, taux = charger_statistiques()

app = Dash(__name__)
app.title = "SportÉgalité"

app.layout = html.Div(
    [
        # Menu latéral
        html.Aside(
            [
                html.Div("SportÉgalité", className="sidebar-logo"),
                html.Div("Filtres", className="sidebar-titre"),
                creer_filtre_region(),
                creer_filtres_histogramme(),
            ],
            className="sidebar",
        ),
        # Contenu principal
        html.Main(
            [
                html.Div(
                    [
                        html.H1("SportÉgalité"),
                        html.P("Accès aux installations sportives en France"),
                    ],
                    className="entete-dashboard",
                ),
                html.Div(
                    [
                        creer_statistique(
                            f"{nombre_equipements:,}".replace(",", " "),
                            "Équipements sportifs",
                        ),
                        creer_statistique(
                            f"{nombre_installations:,}".replace(",", " "),
                            "Installations sportives",
                        ),
                        creer_statistique(
                            f"{taux:.1f} %".replace(".", ","),
                            "Rattachés à une région",
                        ),
                    ],
                    className="grille-statistiques",
                ),
                html.Section(
                    [
                        html.H2("Carte des installations"),
                        creer_graphique_carte(),
                    ],
                    className="carte-graphique",
                ),
                html.Section(
                    [
                        html.H2("Répartition des surfaces"),
                        creer_graphique_histogramme(),
                    ],
                    className="carte-graphique",
                ),
            ],
            className="contenu-principal",
        ),
    ],
    className="dashboard",
)

if __name__ == "__main__":
    app.run(debug=False, port=8050)
