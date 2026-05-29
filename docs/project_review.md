# Code Review — Projet Fly-in (état au 29/05/2026 — v2)

## Périmètre : parser, graph, zone, connection, drone, controller, simulation (squelette)
## Vue non incluse (en cours)

---

## Notation globale : 7.5 / 10

Le modèle est solide et bien découplé. Le controller est propre et pur orchestrateur. Il manque seulement le cœur métier (simulation + pathfinder).

---

## Fichier par fichier

---

### `src/parser/parser.py` — 8.5/10

Déjà reviewé en détail dans `parser_review.md`. Résumé :

| Point | État |
|---|---|
| SRP respecté | ✅ |
| Validation complète (doublons, zones inconnues, métadonnées) | ✅ |
| Type hints + docstrings | ✅ |
| `_parse_hub_line` mute `self.config` au lieu de retourner | ⚠️ |
| Pas extensible sans modification (O/C) | ⚠️ |
| Couplé au disque, pas testable sans fichier | ⚠️ |
| `self.config` non typé (devrait être `TypedDict`) | ⚠️ |

**Rien à corriger en urgence. Fichier fonctionnel.**

---

### `src/model/zone.py` — 9/10

**État actuel :**
- `metadata: dict[str, str | int] | None` typé ✅
- `__str__` retourne juste `self.name` ✅
- Propriétés `max_drones` et `zone_type` présentes ✅
- Plus de `connections` ✅

**Reste :**
- Pas de propriété `color` ni `coordinate` (utiles pour la vue — non urgent)
- Pas de docstring

---

### `src/model/connection.py` — 8.5/10

**État actuel :**
- Renommé `Connection` (faute corrigée) ✅
- `metadata: dict[str, str | int] | None` typé ✅
- Propriété `max_capacity` présente ✅

**Reste :**
- `__str__` affiche encore `(None)` si metadata vide — remplacer par `f"{self.source} -> {self.target}"`
- Pas de docstring

---

### `src/model/drone.py` — 8.5/10

**État actuel :**
- `path`, `status`, `transit_turns` présents ✅
- `move_to_zone -> None` ✅
- `drone_id` généré en `f"D{i+1}"` via `Simulation.load_drones` ✅

**Reste :**
- Pas de docstring
- `status` est un `str` libre — un `Literal["waiting", "in_transit", "arrived"]` serait plus robuste

---

### `src/model/graph.py` — 8.5/10

**État actuel :**
- Type hints complets ✅
- `start_zone` / `end_zone` séparés ✅
- `load_zones(config)` et `load_connections(config)` : le graph construit lui-même son contenu depuis le config ✅
- Convention harmonisée : `add_connection(source, target, metadata)` crée le `Connection` en interne ✅

**Reste :**
- `get_neighbors(zone_name: str) -> list[Zone]` manquante — le pathfinder en aura besoin
- `is_accessible(zone_name: str) -> bool` manquante
- `__str__` n'affiche que les connexions, pas les zones
- Pas de docstrings

---

### `src/controller/controller.py` — 9.5/10

**État actuel :**
```python
def __init__(self, file_path: str) -> None:
    config = Parser(file_path).parse()
    self.graph = self.__create_graph()
    self.simulation = self.__create_simulation()
    self.view = self.__create_view()
    self.graph.load_zones(config)
    self.graph.load_connections(config)
    self.simulation.load_drones(config["nb_drones"])
```
- Pur orchestrateur : ne connaît plus `Zone`, `Drone`, `Connection` ✅
- `config` variable locale (pas d'attribut inutile) ✅
- `graph`, `simulation`, `view` tous créés et initialisés ✅
- Type hints sur toutes les méthodes ✅

**Reste :**
- Pas de docstrings
- `__create_view` retourne `View` qui dépend d'un module non reviewé

---

### `src/model/simulation.py` — 4/10 (squelette)

**État actuel :**
- `add_drone(drone: Drone)` ✅
- `load_drones(nb_drones: int)` — crée les drones `D1..Dn` ✅
- `start()` présent mais vide ⚠️

**Reste (tout le cœur métier) :**
- Boucle tour par tour
- Appel au pathfinder pour calculer les chemins
- Respect des capacités zones/connexions
- Affichage `D1-zone D2-zone ...` à chaque tour
- Détection de fin (tous les drones `arrived`)

---

### `src/model/pathfinder.py` — 0/10 (vide)

À implémenter. Besoins minimaux :
- BFS ou Dijkstra sur `Graph`
- Respecter `zone_type` (blocked = inaccessible, restricted = 2 tours)
- Retourner un chemin `list[str]` (noms de zones)

---

## Point OOP

| Principe | État |
|---|---|
| **Encapsulation** | ✅ Parser API réduite à `parse()`. Controller utilise des méthodes privées. Zone/Connection exposent des propriétés au lieu de metadata brutes. |
| **Abstraction** | ✅ Propriétés `max_drones`, `zone_type`, `max_capacity` masquent le dict interne. |
| **Héritage** | ➖ Non utilisé. Pas nécessaire à ce stade. |
| **Polymorphisme** | ➖ Non utilisé. Pourrait servir pour les types de zones mais pas obligatoire. |
| **SRP** | ✅ Chaque classe a une responsabilité claire. |
| **Couplage** | ✅ Controller ne connaît plus les classes du modèle en détail. |

---

## Point MVC

| Couche | Fichier | État |
|---|---|---|
| **Model** | `zone`, `connection`, `drone`, `graph`, `simulation`, `pathfinder` | Bien séparé. Aucun import de controller ou view. ✅ |
| **View** | `terminal.py`, `pygame_view.py` | En cours — non reviewé. |
| **Controller** | `controller.py`, `parser.py` | ⚠️ Le parser est dans `src/parser/` — cohérent. Le controller est dans `src/controller/` — cohérent. Mais le controller importe directement `Conection`, `Drone`, `Zone` alors qu'il ne devrait les manipuler qu'à travers le `Graph` et la `Simulation`. |

**MVC résolu ✅** : le controller ne connaît plus `Zone`, `Drone`, `Connection`. Il délègue via `graph.load_zones()`, `graph.load_connections()`, `simulation.load_drones()`. Chaque couche encapsule sa propre logique de construction.

---

## Ce qui reste à faire (par priorité)

| Priorité | Tâche |
|---|---|
| 🔴 | Implémenter `Simulation.start()` (boucle tours + appel pathfinder) |
| 🔴 | Implémenter `Pathfinder` (BFS + contraintes zone_type + capacités) |
| 🟠 | Ajouter `get_neighbors(zone_name)` dans `Graph` |
| 🟠 | Ajouter `is_accessible(zone_name)` dans `Graph` |
| 🟡 | `Connection.__str__` : ne pas afficher `(None)` si metadata vide |
| 🟡 | `Drone.status` → `Literal["waiting", "in_transit", "arrived"]` |
| 🟡 | Docstrings sur tous les fichiers |
| 🟡 | Tests unitaires `Graph`, `Drone`, `Simulation` |
