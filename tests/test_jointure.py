"""Tests de cohérence de la jointure territoriale."""

import sqlite3

from config import DATABASE_PATH


def test_jointure_conserve_equipements():
    """La jointure ne doit pas supprimer des équipements."""
    with sqlite3.connect(DATABASE_PATH) as connexion:
        nombre_raw = connexion.execute('SELECT COUNT(*) FROM "raw"').fetchone()[0]

        nombre_cleaned = connexion.execute('SELECT COUNT(*) FROM "cleaned"').fetchone()[
            0
        ]

    assert nombre_raw == nombre_cleaned


def test_colonnes_territoriales():
    """Les informations géographiques doivent être présentes."""
    with sqlite3.connect(DATABASE_PATH) as connexion:
        colonnes = {
            ligne[1] for ligne in connexion.execute('PRAGMA table_info("cleaned")')
        }

    attendues = {
        "region",
        "departement",
        "code_departement",
        "type_territoire",
    }

    assert attendues.issubset(colonnes)


def test_rattachement_regions():
    """Une proportion importante doit être rattachée à une région."""
    with sqlite3.connect(DATABASE_PATH) as connexion:
        nombre_total, nombre_rattache = connexion.execute(
            """
            SELECT COUNT(*), COUNT(region)
            FROM cleaned
            """
        ).fetchone()

    assert nombre_total > 0
    assert nombre_rattache / nombre_total >= 0.90
