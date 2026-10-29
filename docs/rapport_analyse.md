## Rapport d'analyse

### Question étudiée

> **Toutes les communes françaises disposent-elles du même accès aux installations sportives ?**

Pour y répondre, nous avons analysé le recensement national des équipements sportifs
(Data ES, ministère chargé des Sports) sous quatre angles :

1. **Où** se trouvent les installations sportives sur le territoire (carte de densité) ;
2. **Quelles communes** concentrent le plus d'équipements (classement des communes) ;
3. **Comment** les équipements sont regroupés en installations, selon les communes
   (comparaison installations / équipements) ;
4. **Quelle taille** ont les équipements selon leur nature (histogramme des surfaces).

Les chiffres présentés proviennent de la base `data/db.sqlite` (tables `cleaned`
et `cleaned_installations`). Ils peuvent être retrouvés dans le dashboard
avec les filtres indiqués pour chaque graphique.

**Les données analysées :**
| Élément                                                   | Valeur           |
|:----------------------------------------------------------|-----------------:|
| Équipements sportifs                                      |          334 371 |
| Installations sportives (brutes)                          |          152 309 |
| Installations conservées après nettoyage                  |          144 572 |
| Installations exclues (coordonnées absentes ou invalides) |            7 737 |
| Équipements rattachés à une région                        | 319 426 (95,5 %) |
| Équipements avec une surface exploitable                  |          277 915 |

Une installation est un lieu (un complexe sportif, un lycée, une piscine municipale). Un équipement est un espace de pratique à l'intérieur de ce lieu (un gymnase, un terrain de football, un court de tennis). Une installation contient en moyenne un peu plus de deux équipements.

### 1. Une offre concentrée dans les agglomérations, dispersée ailleurs

![Carte de densité des installations sportives](docs/images/carte_densite.png)

La carte de densité (vue « Toute la France ») montre que les installations sportives
sont présentes sur l'ensemble du territoire, mais avec une intensité très variable :

- la plus forte concentration se situe en **Île-de-France**, autour de Paris ;
- les autres grandes agglomérations forment des pôles bien visibles :
  Lille, Lyon, Nantes, Bordeaux, Marseille, Toulouse, Strasbourg ;
- l'axe **Rhône-Alpes** (de Lyon à Grenoble et vers la Suisse) apparaît
  comme une zone continue de forte densité ;
- certaines zones sont nettement plus claires, par exemple entre Paris et Nancy
  (**Champagne**) ou au sud d'Orléans (**Sologne, Berry**).

Les territoires ruraux ne sont pas dépourvus d'installations : celles-ci y sont
présentes dans presque chaque commune, mais **dispersées** plutôt que concentrées.

**Constat :** la répartition des installations suit celle de la population.
Elles sont concentrées dans les grandes agglomérations et plus dispersées dans
les territoires ruraux. La carte montre donc **où se trouve l'offre sportive**,
mais ne permet pas, à elle seule, de mesurer l'accès des habitants.

### 2. Les grandes villes concentrent le plus d'équipements

![Classement des communes les plus équipées](docs/images/classement_communes.png)

Le classement des dix communes comptant le plus d'équipements sportifs
(vue « Toute la France », mode « Équipements ») est dominé par les grandes villes :

| Rang | Commune     | Équipements sportifs |
|-----:|:------------|---------------------:|
|    1 | Paris       |                2 940 |
|    2 | Toulouse    |                2 106 |
|    3 | Marseille   |                1 480 |
|    4 | Lyon        |                  881 |
|    5 | Reims       |                  800 |
|    6 | Nantes      |                  773 |
|    7 | Strasbourg  |                  688 |
|    8 | Montpellier |                  675 |
|    9 | Le Mans     |                  576 |
|   10 | Dijon       |                  565 |

En **Île-de-France**, Paris compte environ **dix fois plus** d'équipements
que la deuxième commune de la région, Rueil-Malmaison (2 920 contre 295).

Le classement réserve aussi des surprises : **Toulouse** arrive juste derrière Paris,
alors qu'elle compte environ quatre fois moins d'habitants. À l'inverse,
**Lyon** n'est que quatrième, loin derrière Marseille. Le nombre d'équipements
ne dépend donc pas seulement de la taille de la ville, mais aussi des choix
d'aménagement de chaque commune.

*Les chiffres de la vue régionale peuvent être légèrement inférieurs à ceux de la vue
nationale : les équipements dont l'installation n'a pas été retrouvée lors de la jointure
(4,5 % du total) n'ont pas de région. Par exemple, Paris compte 2 940 équipements
en France, mais 2 920 dans la vue « Île-de-France ».*

**Choix méthodologique :** dans les données d'origine, Paris, Marseille et Lyon
sont découpées en arrondissements, chacun ayant son propre code INSEE.
Sans correction, aucune de ces trois villes n'apparaissait dans le classement.
Nous avons regroupé les arrondissements dans leur ville
(`regrouper_arrondissements()` dans `clean_data.py`) pour comparer des communes
entre elles.

**Constat :** en nombre absolu, l'offre sportive est très concentrée dans
les grandes villes, mais des écarts importants existent entre villes de taille
comparable.

### 3. Installations et équipements : deux façons de compter

Le graphique de comparaison propose un second mode, « Installations ».
Une **installation** est un lieu (un complexe sportif, un gymnase, un stade),
tandis qu'un **équipement** est un espace de pratique dans ce lieu
(un terrain, une salle, un bassin). Le rapport entre les deux indique si une commune
dispose plutôt de nombreux petits sites ou de sites plus complets.

| Rang | Commune     | Installations | Équipements | Équipements par installation |
|-----:|:------------|--------------:|------------:|-----------------------------:|
|    1 | Paris       |           947 |       2 940 |                          3,1 |
|    2 | Toulouse    |           580 |       2 106 |                          3,6 |
|    3 | Marseille   |           541 |       1 480 |                          2,7 |
|    4 | Lyon        |           358 |         881 |                          2,5 |
|    5 | Reims       |           263 |         800 |                          3,0 |
|    6 | Nantes      |           253 |         773 |                          3,1 |
|    7 | Strasbourg  |           234 |         688 |                          2,9 |
|    8 | Brest       |           227 |         561 |                          2,5 |
|    9 | Montpellier |           192 |         675 |                          3,5 |
|   10 | Perpignan   |           184 |         444 |                          2,4 |

*Classement par nombre d'installations, vue « Toute la France ».
À l'échelle nationale, on compte en moyenne 2,3 équipements par installation
(334 371 équipements pour 144 572 installations).*

Plusieurs observations ressortent :

- **Les quatre premières villes restent les mêmes** dans les deux classements
  (Paris, Toulouse, Marseille, Lyon) : leur avance ne dépend pas de la façon de compter.
- **Toulouse (3,6) et Montpellier (3,5)** ont le plus d'équipements par installation :
  leurs sites sportifs sont en moyenne plus complets, avec plusieurs espaces de pratique
  sur un même lieu.
- **Brest et Perpignan** entrent dans le classement des installations, alors qu'ils
  n'apparaissent pas dans celui des équipements. À l'inverse, **Le Mans et Dijon** en sortent.
  Brest et Perpignan disposent donc de nombreux sites, mais moins équipés
  (2,5 et 2,4 équipements par installation).
- Toutes les communes du classement dépassent la moyenne nationale (2,3) :
  les grandes villes ont tendance à regrouper plusieurs équipements sur un même site.

**Constat :** compter les installations ou les équipements ne donne pas exactement
le même classement. Le nombre d'équipements par installation permet de distinguer
les villes qui ont beaucoup de petits sites de celles qui ont des complexes plus complets.

### 4. Deux grandes familles de surfaces

![Histogramme des surfaces des équipements](docs/images/histogramme_france.png)

L'histogramme représente la surface de l'aire de pratique de chaque équipement.
Sur les 334 371 équipements, **277 915 ont une surface exploitable** :
les autres n'ont pas de surface renseignée, ou une surface nulle ou négative.

La distribution est très **asymétrique** : la surface médiane est de **648 m²**,
mais certains équipements dépassent plusieurs hectares. Pour rester lisible,
l'histogramme est limité par défaut à **10 800 m²**, qui correspond exactement
au 95ᵉ percentile, et peut être élargi à **72 000 m²** (99ᵉ percentile).
Les **13 878 équipements** plus grands que 10 800 m² restent dans la base de données.

![Histogramme élargi à 72 000 m²](docs/images/histogramme_72000.png)

*Avec le seuil à 72 000 m², la grande majorité des équipements se retrouve
dans les premières barres : c'est pourquoi l'affichage par défaut est limité à 10 800 m².*

Deux familles de surfaces apparaissent :

- **les petits équipements**, de loin les plus nombreux : **65,9 %** des équipements
  font moins de 1 000 m² (salles spécialisées, courts de tennis, plateaux sportifs…) ;
- **les terrains de grands jeux**, qui forment un second pic autour de 6 000 à 8 000 m²,
  la taille d'un terrain de football ou de rugby : **11,3 %** des équipements
  mesurent entre 5 000 et 9 000 m².

Le filtre **Nature** précise cette lecture :

| Nature            | Équipements | Surface médiane |
|:------------------|------------:|----------------:|
| Découvert         |     166 838 |          650 m² |
| Intérieur         |      81 677 |          252 m² |
| Extérieur couvert |       4 308 |          600 m² |

- Les équipements **intérieurs** (gymnases, salles) sont les plus petits,
  avec une médiane de 252 m².
- Les équipements **découverts** sont les plus nombreux (60 % des surfaces valides),
  mais restent en majorité de taille modeste (médiane de 650 m²) :
  les grands terrains de plein air n'en représentent qu'une partie.

*Environ 25 000 équipements ont une autre nature (sites naturels ou artificiels,
équipements découvrables). Ils sont inclus dans le choix « Tous les équipements »,
mais ne disposent pas d'un filtre dédié.*

**Constat :** la majorité des équipements sportifs sont de petite taille.
Les grands terrains, plus coûteux à construire et à entretenir, sont nettement moins nombreux.

### Limites de l'analyse

**Limites liées à la question**

- **Des nombres bruts, et non par habitant.** Les classements comptent des équipements
  et des installations, sans tenir compte de la population. Une grande ville en a
  mécaniquement plus qu'un village. Ces résultats décrivent donc **où se trouve l'offre**,
  mais ne mesurent pas directement l'**accès** des habitants. Un indicateur
  « équipements pour 10 000 habitants » serait nécessaire pour comparer équitablement
  les communes.
- **Présence ne signifie pas accessibilité.** Un équipement recensé peut être réservé
  (scolaires, clubs), payant, fermé une partie de l'année ou éloigné des transports.
  La distance entre les habitants et les équipements n'est pas prise en compte.

**Limites liées aux données**

- **Des données déclaratives.** Le recensement Data ES est alimenté par des enquêtes et
  des déclarations, mises à jour de façon inégale selon les territoires.
  Les chiffres correspondent à la version téléchargée en octobre 2026.
- **Des équipements sans surface.** 56 456 équipements (17 %) n'ont pas de surface
  exploitable : ils ne figurent pas dans l'histogramme.
- **Des installations sans position.** 7 737 installations sans coordonnées valides
  ont été exclues de la carte. Par conséquent, 14 945 équipements (4,5 %) n'ont pas pu
  être rattachés à une région : ils apparaissent dans la vue « Toute la France »,
  mais pas dans les vues régionales.

**Limites liées aux choix de représentation**

- **Une carte de densité relative.** Pour rester fluide, la carte nationale regroupe
  les installations par cases d'environ 5 km. Son intensité dépend aussi du niveau
  de zoom : les observations de ce rapport portent sur la vue par défaut.
- **Un histogramme tronqué.** L'affichage est limité à 10 800 m² (ou 72 000 m²)
  pour rester lisible. Les 13 878 équipements plus grands restent dans la base,
  mais ne sont pas représentés.
- **Un filtre « Nature » incomplet.** Environ 25 000 équipements ont une autre nature
  que celles proposées (sites naturels ou artificiels, équipements découvrables) :
  ils sont inclus dans « Tous les équipements », mais ne peuvent pas être sélectionnés seuls.
- **Le regroupement des arrondissements.** Paris, Marseille et Lyon sont traitées
  comme une seule commune chacune. Ce choix permet de comparer des communes entre elles,
  mais masque les écarts entre arrondissements.

  ### Conclusion

> **Toutes les communes françaises disposent-elles du même accès aux installations sportives ?**

Nos données montrent que **non, l'offre sportive n'est pas répartie de façon homogène**
sur le territoire :

- les installations sont **concentrées dans les grandes agglomérations**, en particulier
  en Île-de-France, et plus **dispersées** dans les territoires ruraux (partie 1) ;
- quelques grandes villes dominent nettement les classements : Paris compte à elle seule
  **2 940 équipements**, et environ **dix fois plus** que la deuxième commune
  d'Île-de-France (partie 2) ;
- à taille comparable, les villes ne sont pas équipées de la même façon : Toulouse et
  Montpellier ont des sites plus complets (3,6 et 3,5 équipements par installation),
  tandis que Brest et Perpignan comptent de nombreux sites moins équipés (partie 3) ;
- la grande majorité des équipements sont de **petite taille** (65,9 % font moins
  de 1 000 m²), et les grands terrains sont nettement moins nombreux (partie 4).

Ces résultats doivent cependant être nuancés. Ils décrivent **où se trouvent
les équipements**, et non **l'accès réel des habitants** : un village ne dispose pas
d'autant d'équipements qu'une grande ville, mais il compte aussi beaucoup moins
d'habitants. Pour répondre pleinement à la question, il faudrait rapporter
le nombre d'équipements à la population de chaque commune, et tenir compte
de la distance et des conditions d'accès (horaires, tarifs, public autorisé).

Une suite naturelle de ce projet serait donc d'intégrer les **données de population
de l'INSEE**, afin de calculer un nombre d'équipements pour 10 000 habitants
et de comparer les communes de façon plus équitable.
