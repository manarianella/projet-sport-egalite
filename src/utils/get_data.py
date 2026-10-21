"""Récupération des données publiques du projet SportÉgalité."""

import requests

from config import EQUIPEMENTS_CSV, EQUIPEMENTS_URL


def telecharger_equipements() -> None:
    """Télécharge le fichier CSV officiel des équipements sportifs."""

    # Créer le dossier de destination si nécessaire
    EQUIPEMENTS_CSV.parent.mkdir(parents=True, exist_ok=True)

    print("Téléchargement des équipements sportifs en cours...")

    # Télécharger les données progressivement
    with requests.get(
        EQUIPEMENTS_URL,
        stream=True,
        timeout=120,
    ) as response:
        response.raise_for_status()

        # Enregistrer les données sans les modifier
        with EQUIPEMENTS_CSV.open("wb") as fichier:
            for bloc in response.iter_content(chunk_size=1024 * 1024):
                if bloc:
                    fichier.write(bloc)

    print(f"Téléchargement terminé : {EQUIPEMENTS_CSV}")


if __name__ == "__main__":
    telecharger_equipements()