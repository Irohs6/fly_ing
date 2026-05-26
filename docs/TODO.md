# TODO — Fly-in Project

## Structure du projet

```
fly_ing/
├── main.py                  # Point d'entrée principal
├── Makefile
├── README.md
├── .gitignore
├── requirements.txt
├── docs/
│   ├── subject_en.md
│   ├── subject_fr.md
│   └── TODO.md              (ce fichier)
├── src/
│   ├── parser.py            # Parsing du fichier de carte
│   ├── graph.py             # Structure de graphe (zones + connexions)
│   ├── drone.py             # Classe Drone
│   ├── simulation.py        # Moteur de simulation
│   ├── pathfinder.py        # Algorithme(s) de pathfinding
│   └── visualizer.py        # Représentation visuelle (terminal + graphique)
└── tests/
    ├── test_parser.py
    ├── test_graph.py
    ├── test_simulation.py
    └── test_pathfinder.py
```

---

## Checklist des tâches

### 1. Mise en place du projet
- [ ] Initialiser l'environnement virtuel (`venv`)
- [ ] Créer `requirements.txt` (ex : `pytest`, `mypy`, `flake8`, `colorama` ou autre lib de couleur terminal)
- [ ] Créer `.gitignore` (Python, venv, mypy/flake8 cache)
- [ ] Créer le `Makefile` avec les règles : `install`, `run`, `debug`, `clean`, `lint`, `lint-strict`
- [ ] Créer `README.md` conforme aux exigences du sujet

---

### 2. Parser (`src/parser.py`)
- [ ] Lire et valider la première ligne (`nb_drones`)
- [ ] Parser les zones : `start_hub`, `end_hub`, `hub`
  - [ ] Nom unique, coordonnées entières
  - [ ] Métadonnées optionnelles : `zone`, `color`, `max_drones`
  - [ ] Valider les types de zone : `normal`, `blocked`, `restricted`, `priority`
  - [ ] Valider que `max_drones` est un entier positif
- [ ] Parser les connexions : `connection: <zone1>-<zone2> [métadonnées]`
  - [ ] Vérifier que les zones référencées existent
  - [ ] Détecter les doublons (`a-b` == `b-a`)
  - [ ] Valider `max_link_capacity` (entier positif)
- [ ] Ignorer les commentaires (`#`)
- [ ] Gérer toutes les erreurs avec message clair (numéro de ligne + cause)
- [ ] Tester avec les fichiers fournis (easy, medium, hard, challenger)
- [ ] Créer des fichiers de carte personnalisés pour les cas limites

---

### 3. Structure de graphe (`src/graph.py`)
- [ ] Classe `Zone` avec attributs : nom, coordonnées, type, couleur, max_drones
- [ ] Classe `Connection` avec attributs : zone1, zone2, max_link_capacity
- [ ] Classe `Graph` :
  - [ ] Ajouter/récupérer des zones et connexions
  - [ ] Obtenir les voisins d'une zone
  - [ ] Vérifier si une zone est accessible (non bloquée)
  - [ ] Aucune bibliothèque de graphe externe (networkx, graphlib interdits)

---

### 4. Classe Drone (`src/drone.py`)
- [ ] Classe `Drone` avec attributs : id, zone courante, chemin planifié, état (en attente, en transit, arrivé)
- [ ] Gestion de l'état de transit pour les zones `restricted` (2 tours)
- [ ] Méthode pour avancer d'un tour selon le chemin planifié

---

### 5. Algorithme de pathfinding (`src/pathfinder.py`)
- [ ] Implémenter BFS ou Dijkstra **sans bibliothèque de graphe**
- [ ] Prendre en compte les coûts de déplacement par type de zone
  - [ ] `normal` = 1 tour
  - [ ] `restricted` = 2 tours
  - [ ] `priority` = 1 tour (priorisé)
  - [ ] `blocked` = inaccessible
- [ ] Trouver plusieurs chemins (chemins disjoints si possible)
- [ ] Distribuer les drones intelligemment sur les chemins disponibles
- [ ] Gérer les conflits de capacité (zones et connexions)
- [ ] Éviter les deadlocks
- [ ] Stratégie d'attente quand un chemin est bloqué

**Cibles de performance à atteindre :**
- Easy : ≤ 6 / 8 / 6 tours
- Medium : ≤ 12 / 15 / 12 tours
- Hard : ≤ 30 / 35 / 45 tours
- Challenger (bonus) : < 45 tours

---

### 6. Moteur de simulation (`src/simulation.py`)
- [ ] Boucle de simulation tour par tour
- [ ] À chaque tour :
  - [ ] Calculer les mouvements possibles pour chaque drone
  - [ ] Respecter les capacités de zones et de connexions
  - [ ] Libérer la capacité des zones de départ avant d'occuper les zones d'arrivée
  - [ ] Gérer le transit des drones sur les zones `restricted` (2 tours, pas d'attente sur la connexion)
  - [ ] Les drones arrivés ne sont plus trackés
- [ ] Générer la sortie au format attendu :
  ```
  D1-zone D2-zone ...
  ```
- [ ] Arrêter quand tous les drones sont arrivés

---

### 7. Représentation visuelle (`src/visualizer.py`)
- [ ] Sortie terminal colorée (utiliser `colorama` ou codes ANSI)
  - [ ] Afficher la position des drones à chaque tour
  - [ ] Utiliser les couleurs définies dans les métadonnées des zones
  - [ ] Distinguer visuellement les types de zones (restricted, priority, blocked)
- [ ] (Bonus) Interface graphique (ex : `pygame`, `tkinter`, `matplotlib`)
  - [ ] Afficher le graphe avec les zones et connexions
  - [ ] Animer les déplacements des drones tour par tour

---

### 8. Qualité du code
- [ ] Annotations de type complètes (toutes fonctions et variables)
- [ ] Docstrings sur toutes les classes et fonctions (PEP 257)
- [ ] Gestion des exceptions partout (pas de crash non géré)
- [ ] Passage de `flake8` sans erreur
- [ ] Passage de `mypy --warn-return-any --warn-unused-ignores --ignore-missing-imports --disallow-untyped-defs --check-untyped-defs` sans erreur
- [ ] Code 100% orienté objet (démontrable en peer review)

---

### 9. Tests (`tests/`)
- [ ] Tests unitaires du parser (cas valides + cas d'erreur)
- [ ] Tests unitaires du graphe
- [ ] Tests de l'algorithme de pathfinding sur les cartes fournies
- [ ] Tests du moteur de simulation
- [ ] Vérification des benchmarks sur toutes les cartes

---

### 10. README
- [ ] Première ligne italique avec login(s)
- [ ] Section Description
- [ ] Section Instructions (installation, exécution)
- [ ] Section Ressources (références + utilisation de l'IA)
- [ ] Description détaillée des choix algorithmiques
- [ ] Documentation de la représentation visuelle

---

## Cartes de test fournies

| Dossier | Fichier | Drones | Cible |
|---------|---------|--------|-------|
| easy | 01_linear_path.txt | 2 | ≤ 6 tours |
| easy | 02_simple_fork.txt | 4 | ≤ 8 tours |
| easy | 03_basic_capacity.txt | 4 | ≤ 6 tours |
| medium | 01_dead_end_trap.txt | 5 | ≤ 12 tours |
| medium | 02_circular_loop.txt | 6 | ≤ 15 tours |
| medium | 03_priority_puzzle.txt | 5 | ≤ 12 tours |
| hard | 01_maze_nightmare.txt | 8 | ≤ 30 tours |
| hard | 02_capacity_hell.txt | 12 | ≤ 35 tours |
| hard | 03_ultimate_challenge.txt | 15 | ≤ 45 tours |
| challenger | 01_the_impossible_dream.txt | 25 | < 45 tours (bonus) |

---

## Points critiques à ne pas oublier

- **Pas de `networkx`, `graphlib` ou autre lib de graphe.**
- Les noms de zones **ne peuvent pas contenir de tirets** (utilisés comme séparateur dans `connection:`).
- La zone de départ et la zone d'arrivée ont des règles d'occupation spéciales.
- Pour les zones `restricted` : le drone est "en connexion" pendant 1 tour, puis arrive obligatoirement au tour suivant — il ne peut **pas attendre** sur la connexion.
- Les drones qui quittent une zone libèrent leur place **dans le même tour** (pas le tour suivant).
- La simulation doit gérer les **deadlocks** (situation où aucun drone ne peut avancer).
