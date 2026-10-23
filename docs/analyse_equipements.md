# Analyse des équipements sportifs — SportÉgalité

**Projet Python 2 — ESIEE Paris**  
**Anella Manari**

## 1. Objectif

Notre projet SportÉgalité cherche à répondre à la problématique suivante :

**« Toutes les communes françaises disposent-elles du même accès aux installations sportives ? »**

Pour cette première partie, nous avons choisi d'étudier les équipements sportifs français, en nous intéressant particulièrement à leur surface et à leur nature.

L'objectif est de comprendre comment les surfaces se répartissent selon les types d'équipements, puis de compléter cette analyse avec la carte géographique des installations.

## 2. Source et préparation des données

Les données proviennent de la plateforme publique [Data ES](https://data.sports.gouv.fr/), mise à disposition par le ministère chargé des Sports.

Le jeu de données utilisé contient **334 371 équipements sportifs** dans la version téléchargée le 23 octobre 2026.

Nous avons développé un script Python pour télécharger le fichier CSV, puis importer les colonnes utiles dans une base SQLite.

La table `raw` contient les données des équipements avant nettoyage.

Le script `clean_data.py` permet ensuite de créer la table `cleaned`. Les surfaces sont converties en valeurs numériques. Les surfaces manquantes, nulles, négatives ou non numériques sont considérées comme non exploitables.

Les lignes correspondantes restent dans la base, mais leur surface n'est pas utilisée dans l'histogramme.

Après nettoyage, **277 915 équipements possèdent une surface positive exploitable**.

## 3. Histogramme interactif

Nous avons créé un histogramme avec Plotly, intégré dans une interface Dash.

Chaque barre représente une tranche de surfaces en mètres carrés. Sa hauteur correspond au nombre d'équipements appartenant à cette tranche.

L'utilisateur peut sélectionner la nature de l'équipement : intérieur, découvert ou extérieur couvert.

Un deuxième filtre permet de modifier la plage de surface affichée :

- **10 800 m²** : seuil proche du 95e percentile.
- **72 000 m²** : seuil proche du 99e percentile.

Ces valeurs permettent d'observer la majorité des équipements tout en évitant que les surfaces extrêmes rendent le graphique difficile à lire.

Nous avons également ajouté des couleurs différentes selon les catégories et des explications directement dans l'interface pour faciliter la lecture.

## 4. Résultats statistiques

### 4.1. Comparaison des surfaces selon la nature

| Nature de l'équipement | Nombre avec surface valide | Surface médiane |
|---|---:|---:|
| Découvert | 166 838 | 650 m² |
| Intérieur | 81 677 | 252 m² |
| Extérieur couvert | 4 308 | 600 m² |
| Site naturel aménagé | 17 269 | 8 500 m² |
| Site naturel | 4 812 | 10 000 m² |

Les équipements découverts présentent généralement des surfaces plus importantes que les équipements intérieurs.

Les sites naturels présentent des surfaces beaucoup plus grandes. Certaines valeurs extrêmes augmentent fortement leur moyenne, ce qui rend la médiane plus pertinente pour comparer les catégories.

### 4.2. Types d'équipements les plus fréquents

| Type d'équipement | Nombre avec surface valide | Surface médiane |
|---|---:|---:|
| Court de tennis | 37 884 | 648 m² |
| Terrain de football | 35 889 | 6 000 m² |
| Multisports / City-stades | 24 502 | 600 m² |
| Terrain de pétanque | 20 484 | 250 m² |
| Salle multisports (gymnase) | 18 327 | 800 m² |

On remarque que les types d'équipements présentent des surfaces très différentes, notamment entre les terrains de football et les salles spécialisées.

### 4.3. Explication du pic autour de 6 000 m²

Nous avons observé un pic autour de 6 000 m² sur notre histogramme.

Pour comprendre ce résultat, nous avons analysé les équipements dont la surface est comprise entre 5 832 et 6 048 m².

Nous avons identifié notamment 4 467 terrains de football, 303 boucles de randonnée, 138 terrains mixtes et 128 terrains de rugby.

Les terrains de football sont donc les principaux contributeurs identifiés à cette concentration.

Cette analyse montre que certains pics de l'histogramme peuvent correspondre à des surfaces fréquentes pour un type d'équipement particulier.

## 5. Limites de l'analyse

Notre histogramme présente uniquement les équipements possédant une surface valide.

De plus, la surface d'un équipement ne permet pas à elle seule de mesurer son accessibilité.

Une commune peut avoir plusieurs installations sportives sans que tous les habitants puissent les utiliser. Les différences de population, la distance et les conditions d'accès doivent également être prises en compte.

La carte des installations sportives développée dans le projet permet de compléter cette analyse en étudiant leur répartition géographique.

## 6. Conclusion

Cette étude met en évidence des différences importantes entre les surfaces des équipements sportifs français.

Les équipements intérieurs sont généralement plus petits que les équipements découverts, tandis que les sites naturels peuvent présenter des surfaces beaucoup plus importantes.

L'histogramme interactif permet de visualiser ces différences et de comprendre la répartition des surfaces. Toutefois, ces observations ne suffisent pas à démontrer une inégalité d'accès entre les communes : elles doivent être complétées par l'analyse territoriale des installations sportives.