# fly_ing — Drone Routing Simulation (42 Project)

> Simulate multiple autonomous drones navigating a network of zones from a start point to an end point in the minimum number of turns.

---

## Project Overview

**fly_ing** is a network-flow optimization and visualization tool built with Python and Pygame. Drones are routed simultaneously through a directed graph of zones (hubs) while respecting capacity constraints and zone-type movement costs. The objective is to deliver all drones to the destination in as few simulation turns as possible.

---

## Architecture (MVC)

```
src/
├── controller/     # Orchestrator — wires parser, model, view
├── model/          # Core entities: Graph, Zone, Connection, Drone, Simulation, Pathfinder
├── parser/         # Map file parser
├── pathfinding/    # A* solver, cost model, heuristics, path generator, route manager
└── view/           # Pygame visualization + terminal output
```

---

## Current State

### ✅ Done

| Component | File | Status |
|---|---|---|
| Parser | `src/parser/parser.py` | Complete — validates map syntax, zones, connections |
| Graph model | `src/model/graph.py` | Complete — adjacency list, zone/connection loading |
| Zone / Connection / Drone | `src/model/*.py` | Complete — all entity attributes modelled |
| Controller | `src/controller/controller.py` | Complete — clean MVC orchestrator |
| A* solver | `src/pathfinding/astar_solver.py` | Complete — heapq-based, supports excluded edges |
| Graph adapter | `src/pathfinding/graph_adapter.py` | Complete — converts Graph for A* |
| Cost model | `src/pathfinding/cost_model.py` | Complete — zone-type costs + capacity malus |
| Heuristics | `src/pathfinding/heuristic.py` | Complete — Manhattan & Euclidean |
| Maps | `assets/maps/` | Complete — easy / medium / hard / challenger |

### 🟡 Partial

| Component | File | Missing |
|---|---|---|
| Path generator | `src/pathfinding/path_generator.py` | Yen's K-shortest paths algorithm incomplete |
| Route manager | `src/pathfinding/route_manager.py` | `prepare()` and `compute_routes()` logic missing |
| Pygame view | `src/view/pygame_view.py` | Zone/connection/drone rendering, stats panel, debug mode |

### 🔴 Not implemented

| Component | File | What's needed |
|---|---|---|
| Simulation engine | `src/model/simulation.py` | Turn-by-turn loop, pathfinder integration, capacity management, output format |
| Pathfinder (model layer) | `src/model/pathfinder.py` | Bridge between simulation and pathfinding module |
| Terminal output | `src/view/terminal.py` | Print moves in format `D1-zone D2-zone ...` per turn |

---

## Rules & Constraints

**Zone types:**
- `normal` — 1-turn transit
- `restricted` — 2-turn transit (drone occupies link for 2 turns)
- `priority` — 1-turn, prioritized in pathfinding
- `blocked` — impassable

**Capacity:**
- Each zone has a `max_drones` limit (default 1; start/end zones allow more)
- Each connection has a `max_link_capacity` (default 1)
- Drones leaving a zone free its capacity on the same turn

**Movement:**
- All drones move simultaneously each turn
- Every drone that can move must move (no unnecessary waiting)
- Drones in multi-turn restricted transit cannot pause mid-link

---

## Performance Targets

| Difficulty | Map | Target turns |
|---|---|---|
| Easy | 3 maps | ≤ 6 / 8 / 6 |
| Medium | 3 maps | ≤ 12 / 15 / 12 |
| Hard | 3 maps | ≤ 30 / 35 / 45 |
| Challenger | 1 map (25 drones) | < 45 |

---

## Setup & Usage

```bash
# Install dependencies
make install

# Run simulation with a map
python main.py assets/maps/easy/01_linear_path.txt

# Debug mode
make debug

# Type checking & linting
make lint
```

**Requirements:** Python ≥ 3.10, Pygame ≥ 2.6

---

## What to do next

1. Implement `Simulation.start()` — the turn-by-turn engine
2. Implement `Pathfinder` (model layer) to call the A* / route manager
3. Complete `PathGenerator` (Yen's K-shortest paths)
4. Complete `RouteManager.prepare()` and `compute_routes()`
5. Add drone/zone/connection rendering to Pygame view
6. Implement `terminal.py` for text output
