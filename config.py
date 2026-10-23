"""Configuration du projet SportÉgalité."""

from pathlib import Path

# Dossier principal du projet
BASE_DIR = Path(__file__).resolve().parent

# Dossier de stockage des données
DATA_DIR = BASE_DIR / "data"
RAW_DIR = DATA_DIR / "raw"

# Chemin de la future base SQLite
DATABASE_PATH = DATA_DIR / "db.sqlite"

# Adresse officielle des équipements sportifs
EQUIPEMENTS_URL = (
    "https://data.sports.gouv.fr/api/explore/v2.1/"
    "catalog/datasets/equipements-sportifs/exports/csv"
    "?lang=fr&timezone=Europe%2FBerlin"
    "&use_labels=true&delimiter=%3B"
)

# Fichier dans lequel les données seront téléchargées
EQUIPEMENTS_CSV = RAW_DIR / "equipements_sportifs.csv"

   # Adresse officielle des installations sportives
INSTALLATIONS_URL = (
       "https://equipements.sports.gouv.fr/api/explore/v2.1/catalog/datasets/"
       "data-es-installation/exports/csv"
       "?delimiter=%3B"
    
   )

   # Fichier dans lequel les installations seront téléchargées
INSTALLATIONS_CSV = RAW_DIR / "installations_sportives.csv"

# Valeur du menu Région qui affiche toute la France (carte + histogramme)
TOUTE_LA_FRANCE = "Toute la France"