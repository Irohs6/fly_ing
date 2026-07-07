# Récap — Problèmes de simulation (map : challenger/01_the_impossible_dream)

Logs capturés le 2026-07-07. 25 drones, simulation terminée au **tour 57**.

---

## 1. Comportements erratiques observés dans les logs

### 1.1 Drones redirigés dans `maze_loop` (boucle restreinte)

```
Turn 14: D6-maze_loop1(transit)
Turn 16: D6-maze_loop2(transit)
Turn 23: D13-maze_loop1(transit)
Turn 29: D13-maze_loop2(transit) / D23-maze_loop1(transit)
...
Turn 37: D23-maze_loop2(transit)
```

Les zones `maze_loop1-6` forment une **boucle fermée** avec une seule sortie :
`maze_loop3 → micro_gate2`. Ce sont des zones `restricted` à `move_cost = 2`.

Dijkstra les emprunte comme chemin alternatif quand
`gate_hell1 → maze_trap_a1 → maze_trap_a2 → micro_gate1` est saturé.
Résultat : **6+ tours de transit** au lieu d'attendre 1–2 tours que la zone se libère.

### 1.2 Drones redirigés via `priority_trap`

```
Turn 23: D6-priority_trap1
Turn 24: D6-conv_restricted4(transit)

Turn 32: D13-priority_trap1
Turn 33: D13-conv_restricted4(transit)

Turn 38: D18-priority_trap1 / D23-priority_trap1
```

Chemin emprunté : `false_hope1 → priority_trap1 → conv_restricted4 → conv_restricted5 → conv_restricted6 → final_merge`

Ce contournement est disponible via la connexion emergency bypass de la map mais il est **3–4 zones plus long** que le chemin direct `false_hope1 → false_hope2 → false_hope3 → conv_restricted4`. Dijkstra le prend dès que `false_hope2` ou `false_hope3` est bloquée, sans considérer qu'attendre serait souvent plus rapide.

### 1.3 Redirections en cascade irréversibles

Une fois qu'un drone a recalculé son chemin, il **garde le nouveau chemin même si la zone originalement bloquée se libère** au tour suivant. Les drones suivants subissent à leur tour des blocages sur les mêmes zones de détour, créant une cascade où chaque recalcul aggrave la congestion.

---

## 2. Bugs dans le code

### Bug A — Code mort dans `apply_moves` pour les zones `restricted`

**Fichier :** `src/model/simulation.py`, fonction `apply_moves`

```python
# ligne ~130
drone.transit_turns = 0                          # (1) reset à 0
if drone.transit_turns < next_zone.move_cost():  # (2) TOUJOURS VRAI (0 < 2)
    drone.status = "in_transit"
    ...
else:
    # Ce bloc n'est JAMAIS atteint
    drone.status = "moving"
```

`drone.transit_turns` est remis à 0 juste avant le `if`, donc la condition est **toujours vraie** et le bloc `else` est du code mort. Un drone entrant dans une zone restricted sera systématiquement marqué `in_transit`, quelle que soit la valeur réelle du coût.

---

### Bug B — `staying_per_zone` ne compte pas les drones `waiting` (avec path non-vide)

**Fichier :** `src/model/simulation.py`, fonction `resolve_conflicts`

```python
# Seuls les drones avec next_zone is None contribuent à staying_per_zone
for drone, next_zone in planned_moves:
    if next_zone is None:
        staying_per_zone[drone.current_zone] += 1
```

Un drone en statut `waiting` mais dont `path` n'est pas vide a `next_zone != None`.
Il **reste pourtant dans sa zone actuelle** ce tour, mais n'est pas comptabilisé.

**Conséquence :** `zone_capacity` sous-estime l'occupation réelle d'une zone → un nouveau drone peut entrer alors que la zone est déjà à `max_drones`, dépassant la capacité.

---

### Bug C — `drone.path` non réinitialisé si `new_path is None`

**Fichier :** `src/model/simulation.py`, fonction `resolve_conflicts`

```python
new_path = pathfinder.shortest_path(drone.current_zone, blocked_zone=next_zone.name)
if new_path is not None:
    drone.path = list(new_path)[1:]
drone.status = "waiting"  # <- déclenché dans tous les cas
```

Si aucun chemin alternatif n'existe (`new_path is None`), `drone.path` **n'est pas modifié**.
Le drone garde l'ancien chemin et retente exactement le même au tour suivant, ce qui peut créer une **boucle infinie** si le blocage est permanent.

---

### Bug D — Recalcul n'évite qu'un seul blocage à la fois

Lors d'un recalcul dans `resolve_conflicts`, seule `next_zone.name` est passée en `blocked_zone`. Les **autres zones déjà saturées ce tour** (mises à jour dans `zone_capacity`) ne sont pas transmises à Dijkstra. Le nouveau chemin peut donc pointer vers une zone également pleine, forçant un nouveau recalcul au tour suivant.

---

## 3. Problème architectural — Absence de calcul coût/bénéfice de l'attente

Chaque fois qu'une zone est pleine, la simulation **prend automatiquement un chemin alternatif** sans évaluer si attendre 1–2 tours serait plus court.

Exemple : drone à `false_hope2` bloqué, chemin direct +2 zones, détour +6 zones.
La simulation prend le détour.

Il n'existe aucune logique du type :
> « Si `distance(detour) > distance(chemin_original) + turns_d_attente`, alors attendre. »

---

## 4. Résumé des problèmes par priorité

| Priorité | Problème | Impact |
|----------|----------|--------|
| 🔴 Critique | Bug B — capacité de zone sous-estimée | Dépassement de `max_drones`, comportement incorrect |
| 🔴 Critique | Bug C — path non réinitialisé si pas de détour | Boucle infinie potentielle |
| 🟠 Majeur  | Bug D — recalcul aveugle aux autres blocages | Redirections inutiles, congestion en cascade |
| 🟠 Majeur  | Absence de logique attente vs détour | Rallongement massif de la simulation |
| 🟡 Mineur  | Bug A — code mort restricted/transit_turns | Logique illisible, `else` jamais exécuté |

---

## 5. Proposition de correction pour les bugs critiques

### Bug B — Correction `staying_per_zone`
Inclure tous les drones qui restent physiquement dans leur zone, pas seulement ceux avec `path` vide :

```python
# Drones qui ne bougent pas (path vide) OU waiting avec path (ils restent quand même)
for drone, next_zone in planned_moves:
    if next_zone is None:
        staying_per_zone[drone.current_zone] = (
            staying_per_zone.get(drone.current_zone, 0) + 1
        )
```
→ Ajouter aussi les drones `waiting` du tour précédent qui n'ont pas bougé.

### Bug C — Correction path non réinitialisé
```python
if new_path is None:
    drone.path = []  # empêche de retenter indéfiniment le même chemin bloqué
else:
    drone.path = list(new_path)[1:]
drone.status = "waiting"
```

### Bug A — Correction code mort
```python
# Avant de reset transit_turns, comparer avec move_cost
if drone.transit_turns < next_zone.move_cost() - 1:
    drone.transit_turns += 1
    drone.status = "in_transit"
else:
    drone.transit_turns = 0
    drone.status = "moving"
    ...
```
Ou simplement supprimer le reset immédiat et laisser `advance_transit` gérer le compteur.
