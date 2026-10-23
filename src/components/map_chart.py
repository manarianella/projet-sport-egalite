import sqlite3
from contextlib import closing

import pandas as pd
import plotly.express as px
import plotly.graph_objects as go

from config import DATABASE_PATH


def charger_installations() -> pd.DataFrame:
    """Charge les installations nettoyées utiles à la carte."""
    requete = """
        SELECT nom_installation, commune, departement, region,
               type_territoire, latitude, longitude
        FROM cleaned_installations
    """
    with closing(sqlite3.connect(DATABASE_PATH)) as connexion:
        return pd.read_sql_query(requete, connexion)


def creer_carte(installations: pd.DataFrame) -> go.Figure:
    """Crée une carte où chaque point est une installation sportive."""
    figure = px.scatter_map(
        installations,
        lat="latitude",
        lon="longitude",
        hover_name="nom_installation",
        hover_data={
            "commune": True,
            "departement": True,
            "latitude": False,
            "longitude": False,
        },
        center={
            "lat": installations["latitude"].mean(),
            "lon": installations["longitude"].mean(),
        },
        zoom=6,
        title="Installations sportives de la région",
        map_style="carto-positron",
    )
    figure.update_traces(marker={"size": 4, "opacity": 0.6})
    figure.update_layout(margin={"l": 0, "r": 0, "t": 40, "b": 0})
    return figure


if __name__ == "__main__":
    installations = charger_installations()
    # Test sur un échantillon : 144 000 points ralentiraient le navigateur
    echantillon = installations.sample(n=5000, random_state=0)
    figure = creer_carte(echantillon)
    figure.write_html("carte_test.html")
    print("Carte enregistrée dans carte_test.html")
