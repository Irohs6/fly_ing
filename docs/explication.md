# Explication : comportement actuel de la simulation

---

## Contexte : output observé (challenger map, 25 drones)

```
Turn   4: D1-micro_gate1 D2-maze_trap_a2 D3-maze_trap_a1 D4-gate_hell1
Turn   5: D1-overflow_hell1 D2-micro_gate1 D3-maze_trap_a2 D4-maze_trap_a1 D5-gate_hell1
Turn   6: D1-conv_restricted1 D2-overflow_hell1 D3-micro_gate1 D4-maze_trap_a2 D5-maze_trap_a1 D6-gate_hell1
Turn   7: D1-conv_restricted2 D2-conv_restricted1 D3-overflow_hell1 D4-micro_gate1 D5-maze_trap_a2 D6-maze_trap_a1 D7-gate_hell1
Turn   8: D1-conv_restricted3 D2-conv_restricted2 D3-conv_restricted1 D4-overflow_hell1 D5-micro_gate1 D6-maze_trap_a2 D7-maze_trap_a1 D8-gate_hell1
Turn   9: D1-final_merge D2-conv_restricted3 D3-conv_restricted2 D4-conv_restricted1 D5-overflow_hell1 D6-micro_gate1 D7-maze_trap_a2 D8-maze_trap_a1 D9-gate_hell1
```

Deux comportements anormaux sont visibles :
1. Tous les drones suivent **le même chemin**, en file indienne
2. Les zones `restricted` sont traversées **en 1 tour** au lieu de 2

---

## Problème 1 — Tous les drones prennent le même chemin

### Cause dans le code

Dans `simulation.py`, méthode `start()` :

```python
def start(self) -> None:
    pathfinder = Dijktra(self.graph)
    path = pathfinder.shortest_path() or []
    for drone in self.drones:
        drone.current_zone = start.name
        drone.path = list(path)[1:]  # ← même chemin pour tous
```

`Dijktra.shortest_path()` calcule **un seul chemin optimal** (le plus court en coût).
Chaque drone reçoit une **copie identique** de ce chemin.

### Ce qui se passe réellement

Sur la challenger map, le chemin calculé est par exemple :
```
start → gate_hell1 → maze_trap_a1 → maze_trap_a2 → micro_gate1 → overflow_hell1
       → conv_restricted1 → conv_restricted2 → conv_restricted3 → final_merge → ...
```

Les 25 drones s'alignent tous sur cette route. Comme chaque zone a `max_drones=1`,
ils avancent à **1 par tour**, comme un serpent — d'où l'effet de décalage visible
dans l'output (D1 avance, D2 le suit au tour suivant, etc.).

### Ce qui devrait se passer

Le sujet exige que les drones soient **distribués sur plusieurs chemins** pour
minimiser le nombre de tours total. La map challenger a plusieurs routes parallèles
(`maze_trap_a`, `maze_trap_b`, `gate_hell1..5`, etc.) qui ne sont jamais exploitées.

### Ce qu'il faut corriger

Implémenter une **stratégie multi-chemins** :
- Calculer K chemins disjoints (ou semi-disjoints) entre start et end
- Répartir les drones équitablement entre ces chemins
- Exemple d'approche : algorithme de Yen (K shortest paths), ou flow-based routing

---

## Problème 2 — Les zones `restricted` sont traversées en 1 tour au lieu de 2

### Ce que dit le sujet

> *"restricted — A sensitive zone. Movement to this zone costs 2 turns. The drone
> MUST reach its destination during the next turn — it cannot wait on the connection."*

Concrètement : quand un drone entre dans une zone `restricted`, il doit passer
**1 tour "en transit"** sur la connexion, puis **1 tour pour arriver** à destination.
Au total : 2 tours.

### Ce qu'on observe dans l'output

```
Turn   4: D1-micro_gate1
Turn   5: D1-overflow_hell1   ← overflow_hell1 est restricted, traversé en 1 tour
Turn   6: D1-conv_restricted1 ← conv_restricted1 est restricted, traversé en 1 tour
```

D1 traverse `overflow_hell1` (restricted) en **un seul tour**. Idem pour `conv_restricted1/2/3`.

### Cause dans le code

Le coût des zones restricted est bien pris en compte dans **Dijkstra** (pour choisir
le chemin), mais pas dans la **simulation** elle-même.

Dans `pathfinder.py` :
```python
weight = neighbor_zone.move_cost()  # restricted → 2, utilisé pour trouver le meilleur chemin
```

Mais dans `simulation.py`, `apply_moves()` :
```python
drone.move_to_zone(next_zone.name)  # téléportation immédiate, sans 2 tours
drone.path.pop(0)
```

Le drone est **téléporté instantanément** dans la zone restricted en un seul appel,
quel que soit le coût de la zone. La simulation n'a aucune notion de "drone en transit".

### Ce qu'il faut corriger

Introduire un mécanisme de transit dans `Drone` :

1. Quand un drone se dirige vers une zone `restricted`, il entre dans un état `"in_transit"`
2. Il reste "sur la connexion" pendant 1 tour (invisible, ne peut pas être redirigé)
3. Au tour suivant, il arrive obligatoirement à destination (même si la zone est pleine — il ne peut pas attendre sur la connexion)

Exemple de logique dans `Drone` :

```python
self.transit_turns: int = 0       # tours restants en transit
self.transit_target: str | None = None  # zone de destination en transit
```

Dans `plan_moves` :
- Si `drone.transit_turns > 0` → décrémenter et arriver si `transit_turns == 0`
- Sinon, si la prochaine zone est `restricted` → entrer en transit (2 tours), ne pas arriver immédiatement

---

## Résumé des deux problèmes

| Problème | Cause | Impact | Correction nécessaire |
|---|---|---|---|
| Chemin unique pour tous les drones | `shortest_path()` retourne 1 seul chemin, copié à l'identique | Tous les drones s'entassent en file sur la même route — très lent | Algorithme multi-chemins (K shortest paths ou flow) |
| Restricted zones en 1 tour | `apply_moves` ne distingue pas le coût de déplacement | Les coûts servent au pathfinding mais pas à la simulation | Système de transit dans `Drone` + logique 2 tours dans `execute` |

Ces deux corrections sont **obligatoires** pour respecter le sujet et atteindre les
benchmarks de performance.
