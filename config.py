"""Configuration du projet SportÉgalité."""

from pathlib import Path

# Dossier principal du projet
BASE_DIR = Path(__file__).resolve().parent

# Dossiers de stockage des données
DATA_DIR = BASE_DIR / "data"
RAW_DIR = DATA_DIR / "raw"

# Base de données SQLite
DATABASE_PATH = DATA_DIR / "db.sqlite"

# Source officielle des équipements sportifs
EQUIPEMENTS_URL = (
    "https://data.sports.gouv.fr/api/explore/v2.1/"
    "catalog/datasets/equipements-sportifs/exports/csv"
    "?lang=fr&timezone=Europe%2FBerlin"
    "&use_labels=true&delimiter=%3B"
)

# Fichier de téléchargement des équipements
EQUIPEMENTS_CSV = RAW_DIR / "equipements_sportifs.csv"

# Source officielle des installations sportives
INSTALLATIONS_URL = (
    "https://equipements.sports.gouv.fr/api/explore/v2.1/catalog/datasets/"
    "data-es-installation/exports/csv"
    "?delimiter=%3B"
)

# Fichier de téléchargement des installations
INSTALLATIONS_CSV = RAW_DIR / "installations_sportives.csv"

# Valeur du filtre permettant d'afficher toute la France
TOUTE_LA_FRANCE = "Toute la France"
