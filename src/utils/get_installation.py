"""Téléchargement des installations sportives."""

from pathlib import Path

import requests

BASE_DIR = Path(__file__).resolve().parents[2]

INSTALLATIONS_CSV = (
    BASE_DIR / "data" / "raw" / "installations_sportives.csv"
)

# le lien CSV officiel copié depuis Data ES.
INSTALLATIONS_URL = (
    "https://equipements.sports.gouv.fr/api/explore/v2.1/catalog/datasets/"
    "data-es-installation/exports/csv"
    "?delimiter=%3B"
    "&select=numero,nom,insee,com_name,dep_code,dep_nom,reg_nom,dens_lib"
)


def telecharger_installations() -> None:
    """Télécharge les installations sportives au format CSV."""
    INSTALLATIONS_CSV.parent.mkdir(parents=True, exist_ok=True)

    print("Téléchargement des installations sportives...")

    with requests.get(
        INSTALLATIONS_URL,
        stream=True,
        timeout=120,
    ) as response:
        response.raise_for_status()

        with INSTALLATIONS_CSV.open("wb") as fichier:
            for bloc in response.iter_content(
                chunk_size=1024 * 1024
            ):
                if bloc:
                    fichier.write(bloc)

    print("Téléchargement terminé !")


if __name__ == "__main__":
    telecharger_installations()