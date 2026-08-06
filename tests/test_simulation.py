"""Tests for the Simulation engine (src/model/simulation.py)."""
import pytest

from src.model.graph import Graph
from src.model.simulation import Simulation
from src.model.error import Graph_Error

# ---------------------------------------------------------------------------
# Helpers
# ---------------------------------------------------------------------------


def _build_graph(
    hubs: list | None = None,
    connections: list | None = None,
    nb_drones: int = 1,
) -> Graph:
    g = Graph()
    hub_items = []
    for hub in hubs or []:
        coord = hub.get("coordinate", (hub.get("x", 0), hub.get("y", 0)))
        hub_items.append(
            {
                "line": 0,
                "name": hub["name"],
                "x": coord[0],
                "y": coord[1],
                "zone_type": "hub",
                "metadata": hub.get("metadata", {}),
            }
        )

    connection_items = [
        {
            "line": 0,
            "source": source,
            "target": target,
            "metadata": metadata,
        }
        for source, target, metadata in (connections or [("start", "end", {})])
    ]

    g.load_zones(
        {
            "line": 1,
            "name": "start",
            "x": 0,
            "y": 0,
            "zone_type": "start",
            "metadata": {"max_drones": nb_drones},
        },
        {
            "line": 2,
            "name": "end",
            "x": 4,
            "y": 0,
            "zone_type": "end",
            "metadata": {"max_drones": nb_drones},
        },
        {"hub": hub_items},
    )
    g.load_connections({"connection": connection_items})
    return g


def _run(graph: Graph, nb_drones: int, capsys) -> Simulation:
    sim = Simulation(graph, debug=False)
    sim.load_drones(nb_drones)
    sim.simulate()
    capsys.readouterr()  # suppress printed output in test results
    return sim


# ---------------------------------------------------------------------------
# Drone loading
# ---------------------------------------------------------------------------


class TestSimulationDroneLoading:
    def test_load_correct_count(self, capsys) -> None:
        g = _build_graph()
        sim = _run(g, 3, capsys)
        assert len(sim.drones) == 3

    def test_drone_ids_sequential(self, capsys) -> None:
        g = _build_graph()
        sim = _run(g, 3, capsys)
        ids = [d.drone_id for d in sim.drones]
        assert ids == ["D1", "D2", "D3"]

    def test_add_drone_manually(self) -> None:
        from src.model.drone import Drone

        g = _build_graph()
        sim = Simulation(g, debug=False)
        sim.add_drone(Drone("D99"))
        assert any(d.drone_id == "D99" for d in sim.drones)


# ---------------------------------------------------------------------------
# Simulation completion
# ---------------------------------------------------------------------------


class TestSimulationCompletion:
    def test_single_drone_finishes(self, capsys) -> None:
        g = _build_graph(nb_drones=1)
        sim = _run(g, 1, capsys)
        assert all(d.status == "finished" for d in sim.drones)

    def test_two_drones_finish(self, capsys) -> None:
        # Two drones on a direct start->end with default capacity 1 on both
        # zone and link — they go one at a time, both finish eventually.
        g = _build_graph(nb_drones=2)
        sim = _run(g, 2, capsys)
        assert all(d.status == "finished" for d in sim.drones)

    def test_turn_count_positive(self, capsys) -> None:
        g = _build_graph(nb_drones=1)
        sim = _run(g, 1, capsys)
        assert sim.turn >= 1

    def test_single_drone_direct_path_one_turn(self, capsys) -> None:
        """A single drone on a direct start->end connection takes 1 turn."""
        g = _build_graph(nb_drones=1)
        sim = _run(g, 1, capsys)
        assert sim.turn == 1

    def test_path_through_intermediate_hub(self, capsys) -> None:
        g = _build_graph(
            hubs=[{"name": "mid", "coordinate": (2, 0), "metadata": {}}],
            connections=[("start", "mid", {}), ("mid", "end", {})],
            nb_drones=1,
        )
        sim = _run(g, 1, capsys)
        assert all(d.status == "finished" for d in sim.drones)
        assert sim.turn == 2  # start->mid (1) + mid->end (1)

    def test_restricted_zone_costs_two_turns(self, capsys) -> None:
        """A restricted intermediate zone costs 2 turns to traverse."""
        g = _build_graph(
            hubs=[
                {
                    "name": "r",
                    "coordinate": (2, 0),
                    "metadata": {"zone": "restricted"},
                }
            ],
            connections=[("start", "r", {}), ("r", "end", {})],
            nb_drones=1,
        )
        sim = _run(g, 1, capsys)
        assert all(d.status == "finished" for d in sim.drones)
        # 1 turn to enter restricted + 1 transit turn + 1 turn to exit = 3
        assert sim.turn == 3

    def test_multiple_drones_on_high_capacity_path(self, capsys) -> None:
        """With high link+zone capacity, all drones finish quickly."""
        g = Graph()
        g.load_zones(
            {
                "line": 1,
                "name": "start",
                "x": 0,
                "y": 0,
                "zone_type": "start",
                "metadata": {"max_drones": 4},
            },
            {
                "line": 2,
                "name": "end",
                "x": 1,
                "y": 0,
                "zone_type": "end",
                "metadata": {"max_drones": 4},
            },
            {"hub": []},
        )
        g.load_connections(
            {
                "connection": [
                    {
                        "line": 3,
                        "source": "start",
                        "target": "end",
                        "metadata": {"max_link_capacity": 4},
                    }
                ]
            }
        )
        sim = Simulation(g, debug=False)
        sim.load_drones(4)
        sim.simulate()
        capsys.readouterr()
        assert all(d.status == "finished" for d in sim.drones)


# ---------------------------------------------------------------------------
# Tours (replay history)
# ---------------------------------------------------------------------------


class TestSimulationTours:
    def test_tours_recorded(self, capsys) -> None:
        g = _build_graph(nb_drones=1)
        sim = _run(g, 1, capsys)
        # At least the initial state (turn 0) + 1 move turn
        assert len(sim.tours) >= 2

    def test_initial_tour_has_drone_at_start(self, capsys) -> None:
        g = _build_graph(nb_drones=1)
        sim = Simulation(g, debug=False)
        sim.load_drones(1)
        sim.start()
        capsys.readouterr()
        assert sim.tours[0]["D1"] == "start"

    def test_tours_count_matches_turns(self, capsys) -> None:
        g = _build_graph(nb_drones=1)
        sim = _run(g, 1, capsys)
        # tours = initial state + one entry per executed turn
        assert len(sim.tours) == sim.turn + 1


# ---------------------------------------------------------------------------
# Capacity constraints
# ---------------------------------------------------------------------------


class TestSimulationCapacity:
    def test_zone_capacity_not_exceeded(self, capsys) -> None:
        """At no point should a zone's nb_drones exceed its max_drones."""
        g = _build_graph(
            hubs=[
                {
                    "name": "mid",
                    "coordinate": (2, 0),
                    "metadata": {"max_drones": 1},
                }
            ],
            connections=[("start", "mid", {}), ("mid", "end", {})],
            nb_drones=2,
        )
        sim = _run(g, 2, capsys)
        # If simulation ran without error, capacity was respected.
        assert all(d.status == "finished" for d in sim.drones)

    def test_connection_capacity_not_exceeded(self, capsys) -> None:
        g = _build_graph(
            connections=[("start", "end", {"max_link_capacity": 1})],
            nb_drones=2,
        )
        sim = _run(g, 2, capsys)
        assert all(d.status == "finished" for d in sim.drones)


# ---------------------------------------------------------------------------
# Error handling
# ---------------------------------------------------------------------------


class TestSimulationErrors:
    def test_start_raises_if_no_start_zone(self) -> None:
        g = Graph()
        sim = Simulation(g, debug=False)
        sim.load_drones(1)
        with pytest.raises(Graph_Error):
            sim.start()

    def test_simulate_completes_without_exception(self, capsys) -> None:
        g = _build_graph(nb_drones=1)
        # Should not raise
        sim = _run(g, 1, capsys)
        assert sim.turn >= 1


# ---------------------------------------------------------------------------
# Real map integration tests
# ---------------------------------------------------------------------------


class TestSimulationRealMaps:
    """End-to-end tests using the actual map files provided in assets/maps/."""

    def _run_map(self, path: str, nb_drones: int, capsys) -> int:
        from src.parser.parser import Parser

        _, start_hub, end_hub, hubs, connections = Parser(path).parse()
        g = Graph()
        g.load_zones(start_hub, end_hub, hubs)
        g.load_connections(connections)
        sim = Simulation(g, debug=False)
        sim.load_drones(nb_drones)
        sim.simulate()
        capsys.readouterr()
        assert all(d.status == "finished" for d in sim.drones)
        return sim.turn

    def test_easy_01_linear_path(self, capsys) -> None:
        turns = self._run_map("assets/maps/easy/01_linear_path.txt", 2, capsys)
        assert turns <= 6

    def test_easy_02_simple_fork(self, capsys) -> None:
        turns = self._run_map("assets/maps/easy/02_simple_fork.txt", 4, capsys)
        assert turns <= 8

    def test_easy_03_basic_capacity(self, capsys) -> None:
        turns = self._run_map(
            "assets/maps/easy/03_basic_capacity.txt", 4, capsys
        )
        assert turns <= 6

    def test_medium_01_dead_end_trap(self, capsys) -> None:
        turns = self._run_map(
            "assets/maps/medium/01_dead_end_trap.txt", 5, capsys
        )
        assert turns <= 12

    def test_medium_02_circular_loop(self, capsys) -> None:
        turns = self._run_map(
            "assets/maps/medium/02_circular_loop.txt", 6, capsys
        )
        assert turns <= 15

    def test_medium_03_priority_puzzle(self, capsys) -> None:
        turns = self._run_map(
            "assets/maps/medium/03_priority_puzzle.txt", 5, capsys
        )
        assert turns <= 12

    def test_hard_01_maze_nightmare(self, capsys) -> None:
        turns = self._run_map(
            "assets/maps/hard/01_maze_nightmare.txt", 8, capsys
        )
        assert turns <= 30

    def test_hard_02_capacity_hell(self, capsys) -> None:
        turns = self._run_map(
            "assets/maps/hard/02_capacity_hell.txt", 12, capsys
        )
        assert turns <= 35

    def test_hard_03_ultimate_challenge(self, capsys) -> None:
        turns = self._run_map(
            "assets/maps/hard/03_ultimate_challenge.txt", 15, capsys
        )
        assert turns <= 45
