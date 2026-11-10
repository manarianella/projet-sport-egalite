# Prompts structurants — utilisation de l'IA
 
Ce fichier répond à la consigne : « Dans le cas de l'IA agentique, les prompts les plus structurants doivent être fournis. »
 
Les prompts ci-dessous correspondent à nos **demandes réelles**, dans l'ordre où nous les avons faites. Ils ont été **reformulés** pour être plus clairs et plus complets (contexte, objectif, contraintes), sans changer leur sens. Pour chacun, nous indiquons ce qu'il a produit dans le projet et, quand c'est le cas, comment nous l'avons vérifié.
 
---
 
## Zelal Sahin — Claude (Anthropic)
 
### Méthode
 
J'ai utilisé **Claude** comme assistant pendant toute ma partie du projet : compréhension de la consigne, récupération et nettoyage des données, carte, tests, Git et rédaction. Je lui ai demandé de **ne plus fournir de fichiers complets**, mais les étapes et les fonctions à modifier, afin d'écrire et de comprendre le code moi-même. Chaque proposition a été exécutée sur nos données et vérifiée avec `pytest`, Ruff et Mypy.
 
### 1. Cadrage et choix des données
 
**Prompt 1 — Choix du sujet**
> Voici la consigne de notre mini-projet de Python 2 : un dashboard Dash et Plotly construit sur des données publiques Open Data. Le jeu de données doit contenir plusieurs centaines d'observations, au moins une variable numérique non catégorielle pour un histogramme, et des observations géolocalisables pour une carte. Propose plusieurs sujets d'intérêt public compatibles avec ces contraintes, avec pour chacun les sources possibles et leurs avantages et limites.
 
*Résultat :* choix du sujet sur la répartition des équipements sportifs en France (Data ES). *Vérification :* validation du sujet avec Anella et l'enseignant.
 
### 2. Récupération des données (`get_data.py`)
 
**Prompt 2 — Un seul script de récupération**
> L'enseignant demande un seul fichier `get_data.py` pour toutes les sources, au lieu de `get_data.py` et `get_installation.py`. Fusionne les deux en évitant de répéter le code de téléchargement, et garde une table `raw` par source.
 
*Résultat :* fusion des scripts, avec une fonction générique `telecharger_fichier()`. *Vérification :* relance complète de `get_data.py` puis de `clean_data.py`.
 
**Prompt 3 — Ajout de la population**
> L'enseignant demande d'intégrer la population des communes pour comparer les territoires par habitant. Trouve une source publique et officielle, puis donne-moi les étapes pour : récupérer les données dans `get_data.py`, créer une table `raw_population` sans modification, puis une table `cleaned_population` dans `clean_data.py`, avec un code commune compatible avec nos autres tables.
 
*Résultat :* API Découpage administratif (populations Insee) ; `telecharger_population()`, `importer_population_sqlite()` (lecture du JSON avec `json_normalize`) et `nettoyer_population()`. *Vérification :* 34 969 communes importées, 34 957 conservées.
 
### 3. Nettoyage des données (`clean_data.py`)
 
**Prompt 4 — Nettoyage des installations**
> À partir de la table `raw_installations`, explique quelles étapes de nettoyage sont nécessaires pour une carte (doublons, coordonnées au format « latitude, longitude », valeurs invalides, codes de département), puis aide-moi à les écrire en petites fonctions testables qui créent la table `cleaned_installations`.
 
*Résultat :* `nettoyer_installations()`, `separer_coordonnees()`, `filtrer_coordonnees_valides()`. *Vérification :* 144 564 installations conservées ; tests du nettoyage.
 
**Prompt 5 — Arrondissements**
> Paris, Marseille et Lyon n'apparaissent pas dans le classement des communes, car leurs arrondissements ont chacun leur propre code INSEE. Propose une solution pour regrouper les arrondissements dans leur commune, compatible avec la jointure de la population.
 
*Résultat :* `regrouper_arrondissements()`, colonnes `code_commune` et `nom_commune`. *Vérification :* Paris, Marseille et Lyon présentes dans les classements.
 
### 4. Carte à bulles (`map_chart.py`, `map_layout.py`)
 
**Prompt 6 — Nouvelle carte demandée par l'enseignant**
> L'enseignant veut remplacer notre carte de densité par une carte à bulles inspirée de celle des stations Vélib' : une bulle par région en vue nationale, qui se divise en départements puis en communes quand on zoome. Quand on choisit une région, il doit y avoir une bulle par grande commune. Au survol, chaque bulle doit indiquer la population, le nombre d'installations et d'équipements, et les équipements les plus présents. La couleur doit représenter le nombre d'installations pour 10 000 habitants. Explique comment organiser ce regroupement avec Pandas et comment lire le zoom dans un callback Dash.
 
*Résultat :* regroupement par niveau avec `groupby`, choix du niveau selon le zoom, lecture du zoom avec `relayoutData` et conservation de la vue avec `uirevision`. *Vérification :* tests dans le navigateur sur plusieurs régions et niveaux de zoom.
 
**Prompt 7 — Écrire le code moi-même**
> Ne me donne plus de fichiers complets. Donne-moi les étapes, les fonctions à ajouter ou modifier et dans quels fichiers, avec une explication courte de chaque fonction, pour que j'écrive le code moi-même. Garde la carte dans `map_chart.py` et `map_layout.py`, sans créer de nouveau fichier.
 
*Résultat :* carte écrite étape par étape : `charger_donnees()`, `types_principaux()`, `compter_par_niveau()`, `preparer_niveaux()`, `choisir_niveau()`, `filtrer_vue()`, `creer_carte_bulles()` et le callback `actualiser_carte()`. *Vérification :* commande de contrôle après chaque étape (régions, populations, ratios).
 
**Prompt 8 — Afficher le ratio dans les bulles**
> Quand on zoome sur les communes, chaque bulle doit afficher directement le nombre d'installations pour 10 000 habitants, sans afficher les noms des rues. Quelle fonction faut-il modifier ?
 
*Résultat :* texte des bulles remplacé par le ratio. *Vérification :* comparaison avec des calculs à la main (Champigny-sur-Marne : 54 installations pour 78 072 habitants, soit 6,9).
 
**Prompt 9 — Interpréter les valeurs extrêmes**
> Certaines bulles affichent 58 ou 45 installations pour 10 000 habitants, et plus de 600 en montagne. Est-ce une erreur ? Comment l'expliquer, et faut-il les garder sur la carte ?
 
*Résultat :* explication par les petites populations et le tourisme ; valeurs gardées et expliquées dans le rapport. *Vérification :* survol des bulles concernées (population et nombre d'installations).
 
### 5. Tests et qualité du code
 
**Prompt 10 — Organisation des tests**
> Pourquoi les tests du nettoyage des installations sont-ils dans un fichier séparé, alors que tout le nettoyage est dans `clean_data.py` ? Et pourquoi ne testons-nous pas `get_data.py` ? Propose une organisation cohérente, et un test de la population qui ne touche pas à la vraie base.
 
*Résultat :* tests de nettoyage regroupés dans `test_clean_data.py` ; test `test_nettoyer_population` sur une base temporaire (`tmp_path`, `monkeypatch`). *Vérification :* même nombre de tests avant et après le regroupement.
 
**Prompt 11 — Garder seulement les tests utiles**
> Parmi les tests de la carte et de l'histogramme, lesquels sont vraiment nécessaires ? Indique ceux qui font doublon pour que je puisse les supprimer.
 
*Résultat :* suppression des tests en doublon. *Vérification :* 23 tests au total, tous réussis.
 
**Prompt 12 — Erreurs de typage**
> Mypy signale des bibliothèques sans types (pandas, plotly) et une erreur dans `inegalites_chart.py`. Explique l'origine de chaque erreur et la correction la plus simple.
 
*Résultat :* `ignore_missing_imports` dans `pyproject.toml` ; type `list[int | str]` pour les paramètres SQL. *Vérification :* `uv run mypy src` sans erreur.
 
### 6. Documentation
 
**Prompt 13 — Relecture du README**
> Voici notre README. Vérifie que les sections sur la carte, la population, le nettoyage, la base SQLite, les tests et l'utilisation de l'IA correspondent au code actuel, et liste ce qui manque ou est encore provisoire.
 
*Résultat :* mise à jour des sections 1.7.2, 2.1, 2.5, 2.6.1, 2.7.1, 3.7, 4.2 et 5.5. *Vérification :* comparaison avec le code et les effectifs des tables SQLite.
 
---
 
## Anella Manari — ChatGPT (OpenAI)
 
### 1. Architecture et interface
 
**Prompt 14 — Conception de l'architecture du projet**
> Nous développons, en binôme, un dashboard interactif en Python dans le cadre d'un projet de Data Science à l'ESIEE Paris. Notre application, SportÉgalité, vise à analyser les disparités territoriales dans la répartition des équipements et installations sportives en France. Nous disposons de données publiques sur les équipements sportifs, les installations sportives et la population des communes. Propose une architecture Python claire, modulaire et maintenable, en séparant la configuration et les chemins des données, la récupération et le nettoyage des données, le stockage dans SQLite, les composants graphiques Plotly, l'interface Dash et les callbacks, et les tests unitaires. Explique le rôle de chaque fichier, les échanges entre les modules et les choix d'organisation. Privilégie une solution adaptée à notre niveau et facile à développer sur GitLab à deux personnes.
 
*Résultat :* organisation autour de `main.py`, `config.py`, `src/components/`, `src/utils/`, `tests/` et `assets/`.
 
**Prompt 15 — Création d'une interface Dash interactive**
> Nous avons développé plusieurs visualisations avec Plotly pour SportÉgalité : une carte des installations, un histogramme des surfaces et un diagramme comparatif des communes. Je souhaite les intégrer dans une interface Dash cohérente et interactive. Le dashboard doit comporter une barre latérale avec un filtre régional commun à toutes les visualisations et un filtre de nature agissant uniquement sur l'histogramme. Il doit également présenter trois cartes statistiques : nombre d'équipements, nombre d'installations et nombre de communes représentées, les deux premières avec un ratio pour 10 000 habitants. Aide-moi à organiser les composants et les callbacks avec `Input`, `Output` et les identifiants Dash appropriés, pour que chaque changement de région mette à jour les éléments concernés sans recharger toute l'application.
 
*Résultat :* `main.py`, `histogram_layout.py` et `map_layout.py`.
 
**Prompt 16 — Amélioration de l'ergonomie et du CSS**
> Je souhaite améliorer l'interface visuelle de notre dashboard sans modifier son fonctionnement : une interface professionnelle et lisible, avec une barre latérale bleu marine, des cartes statistiques, des graphiques bien séparés et une hiérarchie visuelle claire. Propose des améliorations CSS pour harmoniser les couleurs, les espacements et les typographies, rendre les filtres Dash lisibles, créer des infobulles explicatives sur les cartes statistiques, ajouter des raccourcis de navigation vers les trois visualisations, conserver une barre latérale utilisable sur différentes tailles d'écran et empêcher les menus déroulants d'être coupés. Analyse les règles CSS existantes avant de proposer une modification et indique précisément quelles règles remplacer.
 
*Résultat :* `assets/style.css`, `assets/zz_sidebar.css` et `main.py`.
 
### 2. Visualisations
 
**Prompt 17 — Construction de l'histogramme des surfaces**
> Je souhaite créer un histogramme interactif avec Plotly pour analyser la distribution des surfaces des équipements sportifs en France, à partir de la table SQLite `cleaned`. Le graphique doit conserver uniquement les surfaces numériques valides et strictement positives, utiliser une plage fixe de 0 à 10 800 m² répartie en 50 intervalles de largeur identique, afficher le nombre d'équipements par intervalle, permettre un filtrage par région et par nature d'équipement, et afficher au survol l'intervalle, l'effectif et les principaux types d'équipements. Utilise NumPy pour les calculs et Plotly pour la visualisation, explique chaque étape et propose une fonction réutilisable dans notre application Dash, sans modifier les autres composants.
 
*Résultat :* `src/components/histogram.py` et `src/components/histogram_layout.py`.
 
**Prompt 18 — Comparaison des communes avec des ratios par habitant**
> Nous souhaitons comparer les communes françaises selon leur dotation en infrastructures sportives. Une comparaison des nombres absolus serait peu pertinente, car les communes ont des populations très différentes. À partir des tables SQLite des équipements, des installations et des populations, aide-moi à développer un graphique Plotly qui calcule le nombre d'équipements et d'installations pour 10 000 habitants, sélectionne les cinq communes les mieux dotées selon chaque ratio, réunit les deux classements sans doublon, exclut les communes de moins de 1 000 habitants, présente deux barres horizontales par commune (turquoise pour les équipements, orange pour les installations), s'adapte au filtre régional et affiche dans les infobulles la population, les effectifs et les ratios. Explique aussi les limites d'une comparaison fondée sur la population résidente.
 
*Résultat :* `src/components/inegalites_chart.py`.
 
### 3. Qualité, Git et documentation
 
**Prompt 19 — Correction des erreurs et qualité du code**
> Notre application Dash fonctionne, mais certains outils d'analyse statique signalent des erreurs. Je vais te transmettre les sorties de Mypy, Ruff, Pylint et Pytest ainsi que les extraits des fichiers concernés. Pour chaque problème, explique l'origine exacte de l'erreur, identifie le fichier et la ligne concernés, propose une correction minimale compatible avec notre version de Dash, préserve le comportement des graphiques, des callbacks et des requêtes SQLite, et indique les commandes pour vérifier la correction. Évite les refactorisations inutiles et n'affirme pas qu'une correction fonctionne tant qu'elle n'a pas été testée.
 
*Résultat :* corrections de typage dans `main.py`, vérifications avec Mypy, Ruff et Pytest.
 
**Prompt 20 — Gestion collaborative avec Git et GitLab**
> Nous développons SportÉgalité en binôme avec GitLab, avec quatre branches : `anella`, `zelal`, `dev` pour l'intégration et `main` pour la version finale. Explique-moi étape par étape comment récupérer les modifications de ma coéquipière, conserver mes changements locaux, créer un commit et proposer une Merge Request vers `dev`, en tenant compte de fichiers Python et CSS modifiés localement et de sauvegardes SQLite non suivies. Donne les commandes Git exactes, leur effet, et les précautions pour éviter les pertes de données, les conflits et l'envoi de fichiers inutiles.
 
*Résultat :* commits, récupération des branches distantes, fusions et Merge Requests GitLab.
 
**Prompt 21 — Rédaction de la documentation**
> Aide-nous à rédiger et à améliorer le README de SportÉgalité en respectant les consignes du module Python 2, autour des parties User Guide, Data, Developer Guide, Analysis et Copyright. Utilise un style clair et naturel, adapté à un rapport d'étudiants ingénieurs. Ne supprime pas les explications techniques importantes, signale les informations manquantes ou non vérifiées au lieu d'inventer des résultats, des sources ou des tests, et veille à ce que les descriptions correspondent aux fonctionnalités réellement implémentées.
 
*Résultat :* `README.md`, notamment les guides, les légendes de captures et la traçabilité des aides extérieures.
 
**Prompt 22 — Préparation de la vidéo de démonstration**
> Nous devons réaliser une vidéo commentée de SportÉgalité de quatre minutes maximum : une minute pour montrer les fonctionnalités du dashboard à vitesse réelle, puis trois minutes pour présenter où et comment les technologies sont utilisées dans notre code. Propose un déroulement minuté, réparti équitablement entre nous deux, avec les actions à l'écran, les fichiers à afficher et un texte oral naturel. Je présenterai l'introduction, les visualisations, la récupération des données et SQLite ; ma coéquipière présentera le nettoyage, la carte et les tests.
 
*Résultat :* scénario et commentaire oral de la vidéo.
 
---
 
## Vérification des propositions issues de l'IA
 
Nous n'avons pas considéré les réponses des assistants comme automatiquement correctes. Les principales vérifications ont reposé sur :
 
- l'exécution du dashboard et les tests manuels des interactions ;
- la comparaison des graphiques avec les données SQLite ;
- l'exécution des tests unitaires avec Pytest ;
- les contrôles de qualité et de typage avec Ruff et Mypy ;
- la relecture du README et la vérification des informations documentées.
Les résultats statistiques proviennent des jeux de données publics exploités par le projet et ne doivent pas être présentés comme des résultats générés par l'IA.