# Fly-in — Les drones, c'est intéressant.

**Résumé :** Concevoir un système de routage efficace pour drones, navigant à travers des zones connectées tout en minimisant le nombre de tours de simulation et en gérant les contraintes de déplacement.

**Version :** 1.4

---

## Table des matières

1. [Avant-propos](#avant-propos)
2. [Instructions IA](#instructions-ia)
3. [Instructions générales](#instructions-générales)
4. [Introduction](#introduction)
5. [Contraintes](#contraintes)
6. [Faisons voler le drone](#faisons-voler-le-drone)
7. [Partie obligatoire](#partie-obligatoire)
8. [Exigences du README](#exigences-du-readme)
9. [Partie bonus](#partie-bonus)
10. [Soumission et évaluation par les pairs](#soumission-et-évaluation-par-les-pairs)

---

## Avant-propos

Des drones ont été utilisés pour rassembler des moutons en Nouvelle-Zélande, remplaçant les chiens de berger par des bergers aériens bourdonnants. Au Japon, des immeubles de bureaux déploient des drones qui jouent de la musique forte et font clignoter des lumières pour littéralement chasser les employés surmenés chez eux. Un drone a été entraîné à peindre des graffitis sur les murs en plein vol — un mélange rebelle de technologie et d'art de rue. En Suède, des scientifiques ont utilisé des drones pour renifler les excréments de baleines flottant sur l'océan afin d'étudier des espèces en voie de disparition. Certains drones expérimentaux sont conçus pour ressembler à des oiseaux ou à des insectes pour espionner sans être remarqués, battant des ailes et tout. Il existe même un drone qui vole en battant des bulles de savon, sans hélices. Dans la recherche volcanique, un drone a une fois volé directement dans un nuage d'éruption, a fondu en plein air, mais a réussi à transmettre des données quelques secondes avant sa désintégration. Et en Corée du Sud, des spectacles de drones synchronisés ont remplacé les feux d'artifice — plus sûrs, silencieux, et d'une certaine façon encore plus magiques.

L'expression vient de l'idée que la roue est une invention brillante qui existe depuis toujours et fonctionne très bien. Puisqu'il n'y a rien à corriger, essayer de la réinventer n'aiderait vraiment pas et pourrait être une perte de temps — surtout quand ce temps pourrait être consacré à résoudre de nouveaux problèmes.

En programmation, cela se produit quand quelqu'un construit quelque chose à partir de zéro qui existe déjà — comme écrire son propre algorithme de tri ou son propre framework alors que des versions solides et open-source existent déjà. Mais ce n'est pas toujours négatif : le faire soi-même peut être une excellente façon d'apprendre comment les choses fonctionnent en profondeur. La clé est de trouver un équilibre — ne pas tout reconstruire, mais prendre le temps d'explorer comment les outils que vous utilisez fonctionnent réellement. De cette façon, vous grandirez en tant que développeur sans vous retrouver à réinventer les mêmes vieilles roues.

---

## Instructions IA

### Contexte

Tout au long de votre parcours d'apprentissage, l'IA peut vous aider dans de nombreuses tâches. Prenez le temps d'explorer les différentes capacités des outils IA et la façon dont ils peuvent soutenir votre travail. Cependant, abordez-les toujours avec prudence et évaluez les résultats de manière critique. Qu'il s'agisse de code, de documentation, d'idées ou d'explications techniques, vous ne pouvez jamais être complètement sûr que votre question était bien formulée ou que le contenu généré est exact. Vos pairs sont une ressource précieuse pour vous aider à éviter les erreurs et les angles morts.

### Message principal

- Utilisez l'IA pour réduire les tâches répétitives ou fastidieuses.
- Développez des compétences en prompting — à la fois en codage et hors codage — qui bénéficieront à votre future carrière.
- Apprenez comment fonctionnent les systèmes IA pour mieux anticiper et éviter les risques courants, les biais et les problèmes éthiques.
- Continuez à développer vos compétences techniques et interpersonnelles en travaillant avec vos pairs.
- N'utilisez que du contenu généré par l'IA que vous comprenez pleinement et dont vous pouvez assumer la responsabilité.

### Règles pour les apprenants

- Vous devez prendre le temps d'explorer les outils IA et de comprendre leur fonctionnement, afin de les utiliser de manière éthique et de réduire les biais potentiels.
- Vous devez réfléchir à votre problème avant de formuler une invite — cela vous aide à écrire des prompts plus clairs, plus détaillés et plus pertinents en utilisant un vocabulaire précis.
- Vous devez développer l'habitude de systématiquement vérifier, revoir, questionner et tester tout ce qui est généré par l'IA.
- Vous devez toujours chercher une révision par les pairs — ne vous fiez pas uniquement à votre propre validation.

### Résultats attendus

- Développer des compétences en prompting à la fois générales et spécifiques au domaine.
- Booster votre productivité avec une utilisation efficace des outils IA.
- Continuer à renforcer la pensée computationnelle, la résolution de problèmes, l'adaptabilité et la collaboration.

### Commentaires et exemples

- Vous rencontrerez régulièrement des situations — examens, évaluations, etc. — où vous devrez démontrer une vraie compréhension. Soyez prêt, continuez à développer vos compétences techniques et interpersonnelles.
- Expliquer votre raisonnement et débattre avec vos pairs révèle souvent des lacunes dans votre compréhension. Faites de l'apprentissage entre pairs une priorité.
- Les outils IA manquent souvent de votre contexte spécifique et ont tendance à fournir des réponses génériques. Vos pairs, qui partagent votre environnement, peuvent offrir des insights plus pertinents et précis.

**Bonne pratique :**
> Je demande à l'IA : « Comment tester une fonction de tri ? » Elle me donne quelques idées. Je les essaie et révise les résultats avec un pair. Nous affinons l'approche ensemble.

**Mauvaise pratique :**
> Je demande à l'IA d'écrire une fonction entière, je la copie-colle dans mon projet. Pendant l'évaluation par les pairs, je ne peux pas expliquer ce qu'elle fait ni pourquoi. Je perds en crédibilité — et j'échoue mon projet.

---

## Instructions générales

### Règles générales

- Le projet doit être écrit en **Python 3.10 ou version ultérieure**.
- Le projet doit respecter la norme de codage **flake8**.
- Vos fonctions doivent gérer les exceptions de manière élégante pour éviter les plantages. Utilisez des blocs `try-except` pour gérer les erreurs potentielles. Préférez les gestionnaires de contexte pour les ressources comme les fichiers ou les connexions pour assurer un nettoyage automatique. Si votre programme plante en raison d'exceptions non gérées pendant la révision, il sera considéré comme non fonctionnel.
- Toutes les ressources (ex : fichiers, connexions réseau) doivent être correctement gérées pour éviter les fuites. Utilisez des gestionnaires de contexte lorsque c'est possible.
- Votre code doit inclure des **annotations de type** pour les paramètres de fonctions, les types de retour et les variables (en utilisant le module `typing`). Utilisez `mypy` pour la vérification statique des types. Toutes les fonctions doivent passer mypy sans erreurs.
- Incluez des **docstrings** dans les fonctions et les classes selon PEP 257 (style Google ou NumPy) pour documenter l'objectif, les paramètres et les retours.

### Makefile

Incluez un `Makefile` dans votre projet pour automatiser les tâches courantes. Il doit contenir les règles suivantes :

| Règle | Description |
|-------|-------------|
| `install` | Installer les dépendances du projet via pip, uv, pipx ou tout autre gestionnaire de paquets |
| `run` | Exécuter le script principal du projet |
| `debug` | Lancer le script principal en mode débogage via le débogueur Python intégré (pdb) |
| `clean` | Supprimer les fichiers temporaires ou les caches (`__pycache__`, `.mypy_cache`) |
| `lint` | Exécuter `flake8 .` et `mypy . --warn-return-any --warn-unused-ignores --ignore-missing-imports --disallow-untyped-defs --check-untyped-defs` |
| `lint-strict` *(optionnel)* | Exécuter `flake8 .` et `mypy . --strict` |

### Directives supplémentaires

- Créez des programmes de test pour vérifier la fonctionnalité du projet (non soumis ni noté). Utilisez des frameworks comme `pytest` ou `unittest` pour les tests unitaires, en couvrant les cas limites.
- Incluez un fichier `.gitignore` pour exclure les artefacts Python.
- Il est recommandé d'utiliser des environnements virtuels (ex : `venv` ou `conda`) pour l'isolation des dépendances lors du développement.

---

## Introduction

Les drones autonomes sont l'avenir du transport. Ils sont déjà utilisés dans de nombreux secteurs, tels que l'agriculture, la construction et la logistique. Ils sont également utilisés dans des opérations militaires, telles que la surveillance et la reconnaissance.

Votre tâche est de concevoir un système qui achemine efficacement une flotte de drones depuis une base centrale (**départ**) vers un emplacement cible (**arrivée**), tout en naviguant dans ce réseau dynamique sous un ensemble de contraintes strictes et d'objectifs d'optimisation.

Vous recevrez un graphe représentant le réseau de zones, et un ensemble de contraintes que vous devez respecter.

Le graphe est représenté comme un réseau de zones connectées, où les connexions définissent les chemins de déplacement possibles entre les zones.

---

## Contraintes

- Toute bibliothèque qui aide avec la logique de graphe est **interdite** (comme `networkx`, `graphlib`, etc.).
- Le projet doit être complètement **typé** (type-safe). L'utilisation de `flake8` et `mypy` est obligatoire.
- Le projet doit être complètement **orienté objet**.

---

## Faisons voler le drone

Les fichiers d'entrée représentent le réseau de zones dans le format suivant :

```
nb_drones: 5
start_hub: hub 0 0 [color=green]
end_hub: goal 10 10 [color=yellow]
hub: roof1 3 4 [zone=restricted color=red]
hub: roof2 6 2 [zone=normal color=blue]
hub: corridorA 4 3 [zone=priority color=green max_drones=2]
hub: tunnelB 7 4 [zone=normal color=red]
hub: obstacleX 5 5 [zone=blocked color=gray]
connection: hub-roof1
connection: hub-corridorA
connection: roof1-roof2
connection: roof2-goal
connection: corridorA-tunnelB [max_link_capacity=2]
connection: tunnelB-goal
```

### Détails du format de fichier

- La **première ligne** définit le nombre de drones : `nb_drones: <nombre>`.
- Les définitions de zones utilisent des préfixes de type :
  - `start_hub: <nom> <x> <y> [métadonnées]` — marque la zone de départ
  - `end_hub: <nom> <x> <y> [métadonnées]` — marque la zone d'arrivée
  - `hub: <nom> <x> <y> [métadonnées]` — définit une zone ordinaire
  - La syntaxe des connexions **interdit les tirets** dans les noms de zones.
- Toutes les métadonnées sont optionnelles et entre crochets `[...]` avec des valeurs par défaut :
  - `zone=<type>` (défaut : `normal`)
  - `color=<valeur>` (défaut : aucune)
  - `max_drones=<nombre>` (défaut : 1) — Nombre maximum de drones pouvant occuper cette zone simultanément
  - Les balises à l'intérieur des crochets peuvent apparaître dans n'importe quel ordre.

### Types de zones

| Type | Description |
|------|-------------|
| `normal` | Zone standard avec un coût de déplacement de 1 tour (défaut) |
| `blocked` | Zone inaccessible — les drones ne doivent pas y entrer ou passer |
| `restricted` | Zone sensible — le déplacement coûte 2 tours |
| `priority` | Zone préférée — coûte 1 tour mais priorisée dans le pathfinding |

### Couleurs

- Les couleurs sont optionnelles et peuvent être utilisées pour la représentation visuelle.
- Valeurs acceptées : toute chaîne de caractères valide en un seul mot (ex : `red`, `blue`, `gray`).
- Lorsqu'elles sont spécifiées, l'implémentation doit fournir un retour visuel via une sortie terminal colorée ou une représentation graphique.

### Connexions

- Syntaxe : `connection: <nom1>-<nom2> [métadonnées]`
- Définit une connexion **bidirectionnelle** entre deux zones.
- Les noms de zones **ne peuvent pas contenir de tirets**.
- Métadonnées optionnelles : `max_link_capacity=<nombre>` (défaut : 1) — Nombre maximum de drones pouvant traverser cette connexion simultanément.

> Les coordonnées des zones sont toujours des entiers. Il y a toujours une zone de départ unique et une zone d'arrivée unique.

---

## Partie obligatoire

L'objectif principal est de déplacer tous les drones de la zone de départ à la zone d'arrivée dans le **moins de tours de simulation possible**.

### Exigences du pathfinding et de l'algorithme

- Les drones peuvent se déplacer **simultanément**. L'algorithme doit planifier les chemins pour maximiser le débit et éviter les délais inutiles.
- Votre implémentation doit gérer :
  - La distribution des drones sur plusieurs chemins
  - L'attente stratégique lorsque le déplacement n'est pas possible
  - L'évitement des conflits de chemins et des blocages (deadlocks)
- L'algorithme doit prendre en compte :
  - Les longueurs de chemins, y compris les coûts de déplacement associés aux types de zones
  - La planification des tours, pour éviter que les drones ne se percutent ou ne se bloquent
  - La structure du graphe, pour déterminer les chemins disjoints ou superposés disponibles
  - Les contraintes de capacité des zones (`max_drones`) et des connexions (`max_link_capacity`)
- Votre algorithme doit être **adaptable** : différentes cartes peuvent nécessiter différentes stratégies de routage.
- La **représentation visuelle** est obligatoire : sortie terminal colorée, interface graphique, ou les deux.

### Règles d'occupation des zones

- Par défaut, une zone peut contenir **au plus un drone** à un tour de simulation donné.
- Les zones avec `max_drones=N` peuvent contenir jusqu'à N drones simultanément.
- **Exceptions spéciales :**
  - **Zone de départ :** tous les drones commencent ici et peuvent partager l'espace initialement.
  - **Zone d'arrivée :** plusieurs drones peuvent arriver et sont considérés comme livrés.
- Deux drones ne peuvent pas entrer dans la même zone au même tour sauf si la capacité de la zone le permet.
- La capacité de connexion (`max_link_capacity`) limite le nombre de drones pouvant traverser la même connexion simultanément.

### Mécanique des déplacements et des tours

À chaque tour, chaque drone peut :
- Se déplacer vers une zone adjacente connectée (si la capacité le permet).
- Se déplacer vers une connexion en direction d'une **zone restricted** (qui nécessite 2 tours). Le drone **DOIT** atteindre sa destination au tour suivant — il ne peut pas attendre sur la connexion.
- **Rester en place** (pour attendre, ou si le déplacement est bloqué).

Coûts de déplacement par type de zone :

| Type de zone | Coût |
|--------------|------|
| `normal` | 1 tour |
| `restricted` | 2 tours |
| `priority` | 1 tour (préféré) |
| `blocked` | Inaccessible |

**Règles importantes :**
- Les drones qui quittent une zone libèrent de la capacité **pour ce même tour**.
- Une zone doit avoir de la capacité disponible pour qu'un drone puisse y entrer, après que tous les drones sortants ont libéré de l'espace.
- Pour les déplacements multi-tours (zones restricted), le drone occupe la connexion pendant le transit et **ne peut pas attendre** sur la connexion.

### Contraintes du parser

- La première ligne doit définir `nb_drones: <entier_positif>`.
- Exactement un `start_hub:` et un `end_hub:`.
- Chaque zone doit avoir un nom unique et des coordonnées entières valides.
- Les noms de zones ne peuvent pas contenir de tirets ni d'espaces.
- Les connexions doivent lier uniquement des zones préalablement définies.
- La même connexion ne doit pas apparaître plus d'une fois (`a-b` et `b-a` sont des doublons).
- Les types de zones doivent être l'un des suivants : `normal`, `blocked`, `restricted`, `priority`. Les types invalides génèrent une erreur de parsing.
- Les valeurs de capacité doivent être des entiers positifs.
- Toute erreur de parsing doit arrêter le programme avec un message d'erreur clair indiquant la ligne et la cause.

### Format de sortie de la simulation

- Chaque tour de simulation est représenté par **une ligne**.
- Chaque ligne liste tous les déplacements de drones pour ce tour, **séparés par des espaces**.
- Format de déplacement : `D<ID>-<zone>` ou `D<ID>-<connexion>` (pour les drones en transit vers des zones restricted).
- Les drones qui ne se déplacent pas sont **omis** de cette ligne.
- Les drones qui atteignent la zone d'arrivée ne sont **plus suivis**.
- La simulation se termine quand tous les drones ont atteint la zone d'arrivée.

**Exemple de sortie :**
```
D1-roof1 D2-corridorA
D1-roof2 D2-tunnelB
D1-goal D2-goal
```

### Système de score

- La performance est évaluée par le **nombre total de tours de simulation**.
- Moins de tours = meilleur score.
- Une simulation valide doit :
  - Respecter toutes les règles de déplacement et d'occupation
  - Gérer correctement les coûts de déplacement
  - Respecter toutes les contraintes de capacité
  - Éviter tous les conflits

**Métriques secondaires** (optionnelles mais encouragées) :
- Drones déplacés par tour
- Nombre moyen de tours par drone
- Coût total du chemin

### Benchmarks de performance

| Carte | Drones | Cible |
|-------|--------|-------|
| **Facile** | | |
| Chemin linéaire | 2 | ≤ 6 tours |
| Fourche simple | 4 | ≤ 8 tours |
| Capacité basique | 4 | ≤ 6 tours |
| **Moyen** | | |
| Piège cul-de-sac | 5 | ≤ 12 tours |
| Boucle circulaire | 6 | ≤ 15 tours |
| Puzzle priorité | 5 | ≤ 12 tours |
| **Difficile** | | |
| Cauchemar labyrinthe | 8 | ≤ 30 tours |
| Enfer de capacité | 12 | ≤ 35 tours |
| Défi ultime | 15 | ≤ 45 tours |
| **Challenger (optionnel)** | | |
| Le rêve impossible | 25 | Référence : 45 tours |

---

## Exigences du README

Un fichier `README.md` doit être fourni à la racine de votre dépôt Git. Il doit inclure :

- La première ligne doit être en italique et indiquer : *Ce projet a été créé dans le cadre du cursus 42 par \<login\>.*
- Une section **Description** : objectif et aperçu du projet.
- Une section **Instructions** : informations sur la compilation, l'installation et/ou l'exécution.
- Une section **Ressources** : références (docs, articles, tutoriels) et description de l'utilisation de l'IA.
- Une **description détaillée de vos choix algorithmiques** et de votre stratégie d'implémentation.
- **Documentation des fonctionnalités de représentation visuelle** et comment elles améliorent l'expérience utilisateur.

> Le README doit être rédigé en **anglais**.

---

## Partie bonus

*(Évaluée uniquement si toutes les exigences obligatoires sont satisfaites)*

- **Performance exceptionnelle :** Atteindre ou battre tous les objectifs de référence en nombre de tours pour toutes les cartes fournies.
- **Carte Challenger :** Résoudre *Le rêve impossible* et battre le record de référence de 45 tours.

---

## Soumission et évaluation par les pairs

Soumettez dans votre dépôt Git. Placez tous les fichiers à la racine. Une simulation entièrement fonctionnelle doit inclure :

- Un **parser** pour le format de fichier d'entrée.
- Un **moteur de simulation** respectant les règles de déplacement et de zone.
- Un **algorithme de pathfinding** (ou plusieurs) capable de minimiser le nombre total de tours.
- Un **système de représentation visuelle** (couleurs dans le terminal et/ou interface graphique).
- Une **sortie terminal ou journal** qui respecte le format spécifié.

> Les cartes d'évaluation peuvent être différentes de celles fournies dans le sujet. Pendant l'évaluation, une légère modification du projet pourrait être demandée pour vérifier la compréhension réelle.
