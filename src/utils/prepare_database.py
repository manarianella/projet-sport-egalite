"""Prépare la base SQLite locale pour le dashboard SportÉgalité."""

import gzip
import shutil
import sqlite3

from config import DATABASE_PATH

ARCHIVE_PATH = DATABASE_PATH.with_suffix(".sqlite.gz")

TABLES_REQUISES = (
    "raw",
    "cleaned",
    "raw_installations",
    "cleaned_installations",
)


def preparer_base() -> None:
    """Restaure la base SQLite si elle n'existe pas."""
    if DATABASE_PATH.is_file():
        return

    if not ARCHIVE_PATH.is_file():
        raise FileNotFoundError(f"Base et archive introuvables : {DATABASE_PATH}")

    DATABASE_PATH.parent.mkdir(parents=True, exist_ok=True)

    temporaire = DATABASE_PATH.with_name("db_temp.sqlite")

    try:
        with (
            gzip.open(ARCHIVE_PATH, "rb") as source,
            temporaire.open("wb") as destination,
        ):
            shutil.copyfileobj(source, destination)

        with sqlite3.connect(temporaire) as connexion:
            resultat = connexion.execute("PRAGMA integrity_check").fetchone()[0]

            if resultat != "ok":
                raise RuntimeError("Archive SQLite invalide.")

            tables = {
                ligne[0]
                for ligne in connexion.execute(
                    "SELECT name FROM sqlite_master WHERE type='table'"
                )
            }

            if not set(TABLES_REQUISES).issubset(tables):
                raise RuntimeError("Tables SQLite manquantes.")

        temporaire.replace(DATABASE_PATH)
        print("Base SQLite restaurée avec succès.")

    finally:
        temporaire.unlink(missing_ok=True)


if __name__ == "__main__":
    preparer_base()
