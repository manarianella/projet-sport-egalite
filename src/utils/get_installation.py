"""Téléchargement des installations sportives."""

import requests
from config import INSTALLATIONS_CSV, INSTALLATIONS_URL


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