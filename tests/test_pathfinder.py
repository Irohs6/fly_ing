"""
Tests for AStarSolver (src/pathfinding/astar_solver.py).

Fixtures build GraphAdapter state directly (no Graph/parser needed),
so tests are fast and self-contained.
"""

import pytest
from collections import namedtuple

from src.pathfinding.astar_solver import AStarSolver
from src.pathfinding.cost_model import CostModel
from src.pathfinding.graph_adapter import GraphAdapter
from src.pathfinding.heuristic import Heuristic

# ──────────────────────────── helpers ────────────────────────────


def _make_adapter(edges: list[tuple], nodes: dict) -> GraphAdapter:
    """
    Build a GraphAdapter without a real Graph object.

    edges : list of (source, target, capacity)
    nodes : dict of name -> (zone_type, max_drones, x, y)
    """
    adapter = GraphAdapter.__new__(GraphAdapter)
    NI = namedtuple("NodeInfo", ["zone_type", "max_drones", "x", "y"])
    EI = namedtuple("EdgeInfo", ["target", "max_capacity", "source"])
    adapter.NodeInfo = NI
    adapter.EdgeInfo = EI

    adapter.node_meta = {
        name: NI(*values) for name, values in nodes.items()
    }
    adapter.adjacency: dict = {}
    for src, tgt, cap in edges:
        adapter.adjacency.setdefault(src, []).append(EI(tgt, cap, src))
        adapter.adjacency.setdefault(tgt, []).append(EI(src, cap, tgt))

    return adapter


def _make_solver(adapter: GraphAdapter) -> AStarSolver:
    return AStarSolver(adapter, CostModel(), Heuristic.zero)


# ──────────────────────────── fixtures ───────────────────────────


@pytest.fixture
def linear_adapter() -> GraphAdapter:
    """Linear graph: A --5-- B --5-- C"""
    return _make_adapter(
        edges=[("A", "B", 5), ("B", "C", 5)],
        nodes={
            "A": ("normal", 10, 0, 0),
            "B": ("normal", 10, 1, 0),
            "C": ("normal", 10, 2, 0),
        },
    )


@pytest.fixture
def fork_adapter() -> GraphAdapter:
    """
    A --5-- B --5-- D
    |               |
    +--5-- C --5---+
    Two paths: A-B-D and A-C-D
    """
    return _make_adapter(
        edges=[("A", "B", 5), ("B", "D", 5), ("A", "C", 5), ("C", "D", 5)],
        nodes={
            "A": ("normal", 10, 0, 0),
            "B": ("normal", 10, 1, 1),
            "C": ("normal", 10, 1, -1),
            "D": ("normal", 10, 2, 0),
        },
    )


# ──────────────────────────── tests ──────────────────────────────


def test_simple_path(linear_adapter: GraphAdapter) -> None:
    solver = _make_solver(linear_adapter)
    path, cost = solver.solve("A", "C", set())
    assert path == ["A", "B", "C"]
    assert cost == 2  # 2 hops × cost 1


def test_start_equals_end(linear_adapter: GraphAdapter) -> None:
    solver = _make_solver(linear_adapter)
    path, cost = solver.solve("A", "A", set())
    assert path == ["A"]
    assert cost == 0


def test_unknown_start_returns_none(linear_adapter: GraphAdapter) -> None:
    solver = _make_solver(linear_adapter)
    path, cost = solver.solve("X", "C", set())
    assert path is None
    assert cost is None


def test_unknown_end_returns_none(linear_adapter: GraphAdapter) -> None:
    solver = _make_solver(linear_adapter)
    path, cost = solver.solve("A", "Z", set())
    assert path is None
    assert cost is None


def test_no_path_disconnected() -> None:
    """Nodes exist but are not connected."""
    adapter = _make_adapter(
        edges=[],
        nodes={
            "A": ("normal", 10, 0, 0),
            "B": ("normal", 10, 1, 0),
        },
    )
    solver = _make_solver(adapter)
    path, cost = solver.solve("A", "B", set())
    assert path is None
    assert cost is None


def test_excluded_edge_forces_detour(fork_adapter: GraphAdapter) -> None:
    """Excluding A-B forces the solver to go through C."""
    solver = _make_solver(fork_adapter)
    path, cost = solver.solve("A", "D", {("A", "B")})
    assert path is not None
    assert "B" not in path
    assert path[0] == "A"
    assert path[-1] == "D"


def test_path_uses_both_directions(linear_adapter: GraphAdapter) -> None:
    """Edges are bidirectional: C→A should work too."""
    solver = _make_solver(linear_adapter)
    path, cost = solver.solve("C", "A", set())
    assert path == ["C", "B", "A"]
    assert cost == 2


def test_restricted_zone_costs_more() -> None:
    """
    Two paths A→B→D and A→C→D.
    B is 'restricted' (cost 2), C is 'normal' (cost 1).
    Optimal path should avoid B.
    """
    adapter = _make_adapter(
        edges=[("A", "B", 5), ("B", "D", 5), ("A", "C", 5), ("C", "D", 5)],
        nodes={
            "A": ("normal", 10, 0, 0),
            "B": ("restricted", 10, 1, 1),
            "C": ("normal", 10, 1, -1),
            "D": ("normal", 10, 2, 0),
        },
    )
    solver = _make_solver(adapter)
    path, cost = solver.solve("A", "D", set())
    assert path == ["A", "C", "D"]
    assert cost == 2  # normal + normal = 1 + 1
