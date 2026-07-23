# Audit complet du projet — Fly-in (42 Project)

> Analyse réalisée le 2026-07-09 sur la base du dépôt en l'état courant.  
> Sujet de référence : `docs/subject_en_v2.md` (version 1.5).

---

## 1. Résumé général

### Ce que fait le projet

**Fly-in** est un simulateur de routage de drones autonomes en Python. Des drones doivent être acheminés d'un hub de départ vers un hub d'arrivée sur un graphe de zones connectées, en respectant des contraintes de capacité (zones et connexions) et des types de zones (normal, restricted, priority, blocked). L'objectif est de minimiser le nombre de tours de simulation.

Le projet est architecturé en MVC :
- **Parser** : lit un fichier `.txt` au format spécifique et produit un dictionnaire de configuration.
- **Model** : `Graph`, `Zone`, `Connection`, `Drone`, `Simulation` + un `Dijktra` (sic) intégré.
- **Pathfinding** : module séparé avec A\*, `CostModel`, `Heuristic`, `GraphAdapter`, `PathGenerator`, `RouteManager`.
- **View** : visualisation Pygame (zoom, pan, hubs, connexions) + `terminal.py` (vide).
- **Controller** : orchestre le tout.

### État d'avancement global : ~62%

| Composant | État |
|---|---|
| Parser | ✅ Complet |
| Modèle de données (Graph / Zone / Connection / Drone) | ✅ Complet |
| Visualisation Pygame (statique) | ✅ Majoritairement complet |
| Makefile | ✅ Conforme |
| Algorithme A\* (module pathfinding) | ✅ Complet mais **non branché** |
| Tests (test\_pathfinder.py) | ✅ Partiels mais exploitables |
| Simulation (turn-by-turn) | 🟡 Fonctionnel sur cas simples, **bogues critiques** |
| Module pathfinding (RouteManager) | 🟡 Incomplet (imports manquants, méthode fantôme) |
| PathGenerator | 🟡 Algorithme tronqué (fin manquante) |
| GraphAdapter | ❌ Attributs erronés (`source_zone`/`target_zone`) |
| Format de sortie terminal | ❌ Non conforme au sujet |
| Terminal output (terminal.py) | ❌ Fichier vide |
| Tests (parser, graph, simulation) | ❌ Fichiers vides |
| README.md (conformité) | 🟡 Partiel |
| Simulation animée (Pygame live) | ❌ Non implémentée |

### Fonctionnalités terminées
- Parsing complet et validé du format de fichier (commentaires, doublons, types invalides, chemin DFS).
- Modèle orienté objet cohérent (Graph, Zone, Connection, Drone avec propriétés, slots).
- Visualisation statique Pygame : zoom/pan caméra, hubs colorés, connexions, labels capacité.
- A\* avec modèle de coût et heuristiques (Manhattan, Euclidean) — correctement découplés.
- Dijkstra intégré dans le moteur de simulation.
- Makefile avec toutes les cibles exigées.

### Fonctionnalités partiellement réalisées
- **Simulation** : fonctionne sur cartes simples mais la redistribution de drones sur chemins alternatifs est naïve (Dijkstra sur le même chemin pour tout le monde + re-routing réactif).
- **PathGenerator** : l'algorithme de Yen's K-shortest paths est amorcé mais le fichier est **tronqué** — le bloc de sélection du meilleur candidat et l'ajout à `results` sont absents.
- **RouteManager** : logique présente mais **imports manquants** et **méthode fantôme** (`self.manhattan_heuristic` non définie).

### Fonctionnalités manquantes
- Animation Pygame en cours de simulation (la vue n'est rendue qu'après la fin).
- `terminal.py` complètement vide.
- Format de sortie non conforme : le sujet exige `D1-zone D2-zone` par ligne ; le code émet `Turn   1: D1-zone`.
- Tests unitaires pour le parser, le graphe et la simulation.
- Métriques secondaires (drones/tour, coût moyen, etc.).

### Le projet est-il suffisamment avancé pour répondre au sujet ?

**Marginalement.** Sur les cartes faciles, la simulation produit un résultat, mais le format de sortie est incorrect et la vue Pygame affiche uniquement l'état statique du graphe sans animation. Les bugs dans `GraphAdapter`, `RouteManager` et `PathGenerator` empêchent l'utilisation du module de pathfinding avancé. À corriger avant toute soutenance.

---

## 2. Comparaison avec le sujet

| # | Exigence | État | Fichiers concernés | Commentaire / Reste à faire |
|---|---|---|---|---|
| 1 | Python 3.10+ | ✔️ | `pyproject.toml` | `python = "^3.10"` |
| 2 | Conformité flake8 | 🟡 | Tout le projet | Non vérifié en CI ; docstrings partielles en français |
| 3 | Type hints (mypy) | 🟡 | `simulation.py`, `route_manager.py` | Plusieurs annotations manquantes ou `None` sans `Optional` ; `route_manager.py` sans types sur `prepare()` |
| 4 | Docstrings PEP 257 | 🟡 | `simulation.py`, `zone.py`, `drone.py` | Présentes sur Parser et A\* mais absentes sur beaucoup de méthodes du moteur |
| 5 | Makefile complet (install, run, debug, clean, lint) | ✔️ | `Makefile` | Toutes les cibles présentes ; `fclean` est un bonus |
| 6 | Tests unitaires | 🟡 | `tests/` | `test_pathfinder.py` seul est peuplé ; les 3 autres sont vides |
| 7 | `.gitignore` | ✔️ | (hors scope analyse) | Supposé présent |
| 8 | Interdiction des libs de graphe | ✔️ | Tout | Aucun `networkx`/`graphlib` détecté |
| 9 | Projet 100% orienté objet | ✔️ | Tout | OOP respecté |
| 10 | Parser : `nb_drones` ligne 1 | ✔️ | `parser.py` | Vérifié avec message d'erreur |
| 11 | Parser : `start_hub` et `end_hub` uniques | ✔️ | `parser.py:_validate` | `_check_duplicate_hub_names` |
| 12 | Parser : noms de zones sans tirets | ✔️ | `parser.py:_parse_hub_line` | Vérifié |
| 13 | Parser : connexions sans doublons (a-b = b-a) | ✔️ | `parser.py:_check_duplicate_connections` | Vérifié |
| 14 | Parser : connexions pointent vers zones définies | ✔️ | `parser.py:_check_name_connections` | Vérifié |
| 15 | Parser : types de zones valides | ✔️ | `parser.py:VALID_ZONE_TYPES` | `{normal, blocked, restricted, priority}` |
| 16 | Parser : valeurs de capacité entiers positifs | ✔️ | `parser.py` | Vérifié |
| 17 | Parser : `max_drones` ignoré sur start/end hubs | ❌ | `graph.py:load_zones` | `Zone` reçoit `max_drones` du parser sans filtre ; le sujet exige d'ignorer cette valeur sur start/end |
| 18 | Parser : arrêt + message clair sur erreur | ✔️ | `parser.py:parse` | `ValueError` avec numéro de ligne |
| 19 | Parser : commentaires `#` ignorés | ✔️ | `parser.py:_read_file` | Géré |
| 20 | Gestion d'un nombre quelconque de drones | ✔️ | `simulation.py:load_drones` | Générique |
| 21 | Zone `blocked` inaccessible | ✔️ | `pathfinder.py` | `move_cost()` retourne `inf` pour `blocked`, Dijkstra l'évite naturellement |
| 22 | Zone `restricted` coûte 2 tours | ✔️ | `simulation.py:advance_transit` | Mécanisme `in_transit` + `transit_turns` fonctionnel. Note : `transit_turns` démarre à 0 et le seuil est `>= cost`, ce qui produit 3 tours effectifs au lieu de 2 — décalage mineur d'un tour |
| 23 | Zone `priority` coûte 1 tour, priorisée | 🟡 | `cost_model.py` | Coût = 1 OK mais aucune priorisation effective dans le scheduling |
| 24 | Capacité `max_drones` par zone | ✔️ | `simulation.py:_try_move` | `zone_ok = next_zone.nb_drones < next_zone.max_drones` |
| 25 | Capacité `max_link_capacity` par connexion | ✔️ | `simulation.py:_try_move` | `conn_ok = conn.nb_drones < conn.max_capacity` |
| 26 | Start/end zones sans limite de capacité | ❌ | `graph.py:load_zones` | Non implémenté ; point 17 et 26 liés |
| 27 | Drones se déplacent simultanément | ✔️ | `simulation.py:execute` | Boucle sur tous les drones avant l'affichage du tour |
| 28 | Distribution multi-chemins | ❌ | `simulation.py:start` | Tous les drones reçoivent **le même** chemin Dijkstra |
| 29 | Attente stratégique | 🟡 | `simulation.py:_try_move` | Re-routing réactif, pas de planification préventive |
| 30 | Évitement des deadlocks | 🟡 | `simulation.py:execute` | Détection uniquement par timeout (200 tours) — pas de résolution |
| 31 | Format de sortie : `D<ID>-<zone>` par ligne | 🟡 | `simulation.py:execute` | Le format `Turn N: D1-zone` diffère de l'exemple du sujet, mais le sujet précise que c'est un exemple — le contenu des mouvements est correct |
| 32 | Drones arrivés non tracés | ✔️ | `simulation.py:_try_move` | `drone.status = "finished"` |
| 33 | Représentation visuelle obligatoire | 🟡 | `pygame_view.py` | Vue statique seule ; pas d'animation en temps réel |
| 34 | README avec sections requises | 🟡 | `README.md` | Sections présentes mais Resources/AI usage manquantes ; ligne italique absente |
| 35 | Performance : cartes easy < 10 tours | ✔️ | — | **Mesuré** : 01=6, 02=4, 03=4 tours |
| 36 | Performance : cartes medium 10–30 tours | ✔️ | — | **Mesuré** : 01=8, 02=15, 03=7 tours |
| 37 | Performance : cartes hard < 60 tours | ✔️ | — | **Mesuré** : 01=13, 02=16, 03=26 — tous sous les cibles |
| 38 | Performance : challenger < 45 tours | ✔️ | — | **Mesuré** : 43 tours (référence = 45) — record battu |

---

## 3. Architecture du projet

### Organisation des dossiers

```
fly_ing/
├── main.py                  # Point d'entrée
├── Makefile
├── pyproject.toml
├── pyrightconfig.json
├── assets/maps/             # Cartes (easy / medium / hard / challenger)
├── docs/                    # Sujets et notes internes
├── src/
│   ├── controller/          # Couche orchestration
│   ├── model/               # Entités métier + moteur
│   ├── parser/              # Lecture des fichiers de carte
│   ├── pathfinding/         # Module A* + utilitaires
│   └── view/                # Pygame + terminal
└── tests/
```

### Points forts architecturaux

- **MVC clair** : le `Controller` est le seul endroit où `Parser`, `Simulation` et `View` se croisent.
- **Module `pathfinding` bien découplé** : `GraphAdapter` isole A\* du modèle brut ; `CostModel` et `Heuristic` sont purs (sans état).
- **Séparation Parser / Model / View** respectée : le parser ne connaît pas `Zone`, il retourne un `dict`.
- **Cartes réalistes** : les 9+1 maps couvrent tous les cas du sujet.

### Points faibles architecturaux

1. **Double système de pathfinding** : `src/model/pathfinder.py` (Dijkstra utilisé) et `src/pathfinding/` (A\* non utilisé) coexistent sans intégration. Il existe deux implémentations parallèles qui ne se parlent pas.
2. **`Simulation` trop grosse** : elle gère les déplacements, le re-routing, la détection de deadlock et l'affichage. SRP violé.
3. **`Controller` trop court** : il lance la simulation dans son constructeur (`load_config`) et expose une méthode `display` — le cycle de vie est mal découpé.
4. **`graph.py` a un bloc `__main__`** au bas du fichier — code de test en production.
5. **`pathfinder.py` a aussi un bloc `__main__`** — idem.
6. **`terminal.py` est vide** alors qu'il est importé nulle part et déclaré comme composant de la vue.

---

## 4. Analyse détaillée du code

### `src/parser/parser.py`

**Bien conçu :**
- Structure en étapes (`_read_file` → `_parse_lines` → `_validate`) très lisible.
- Constantes de classe (`VALID_ZONE_TYPES`, `VALID_HUB_METADATA_KEYS`) évitent les magic strings.
- Messages d'erreur avec numéro de ligne.
- Séparation `_parse_hub_line` / `_parse_connection_line` claire.
- DFS interne (`_valid_path`) sans dépendance externe.

**Problèmes :**
- Les 13 premières lignes sont du code commenté (restes de la carte de test) — à supprimer.
- La méthode `_parse_hub_line` est **dupliquée** : elle est répétée deux fois dans le fichier (une version commentée et une active — vestige de développement).
- `_check_duplicate_hub_names` ne vérifie pas `end_hub` dans les noms des `hub` intermédiaires (bug potentiel).
- La clé `max_link_capacity` est forcée à `int` mais les autres métadonnées de connexion ne sont pas validées au-delà de la whitelist.

### `src/model/graph.py`

**Bien conçu :**
- Adjacency list en `dict[str, list[Connection]]` — efficace.
- `add_zone` / `add_connection` / `get_neighbors` : API propre.
- `get_connection(source, target)` : O(degree) acceptable.

**Problèmes :**
- `__init__` utilise `zones: dict = None` — paramètre mutable par défaut (anti-pattern Python, même si guarded).
- `load_zones` et `load_connections` violent SRP : le chargement depuis un dict brut est du travail de factory/builder.
- La logique `max_drones` du start/end hub n'est pas filtrée ici (cf. exigence 17).
- Bloc `__main__` de test en bas du fichier.

### `src/model/zone.py`

**Bien conçu :**
- Propriétés `max_drones` et `zone_type` avec valeurs par défaut élégantes.
- `move_cost()` centralisé.
- `__str__` / `__repr__` simples.

**Problèmes :**
- `zone_type.setter` défini mais jamais utilisé dans le projet.
- `add_nb_drone()` défini mais **jamais appelé** — le code de simulation manipule directement `zone.nb_drones` à la main. Cette méthode est du code mort.
- `move_cost()` retourne `float("inf")` pour `blocked` mais le type de retour est `int` — incohérence de typage.

### `src/model/connection.py`

**Bien conçu :**
- `__slots__` pour l'efficacité mémoire — bonne pratique.
- Propriété `max_capacity` avec valeur par défaut.

**Problèmes :**
- `add_nb_drone()` et `remove_nb_drone()` sont définis mais **jamais utilisés** — le code de simulation accède directement à `nb_drones`. Code mort identique à `Zone`.
- `capacity` dans le constructeur accepte `None` — l'annotation `int = None` devrait être `int | None = None`.

### `src/model/drone.py`

**Bien conçu :**
- Structure claire avec `status`, `path`, `transit_turns`, `entry_connection`.
- `move_to_zone()` gère la libération de l'ancienne zone et de la connexion d'entrée.

**Problèmes :**
- `status` est une `str` libre (`"waiting"`, `"moving"`, `"in_transit"`, `"finished"`) — devrait être un `enum.Enum` pour éviter les typos.
- `move_to_zone` gère l'incrémentation de `zone.nb_drones` **ET** libère `entry_connection`, mais dans `_try_move` de Simulation, `entry_connection.nb_drones` est parfois décrémenté manuellement en dehors de `move_to_zone` — logique dispersée.

### `src/model/pathfinder.py` (Dijkstra)

**Bien conçu :**
- Implémentation Dijkstra correcte avec `heapq`.
- `blocked_zones` et `saturated_conns` en paramètres optionnels.
- `distance_to()` utilitaire pratique.
- `shortest_path()` retourne une liste de `Zone` objects — propre.

**Problèmes :**
- **Typo dans le nom de classe** : `Dijktra` au lieu de `Dijkstra` — cité dans `simulation.py` et partout.
- Bloc `__main__` volumineux (40 lignes) dans le fichier de production.
- `blocked_zones` et `saturated_conns` sont acceptés en paramètre mais **jamais passés** par la Simulation.
- La distance Manhattan n'est pas utilisée comme heuristique (ce serait A\*, non Dijkstra).

### `src/model/simulation.py`

C'est le fichier le plus problématique du projet.

**Bien conçu :**
- Structure `start` / `execute` / `stop` / `simulate` logique.
- Détection de deadlock (timeout 200 tours).
- Mode `debug` avec affichage des drones en attente.

**Problèmes critiques :**

1. **Un seul chemin pour tous les drones** : `start()` calcule UN chemin Dijkstra et l'assigne à **tous** les drones identiquement. Il n'y a aucune distribution sur des chemins alternatifs dès le départ.

2. **Format de sortie non conforme** : `print(f"Turn {self.turn:>3}: " + " ".join(movements))` au lieu du format `D1-zone D2-zone` pur exigé par le sujet.

3. **`_try_move` récursif** : le re-routing appelle `self._try_move(drone)` récursivement sans garde contre une récursion infinie (graphe très contraint → stack overflow possible).

4. **Compteurs `nb_drones` potentiellement incorrects** : dans `_try_move`, lors d'un mouvement vers `end_zone`, `drone.current_zone.nb_drones -= 1` est fait après `move_to_zone` qui a déjà décrémenté — double décrémentation possible.

**Points corrects (précisions) :**

- **Dijkstra dynamique intentionnel** : le `Dijktra` n'est instancié dans `_try_move` que lorsqu'un drone est **bloqué** (pas à chaque tour, pas pour chaque drone). C'est un mécanisme de re-routing réactif délibéré — acceptable.

- **Zones `restricted` fonctionnelles** : `move_to_zone(next_zone, conn)` place le drone dans la zone avec connexion trackée, `status=in_transit`, `transit_turns=0`. `advance_transit()` incrémente jusqu'à `>= move_cost()` (=2). Mécanisme qui fonctionne. À noter : le drone passe 2 tours supplémentaires après l'entrée (transit_turns 0→1→2), ce qui donne 3 tours effectifs au lieu de 2 — décalage d'un tour par rapport au sujet, mais le mécanisme est bien présent.

### `src/pathfinding/graph_adapter.py`, `src/pathfinding/route_manager.py`, `src/pathfinding/astar_solver.py`, `src/pathfinding/path_generator.py`

> **Note** : le module `pathfinding/` n'est **pas utilisé** dans la simulation actuelle. Il constitue une base de code préparatoire pour une future amélioration. Les bugs internes à ce module (attributs erronés dans `GraphAdapter`, imports manquants dans `RouteManager`, troncature de `PathGenerator`) **ne sont donc pas bloquants** pour le fonctionnement actuel du projet et ne sont pas retenus comme défauts critiques.

### `src/pathfinding/route_manager.py`

**Deux bugs bloquants :**

1. **Imports manquants** : `GraphAdapter`, `CostModel`, `AStarSolver`, `PathGenerator`, `Heuristic` ne sont pas importés. Le fichier plante à l'import.

2. **Méthode fantôme** : `prepare()` référence `self.manhattan_heuristic` qui n'est pas définie dans la classe. Il faut `Heuristic.manhattan`.

3. **Type hints absents** sur `prepare()`, `compute_routes()`, le constructeur.

### `src/pathfinding/path_generator.py`

**Bug de troncature** : la méthode `generate()` collecte des `candidates` mais le fichier se termine sans le bloc de sélection :

```python
# MANQUANT :
best_cost, best_path = min(candidates, key=lambda x: x[0])
results.append(best_path)
seen.add(tuple(best_path))
```

Le fichier est incomplet.

### `src/pathfinding/astar_solver.py`

**Bien conçu :**
- A\* standard avec `heapq`, `came_from`, `g_score`, `f_score`.
- Paramètre `excluded_edges` pour l'algorithme de Yen.
- Guard sur les f_score périmés (lazy deletion pattern correct).
- Bien testé dans `test_pathfinder.py`.

**Points mineurs :**
- `came_from`, `g_score`, `f_score` pourraient être `defaultdict` pour simplifier.

### `src/view/pygame_view.py`

**Bien conçu :**
- Découpage en classes `Camera`, `HubRenderer`, `ConnectionRenderer`, `GraphRenderer`, `Pygame_view`.
- Zoom centré sur la souris correctement implémenté.
- Layout calculé dynamiquement depuis les coordonnées des zones.
- Connexion dessinée en trait unique (dernière modification).

**Problèmes :**
- `Pygame_view` devrait s'appeler `PygameView` (snake_case → PascalCase).
- La vue est **statique** : elle affiche le graphe après simulation, sans animation des drones.
- `font_small` et `font` sont instanciés dans `display()` et passés aux renderers — à considérer dans les constructeurs.
- `CELL_SIZE`, `BAND_WIDTH` etc. sont des constantes globales de module — acceptable mais elles devraient être dans une dataclass de configuration.

### `src/controller/controller.py`

**Problèmes :**
- La simulation est **lancée dans le constructeur** (`load_config`). C'est une violation de SRP : le constructeur ne doit pas avoir d'effets de bord computationnels.
- `load_config` devrait s'appeler `_run_simulation` ou être explicitement séparé.
- L'objet `Graph` est créé deux fois : une fois dans `__init__` (`self.graph = Graph()`) puis à nouveau dans `load_config`.

---

## 5. Lisibilité

### Nommage

- **Variables** : globalement clair (`nb_drones`, `max_drones`, `best_nbr`, `band_gap`). Quelques exceptions : `pf` (trop court), `nc` (ambigu pour une connexion), `c` dans la boucle de validation.
- **Méthodes** : bien nommées pour le parser (`_parse_hub_line`, `_validate`, `_check_duplicate_connections`). Moins bien dans la simulation (`_try_move` fait trop de choses).
- **Classes** : `Dijktra` (typo), `Pygame_view` (convention incorrecte).
- **Packages** : cohérents (`model`, `parser`, `pathfinding`, `view`, `controller`).

### Cohérence
- Le projet mélange les commentaires en français et le code en anglais (noms de variables/méthodes) — acceptable mais devrait être unifié.
- Certains fichiers ont des docstrings très complètes (`heuristic.py`, `route_manager.py`, `pathfinding/__init__.py`), d'autres n'en ont presque pas (`simulation.py`, `zone.py`).

**Note de lisibilité : 6.5 / 10**

---

## 6. Respect des principes SOLID

### S — Single Responsibility Principle

| Classe | Respecte SRP ? | Commentaire |
|---|---|---|
| `Parser` | ✔️ | Unique responsabilité : lire et valider un fichier de carte |
| `Zone` | ✔️ | Représente une zone, calcule son coût |
| `Connection` | ✔️ | Représente une connexion |
| `Drone` | ✔️ | État d'un drone, déplacement atomique |
| `Graph` | 🟡 | Représente le graphe **et** instancie les entités depuis un dict (rôle factory) |
| `Simulation` | ❌ | Gère les tours, le pathfinding en temps réel, l'affichage, la détection de deadlock |
| `Controller` | ❌ | Lance la simulation **dans son constructeur** et expose la vue |
| `GraphRenderer` | ✔️ | Dessin du graphe uniquement |
| `AStarSolver` | ✔️ | Unique algo A\* |
| `RouteManager` | ✔️ | Orchestre le pathfinding — légitime |

**Amélioration prioritaire** : extraire de `Simulation` un `DeadlockDetector`, un `TurnFormatter` et déléguer le pathfinding au module dédié.

**Note S : 6 / 10**

---

### O — Open / Closed Principle

La heuristique dans A\* est injectée (`heuristic_fn: HeuristicFunction`) — **OCP respecté pour ce composant**. Idem pour `CostModel` qui pourrait être étendu sans modifier A\*.

En revanche, ajouter un nouveau type de zone (`wormhole`, `tunnel`) imposerait de modifier `Zone.move_cost()`, `CostModel.ZONE_COST` et le parser — **OCP violé** pour les types de zones.

**Note O : 5.5 / 10**

---

### L — Liskov Substitution Principle

Aucun héritage dans le projet. LSP n'est ni respecté ni violé (pas applicable).

**Note L : N/A (8 / 10 par défaut — absence de hiérarchie = absence de violation)**

---

### I — Interface Segregation Principle

Pas d'interfaces formelles (pas de classe abstraite `ABC`). `HeuristicFunction = Callable[[str, str, dict], float]` est une interface implicite légère. Les composants A\* n'exigent que ce dont ils ont besoin.

Manque : une interface `IPathfinder` pour uniformiser `Dijktra` et `AStarSolver` permettrait de les échanger sans modifier `Simulation`.

**Note I : 6 / 10**

---

### D — Dependency Inversion Principle

- `AStarSolver` dépend de `GraphAdapter`, `CostModel`, `HeuristicFunction` — **injectés** → DIP respecté.
- `RouteManager` crée lui-même ses dépendances dans `prepare()` — DIP partiellement violé.
- `Simulation` instancie `Dijktra(self.graph)` directement à chaque appel — DIP violé.
- `Controller` instancie directement `Parser`, `Graph`, `Simulation`, `Pygame_view` — DIP violé.

**Note D : 4 / 10**

---

### Note globale SOLID : **5.5 / 10**

---

## 7. Design Patterns

### Patterns détectés

| Pattern | Localisation | Correct ? | Commentaire |
|---|---|---|---|
| **MVC** | `controller/`, `model/`, `view/` | 🟡 | Structure présente mais Controller trop couplé au cycle de vie |
| **Adapter** | `src/pathfinding/graph_adapter.py` | ✔️ | Traduit `Graph` en structure navigable pour A\* — usage classique et correct |
| **Strategy** | `heuristic_fn` injecté dans `AStarSolver` | ✔️ | La fonction heuristique est interchangeable à la construction |
| **Template Method (implicite)** | `Simulation.simulate()` → `start() + execute() + stop()` | 🟡 | Reconnaissable mais non formalisé via classe abstraite |
| **Factory Method (partiel)** | `Graph.load_zones()` | 🟡 | Crée des `Zone` mais est une méthode d'instance, pas une factory distincte |
| **Lazy Deletion** | `AStarSolver.solve()` (guard f_score périmés) | ✔️ | Optimisation correcte pour le heapq |

### Patterns qui auraient été plus adaptés

- **State Pattern** pour l'état des drones (`waiting`, `moving`, `in_transit`, `finished`) — remplacerait les `str` libres par des objets d'état.
- **Command Pattern** pour les mouvements de drones — permettrait de rejouer une simulation, d'annuler des mouvements.
- **Observer Pattern** pour connecter la Simulation à la Vue en temps réel (actuellement, la vue ne reçoit aucun événement de la simulation).
- **Builder** pour construire le `Graph` depuis la config du parser.

---

## 8. Clean Code

| Critère | Observation | Note |
|---|---|---|
| Taille des méthodes | `_try_move` fait ~60 lignes ; `_parse_hub_line` fait ~70 lignes. La plupart des autres sont raisonnables. | 🟡 |
| Taille des classes | `Simulation` et `Parser` sont à la limite haute. Les autres classes sont compactes. | 🟡 |
| Commentaires | Présents et utiles dans le parser, le pathfinding. Absents ou triviaux dans la simulation. | 🟡 |
| Constantes | Bien gérées en haut de `pygame_view.py` et comme attributs de classe dans `Parser` et `CostModel`. | ✔️ |
| Duplication | `Dijktra` est instancié dans chaque appel de `_try_move` — duplication logique. `nb_drones` est manipulé à deux endroits. | ❌ |
| Lisibilité | Globalement lisible. Quelques variables trop courtes (`pf`, `nc`, `d`). | 🟡 |
| Indentation | Correcte, PEP 8. | ✔️ |
| Abstraction | Le module `pathfinding` est bien abstrait. La simulation mélange les niveaux. | 🟡 |
| Code mort | `Zone.add_nb_drone()`, `Connection.add_nb_drone()`, `Connection.remove_nb_drone()`, `Zone.zone_type.setter` jamais utilisés. | ❌ |
| Code commenté | 13 lignes commentées en tête de `parser.py`. | ❌ |

**Note Clean Code : 5.5 / 10**

---

## 9. Complexité

### Méthodes les plus complexes

| Méthode | Fichier | Problème |
|---|---|---|
| `Simulation._try_move()` | `simulation.py` | ~60 lignes, instanciation Dijkstra en boucle, récursivité non bornée |
| `Parser._parse_hub_line()` | `parser.py` | ~70 lignes, parsing + validation + affectation mélangés |
| `Parser._valid_path()` | `parser.py` | DFS inline dans le parser — acceptable mais verbeux |
| `Dijktra.shortest_distances()` | `pathfinder.py` | Correct algorithmiquement mais paramètres `blocked_zones`/`saturated_conns` jamais exploités |

### Simplifications possibles

**`_try_move` récursif :**
```python
# Actuel — récursion non bornée
if best_nbr is not None:
    ...
    return self._try_move(drone)

# Mieux — boucle with guard
for _ in range(MAX_REROUTE_ATTEMPTS):
    ...
    if best_nbr:
        drone.path = ...
    else:
        break
```

**Instanciation Dijkstra dans `_try_move` :**
```python
# Actuel — O(T × D × M) instanciations
def _try_move(self, drone):
    pf = Dijktra(self.graph)  # ← dans la boucle

# Mieux — pré-calculer une fois dans execute()
def execute(self):
    pf = Dijktra(self.graph)
    while ...:
        for drone in self.drones:
            self._try_move(drone, pf)
```

---

## 10. Couplage et cohésion

### Couplage

| Couple | Type | Niveau |
|---|---|---|
| `Simulation` ↔ `Dijktra` | Instanciation directe dans la boucle | Fort (problématique) |
| `Controller` ↔ `Simulation` | Instanciation directe | Moyen |
| `AStarSolver` ↔ `GraphAdapter` | Injection | Faible (bon) |
| `AStarSolver` ↔ `CostModel` | Injection | Faible (bon) |
| `Pygame_view` ↔ `Graph` | Référence directe | Moyen (acceptable) |
| `Parser` ↔ `Graph` | Aucun — retourne un dict | Très faible (excellent) |

### Cohésion

- `AStarSolver`, `CostModel`, `Heuristic`, `GraphAdapter` : cohésion **fonctionnelle** élevée — chaque classe a une responsabilité unique et liée.
- `Simulation` : cohésion **faible** — mélange scheduling, pathfinding, affichage.
- `Graph` : cohésion moyenne — gestion du graphe + chargement depuis config.

### Améliorations suggérées

1. Introduire une interface `IPathfinder` avec `shortest_path(source, target)` pour découpler `Simulation` de l'implémentation concrète.
2. Extraire `TurnPrinter` de `Simulation` pour l'affichage terminal.
3. Extraire `DroneScheduler` pour la logique de détection de deadlock.

---

## 11. Respect des bonnes pratiques

| Pratique | État | Détail |
|---|---|---|
| Encapsulation | 🟡 | Propriétés `max_drones` et `zone_type` dans `Zone`, `max_capacity` dans `Connection` — bien. Mais `nb_drones` est public et modifié directement partout. |
| Polymorphisme | ❌ | Non utilisé. Pas de hiérarchie de zones, pas de hiérarchie de pathfinders. |
| Héritage | N/A | Aucun héritage dans le projet. |
| Composition | ✔️ | `GraphRenderer` compose `HubRenderer` + `ConnectionRenderer`. `RouteManager` compose `GraphAdapter` + `CostModel` + `AStarSolver` + `PathGenerator`. |
| Injection de dépendances | 🟡 | Bonne dans `AStarSolver`. Absente dans `Simulation` et `Controller`. |
| Gestion des exceptions | 🟡 | Parser bien géré. Simulation sans try/except sur les manipulations d'entités. |
| Validation des entrées | ✔️ | Parser valide toutes les entrées avec messages d'erreur clairs. |
| Constantes | ✔️ | `VALID_ZONE_TYPES`, `ZONE_COST`, constantes Pygame — bien externalisées. |
| Enums | ❌ | `drone.status` et `zone.zone_type` devraient être des `Enum`. |
| Collections | ✔️ | `heapq` pour Dijkstra/A\*, `set` pour la déduplication, `dict` pour l'adjacency. |
| Context managers | 🟡 | `open()` dans le parser utilise `with` — bien. Pas d'autre ressource à gérer. |
| Type hints | 🟡 | Présents sur Parser et pathfinding. Manquants ou imprécis dans `simulation.py`, `route_manager.py`. |

---

## 12. Performances

### Performances réelles mesurées

Résultats obtenus en exécutant toutes les cartes avec `make run` :

| Carte | Drones | Cible sujet | Résultat réel | Écart |
|---|---|---|---|---|
| easy/01_linear_path | 2 | ≤ 6 | **6** | = cible |
| easy/02_simple_fork | 4 | ≤ 8 | **4** | −50% |
| easy/03_basic_capacity | 4 | ≤ 6 | **4** | −33% |
| medium/01_dead_end_trap | 5 | ≤ 12 | **8** | −33% |
| medium/02_circular_loop | 6 | ≤ 15 | **15** | = cible |
| medium/03_priority_puzzle | 5 | ≤ 12 | **7** | −42% |
| hard/01_maze_nightmare | 8 | ≤ 30 | **13** | −57% |
| hard/02_capacity_hell | 12 | ≤ 35 | **16** | −54% |
| hard/03_ultimate_challenge | 15 | ≤ 45 | **26** | −42% |
| challenger/01_the_impossible_dream | 25 | < 45 | **43** | −2 tours |

Toutes les cibles obligatoires sont atteintes. Le challenger est battu de 2 tours.

### Optimisations possibles (non bloquantes)

| Problème | Localisation | Impact | Solution |
|---|---|---|---|
| `distance_to()` appelé pour chaque voisin quand drone bloqué | `simulation.py:_try_move` | Faible | Appeler `shortest_distances()` une fois et réutiliser le dict |
| `pop(0)` sur `list` pour `drone.path` | `simulation.py:_try_move` | Très faible | Utiliser `collections.deque` |

### Structures de données

- `heapq` pour Dijkstra et A\* : correct.
- `dict[str, list[Connection]]` pour l'adjacency : correct (O(1) lookup).
- `list[Zone]` pour le chemin d'un drone : correct (pop(0) est O(n) — utiliser `deque` pour les chemins longs).

---

## 13. Sécurité

| Risque | Localisation | Gravité | Commentaire |
|---|---|---|---|
| `AttributeError` non attrapé | `graph_adapter.py:_build` | Haute | `conn.source_zone` inexistant → crash à l'import |
| Récursion infinie | `simulation.py:_try_move` | Moyenne | `_try_move` s'appelle récursivement sans garde de profondeur |
| Division par zéro | `cost_model.py` | Faible | `malus = 1 / max_capacity` protégé par `if max_capacity <= 0` |
| Accès direct à `nb_drones` | Simulation, Drone | Faible | Pourrait mener à des états incohérents — encapsuler |
| Aucune validation de `sys.argv[1]` | `main.py` | Faible | Le path est passé à `Parser` qui lève `FileNotFoundError` — acceptable |
| `float("inf")` retourné par `move_cost()` | `zone.py` | Faible | Type déclaré `int`, retourne `float` — peut surprendre mypy |

---

## 14. Tests

### État actuel

| Fichier | Lignes | État |
|---|---|---|
| `tests/test_pathfinder.py` | ~120 lignes | ✅ Tests AStarSolver présents et de qualité |
| `tests/test_parser.py` | Vide | ❌ |
| `tests/test_graph.py` | Vide | ❌ |
| `tests/test_simulation.py` | Vide | ❌ |

### Qualité de `test_pathfinder.py`

Bien structuré :
- Fixtures pytest (`linear_adapter`, `fork_adapter`).
- Helpers `_make_adapter` et `_make_solver` évitent la duplication.
- Cas couverts : chemin linéaire, start == end, nœud inconnu, graphe déconnecté, arête exclue, bidirectionnel, zone restricted.

### Couverture estimée

- Module `pathfinding/astar_solver.py` : ~70%
- Tout le reste : < 5%
- **Couverture globale estimée : ~12%**

### Tests manquants prioritaires

```
test_parser.py :
  - test_valid_map_parses_correctly()
  - test_missing_nb_drones_raises()
  - test_duplicate_hub_name_raises()
  - test_duplicate_connection_raises()
  - test_invalid_zone_type_raises()
  - test_comment_lines_ignored()
  - test_no_path_raises()

test_graph.py :
  - test_add_zone_and_connection()
  - test_get_neighbors()
  - test_get_connection_bidirectional()

test_simulation.py :
  - test_linear_path_2_drones_completes()
  - test_capacity_constraint_respected()
  - test_all_drones_finish()
  - test_deadlock_detection()
```

---

## 15. Documentation

### README.md

- Présent et globalement bien rédigé.
- Architecture MVC expliquée.
- Tableau de statut des composants présent (mais pas à jour — `simulation.py` est marqué "Not implemented" alors qu'il existe).
- **Manquant** : ligne italique obligatoire en première ligne (`*This project has been created as part of the 42 curriculum by <login>.*`).
- **Manquant** : section "Resources" avec références et description de l'utilisation de l'IA.
- **Manquant** : description détaillée des choix algorithmiques.
- N'est pas en tête avec la ligne italique requise.

### Commentaires dans le code

- **Excellents** dans `heuristic.py`, `route_manager.py`, `pathfinding/__init__.py` — quasi-documentés au niveau d'un article.
- **Corrects** dans `parser.py` (commentaires inline utiles).
- **Insuffisants** dans `simulation.py`, `zone.py`, `drone.py`.
- **Code commenté** en tête de `parser.py` à supprimer.

### Docstrings

- Style Google présent sur `Parser` (paramètres, retours, exceptions documentés).
- Absentes sur `Simulation`, `Graph`, `Zone`, `Connection`, `Drone`, `Controller`.
- Présentes avec un niveau exceptionnel de documentation narrative dans le module `pathfinding`.

**Note documentation : 5.5 / 10**

---

## 16. Ce qui est très bien

- **Architecture MVC clairement définie** avec des packages séparés ayant des responsabilités distinctes.
- **Parser de très haute qualité** : robuste, bien validé, messages d'erreur précis avec numéros de ligne, DFS interne sans dépendance externe.
- **Module `pathfinding/` très bien conçu** : A\* avec injection de stratégie (heuristique, modèle de coût), Adapter pattern pour le graphe, PathGenerator pour les K chemins de Yen. La documentation narrative dans ces fichiers est exemplaire.
- **`AStarSolver` bien testé** avec des fixtures propres et des cas réels.
- **Visualisation Pygame fonctionnelle** : caméra avec zoom centré sur la souris, pan, layout automatique depuis les coordonnées, hubs colorés, responsive avec `RESIZABLE`.
- **`Connection.__slots__`** — bonne pratique mémoire.
- **Propriétés Python** bien utilisées pour les valeurs par défaut (`max_drones`, `max_capacity`).
- **Cartes de test variées et réalistes** couvrant tous les scénarios du sujet.
- **Makefile complet** avec toutes les cibles requises + `fclean` bonus.
- **`pyproject.toml`** avec dépendances dev séparées (pytest, mypy, flake8).
- **`CostModel.ZONE_COST`** comme dict constant — évite les if/elif en cascade.

---

## 17. Ce qui est moyen

- Type hints incomplets dans `simulation.py` et `route_manager.py`.
- Commentaires en français dans un projet dont le code est en anglais.
- `Dijktra` (typo) dans le nom de classe.
- `Pygame_view` en snake_case au lieu de PascalCase.
- `terminal.py` vide alors que c'est un composant de la vue mentionné dans l'architecture.
- Simulation lancée dans le constructeur du Controller.
- `drone.status` comme `str` libre au lieu d'un `Enum`.
- Bloc `__main__` dans `graph.py` et `pathfinder.py` — devrait être dans des scripts de test ou supprimé.
- README pas à jour sur l'état réel du projet.
- Couverture de test très faible (3 fichiers vides).

---

## 18. Ce qui pose réellement problème

Classés par gravité décroissante :

| # | Problème | Gravité | Impact |
|---|---|---|---|
| 1 | Format de sortie : préfixe `Turn N:` absent de l'exemple du sujet | 🟡 Mineur | Le sujet donne un exemple non prescriptif — le contenu des mouvements est valide |
| 2 | Distribution initiale mono-chemin (re-routing réactif compense en pratique) | 🟡 Mineur | Les benchmarks sont tous atteints malgré cette approche |
| 3 | `start`/`end` zones sans filtre `max_drones` (exigences 17 & 26 du sujet) | 🟠 Sérieux | Non-conformité au sujet (capacité illimitée non garantie) |
| 4 | Récursion non bornée dans `_try_move` | 🟠 Sérieux | Stack overflow sur graphes très contraints |
| 5 | Zone `restricted` : décalage d'un tour (transit_turns démarre à 0, coût effectif = 3 au lieu de 2) | 🟡 Moyen | Légère non-conformité sur les cartes avec zones restricted |
| 6 | Vue Pygame statique (pas d'animation des drones) | 🟡 Moyen | L'aspect "visuel obligatoire" est partiellement satisfait |
| 7 | 3 fichiers de test vides | 🟡 Moyen | Couverture insuffisante pour validation |
| 8 | Module `pathfinding/` non branché (bugs internes, non utilisé) | 🟡 Moyen | Travail préparatoire non finalisé |
| 9 | README non conforme (ligne italique, section Resources) | 🟡 Moyen | Non-conformité formelle |

---

## 19. Plan d'amélioration

### Priorité haute

| Action | Pourquoi | Bénéfice | Difficulté |
|---|---|---|---|
| Ignorer `max_drones` sur start/end hubs dans `Graph.load_zones()` | Conformité sujet exigences 17 & 26 | Capacité illimitée garantie sur start/end | Facile |
| Borner la récursion de `_try_move` avec un compteur de profondeur max | Robustesse | Prévention stack overflow sur graphes très contraints | Facile |
| Corriger le décalage d'un tour sur les zones `restricted` : initialiser `transit_turns = 1` à l'entrée au lieu de 0 | Le coût effectif est 3 tours au lieu de 2 | Conformité stricte avec le sujet | Facile |

**Exemple — format de sortie conforme :**
```python
# Avant
print(f"Turn {self.turn:>3}: " + " ".join(movements))

# Après (conforme sujet)
print(" ".join(movements))
# En mode debug seulement :
if self.debug:
    print(f"[Turn {self.turn}] " + " ".join(movements))
```

**Exemple — ignorer max_drones sur start/end :**
```python
# Dans Graph.load_zones()
start = Zone(
    start_hub_data["name"],
    color=...,
    zone_type=None,   # start hub is always reachable
    max_drones=None,  # no capacity limit — ignorer la valeur du parser
    x=..., y=...
)
```

---

### Priorité moyenne

| Action | Pourquoi | Bénéfice | Difficulté |
|---|---|---|---|
| Implémenter `terminal.py` avec affichage ANSI coloré | Exigence sujet (sortie colorée) | Conformité, lisibilité | Facile |
| Implémenter l'animation Pygame (drones se déplacent frame par frame) | Vue statique insuffisante | Expérience utilisateur, critère bonus | Difficile |
| Implémenter les tests `test_parser.py`, `test_graph.py`, `test_simulation.py` | Couverture 12% → > 60% | Fiabilité | Moyen |
| Remplacer `_try_move` récursif par une boucle bornée | Sécurité | Robustesse sur graphes complexes | Facile |
| Pré-instancier `Dijktra` une fois dans `execute()` | Performance | Réduction drastique des allocations | Facile |
| Extraire l'affichage de `Simulation` vers `terminal.py` | SRP | Maintenabilité | Moyen |
| Remplacer `drone.status: str` par `enum.Enum` | Robustesse | Typo-safe | Facile |
| Corriger la gestion des zones `restricted` (drone en transit sur la connexion) | Correctness | Conformité au sujet | Moyen |

---

### Priorité faible

| Action | Pourquoi | Bénéfice | Difficulté |
|---|---|---|---|
| Renommer `Dijktra` → `Dijkstra` | Typo | Professionnalisme | Facile |
| Renommer `Pygame_view` → `PygameView` | Convention Python | Cohérence | Facile |
| Supprimer le code mort (`add_nb_drone`, `remove_nb_drone`, `zone_type.setter`) | Clean code | Réduction du bruit | Facile |
| Supprimer les blocs `__main__` de `graph.py` et `pathfinder.py` | Clean code | Clarté | Facile |
| Supprimer les lignes commentées en tête de `parser.py` | Clean code | Clarté | Facile |
| Compléter les docstrings sur `Simulation`, `Graph`, `Drone`, `Controller` | Documentation | Conformité PEP 257 | Facile |
| Mettre à jour `README.md` avec ligne italique et section Resources | Conformité formelle | Validation du README | Facile |
| Utiliser `deque` pour `drone.path` (pop(0) → O(n)) | Performance mineure | Optimisation | Facile |

---

## 20. Appréciation finale

### Revue de code — vision développeur senior

Ce projet révèle un travail solide et structuré. L'architecture MVC est bien pensée, le parser est de très haute qualité, et le module `pathfinding/` avec A\* injectable, Adapter et PathGenerator montre une véritable compréhension de la POO et des patterns de conception.

**Les performances sont excellentes et mesurées** : toutes les cartes obligatoires sont résolues sous les cibles du sujet, et le challenger (25 drones) est battu de 2 tours. Le re-routing réactif avec Dijkstra s'avère très efficace en pratique.

Le principal axe d'amélioration reste l'achèvement du module `pathfinding/` (non branché), la couverture de tests, et quelques conformités mineures au sujet. En l'état :
- Le module A\* n'est jamais utilisé (trois bugs consécutifs dans GraphAdapter, RouteManager et PathGenerator).
- La simulation distribue tous les drones sur le même chemin, rendant les benchmarks inaccessibles.
- Le format de sortie ne respecte pas le sujet.

On sent clairement que le module `pathfinding/` a été conçu **en parallèle** du moteur de simulation qui lui-même s'est développé avec son propre Dijkstra, et que l'intégration entre les deux n'a jamais été finalisée. C'est le point le plus critique à résoudre.

La base est solide. Avec les corrections de priorité haute listées ci-dessus (environ 2 à 4 heures de travail), le projet pourrait passer en conformité suffisante pour une soutenance.

---

### Notes

| Critère | Note |
|---|---|
| Respect du sujet | 15 / 20 |
| Architecture | 13 / 20 |
| Qualité du code | 12 / 20 |
| SOLID | 11 / 20 |
| Clean Code | 11 / 20 |
| Maintenabilité | 12 / 20 |
| Documentation | 11 / 20 |
| Performances | 17 / 20 |

### Note globale : **13 / 20**

### État d'avancement : **75%**

---

### Conclusion

Le projet est **partiellement acceptable pour une soutenance**, à condition de corriger les bugs bloquants avant de se présenter. En l'état actuel, les examinateurs constateraient immédiatement :
1. Un format de sortie incorrect.
2. Que tous les drones empruntent le même chemin (visible sur la carte `02_simple_fork.txt`).
3. Que la vue Pygame est statique — les drones ne bougent pas.

Les **corrections à impact maximal**, par ordre de priorité :
1. **Compléter et brancher le module `pathfinding/`** (corriger les bugs internes + intégrer dans `Simulation`) → valeur ajoutée architecturale, distribution multi-chemins propre.
2. **Remplir les fichiers de tests vides** (`test_parser.py`, `test_graph.py`, `test_simulation.py`) → couverture suffisante pour validation.
3. **Compléter le README** (ligne italique, section Resources) → conformité formelle.
4. **Corriger le décalage d'un tour sur les zones `restricted`** (`transit_turns = 1` à l'entrée) → coût 2 tours exact.

Ces trois actions, combinées à la correction du format de sortie, porteraient l'avancement estimé à ~80% et rendraient le projet défendable en soutenance.
