"""Tests for Dijkstra pathfinder (src/model/pathfinder.py)."""

import math

from src.model.graph import Graph
from src.model.pathfinder import Dijkstra

# ---------------------------------------------------------------------------
# Helpers
# ---------------------------------------------------------------------------


def _build_graph(
    hubs: list | None = None,
    connections: list | None = None,
    start: tuple = (0, 0),
    end: tuple = (10, 0),
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
        for source, target, metadata in (connections or [])
    ]

    g.load_zones(
        {
            "line": 1,
            "name": "start",
            "x": start[0],
            "y": start[1],
            "zone_type": "start",
            "metadata": {},
        },
        {
            "line": 2,
            "name": "end",
            "x": end[0],
            "y": end[1],
            "zone_type": "end",
            "metadata": {},
        },
        {"hub": hub_items},
    )
    g.load_connections({"connection": connection_items})
    return g


# ---------------------------------------------------------------------------
# Basic path finding
# ---------------------------------------------------------------------------


class TestDijkstraBasic:
    def test_direct_path_found(self) -> None:
        g = _build_graph(connections=[("start", "end", {})])
        ph = Dijkstra(g)
        path = ph.shortest_path()
        assert path is not None
        assert path[0].name == "start"
        assert path[-1].name == "end"

    def test_path_through_intermediate(self) -> None:
        g = _build_graph(
            hubs=[{"name": "mid", "coordinate": (5, 0), "metadata": {}}],
            connections=[("start", "mid", {}), ("mid", "end", {})],
        )
        ph = Dijkstra(g)
        path = ph.shortest_path()
        assert path is not None
        names = [z.name for z in path]
        assert names == ["start", "mid", "end"]

    def test_no_path_returns_none(self) -> None:
        # No connections at all
        g = _build_graph(connections=[])
        ph = Dijkstra(g)
        assert ph.shortest_path() is None

    def test_path_starts_at_start_ends_at_end(self) -> None:
        g = _build_graph(
            hubs=[
                {"name": "a", "coordinate": (2, 0), "metadata": {}},
                {"name": "b", "coordinate": (5, 0), "metadata": {}},
            ],
            connections=[("start", "a", {}), ("a", "b", {}), ("b", "end", {})],
        )
        ph = Dijkstra(g)
        path = ph.shortest_path()
        assert path is not None
        assert path[0].name == "start"
        assert path[-1].name == "end"

    def test_custom_source(self) -> None:
        g = _build_graph(
            hubs=[{"name": "mid", "coordinate": (5, 0), "metadata": {}}],
            connections=[("start", "mid", {}), ("mid", "end", {})],
        )
        ph = Dijkstra(g)
        path = ph.shortest_path(source="mid")
        assert path is not None
        assert path[0].name == "mid"
        assert path[-1].name == "end"


# ---------------------------------------------------------------------------
# Cost / weights
# ---------------------------------------------------------------------------


class TestDijkstraCosts:
    def test_prefers_normal_over_restricted(self) -> None:
        """When two paths exist, the lower-cost one is chosen."""
        # normal path: start -> n1 -> end  (cost = 1+1 = 2)
        # restricted path: start -> r1 -> end (cost = 1+2 = 3)
        g = _build_graph(
            hubs=[
                {
                    "name": "n1",
                    "coordinate": (3, 0),
                    "metadata": {"zone": "normal"},
                },
                {
                    "name": "r1",
                    "coordinate": (3, 1),
                    "metadata": {"zone": "restricted"},
                },
            ],
            connections=[
                ("start", "n1", {}),
                ("n1", "end", {}),
                ("start", "r1", {}),
                ("r1", "end", {}),
            ],
        )
        ph = Dijkstra(g)
        path = ph.shortest_path()
        assert path is not None
        names = [z.name for z in path]
        assert "n1" in names
        assert "r1" not in names

    def test_distance_to_direct(self) -> None:
        g = _build_graph(connections=[("start", "end", {})])
        ph = Dijkstra(g)
        d = ph.distance_to("start", "end")
        assert d == 1.0  # default normal zone cost

    def test_distance_through_restricted(self) -> None:
        g = _build_graph(
            hubs=[
                {
                    "name": "r",
                    "coordinate": (5, 0),
                    "metadata": {"zone": "restricted"},
                }
            ],
            connections=[("start", "r", {}), ("r", "end", {})],
        )
        ph = Dijkstra(g)
        # cost: start->r = 2 (restricted destination), r->end = 1
        d = ph.distance_to("start", "end")
        assert d == 3.0

    def test_distance_unreachable_is_inf(self) -> None:
        g = _build_graph(connections=[])
        ph = Dijkstra(g)
        d = ph.distance_to("start", "end")
        assert math.isinf(d)


# ---------------------------------------------------------------------------
# Blocked zones
# ---------------------------------------------------------------------------


class TestDijkstraBlocked:
    def test_blocked_zone_in_blocked_set(self) -> None:
        g = _build_graph(
            hubs=[{"name": "b", "coordinate": (5, 0), "metadata": {}}],
            connections=[("start", "b", {}), ("b", "end", {})],
        )
        ph = Dijkstra(g)
        path = ph.shortest_path(blocked_zones={"b"})
        assert path is None

    def test_blocked_zone_with_bypass(self) -> None:
        g = _build_graph(
            hubs=[
                {"name": "blocked_hub", "coordinate": (5, 1), "metadata": {}},
                {"name": "bypass", "coordinate": (5, 0), "metadata": {}},
            ],
            connections=[
                ("start", "blocked_hub", {}),
                ("blocked_hub", "end", {}),
                ("start", "bypass", {}),
                ("bypass", "end", {}),
            ],
        )
        ph = Dijkstra(g)
        path = ph.shortest_path(blocked_zones={"blocked_hub"})
        assert path is not None
        names = [z.name for z in path]
        assert "blocked_hub" not in names
        assert "bypass" in names

    def test_zone_type_blocked_is_never_entered(self) -> None:
        """Dijkstra must not route through a zone with zone_type=blocked."""
        g = _build_graph(
            hubs=[
                {
                    "name": "wall",
                    "coordinate": (5, 0),
                    "metadata": {"zone": "blocked"},
                }
            ],
            connections=[("start", "wall", {}), ("wall", "end", {})],
        )
        # valid_path() uses DFS that skips blocked zones
        assert g.valid_path() is False


# ---------------------------------------------------------------------------
# Shortest distances
# ---------------------------------------------------------------------------


class TestDijkstraDistances:
    def test_all_distances_initialized(self) -> None:
        g = _build_graph(
            hubs=[{"name": "mid", "coordinate": (5, 0), "metadata": {}}],
            connections=[("start", "mid", {}), ("mid", "end", {})],
        )
        ph = Dijkstra(g)
        dists, _ = ph.shortest_distances("start")
        assert "start" in dists
        assert "mid" in dists
        assert "end" in dists

    def test_source_distance_is_zero(self) -> None:
        g = _build_graph(connections=[("start", "end", {})])
        ph = Dijkstra(g)
        dists, _ = ph.shortest_distances("start")
        assert dists["start"] == 0

    def test_predecessors_reconstruct_path(self) -> None:
        g = _build_graph(
            hubs=[{"name": "m", "coordinate": (5, 0), "metadata": {}}],
            connections=[("start", "m", {}), ("m", "end", {})],
        )
        ph = Dijkstra(g)
        _, preds = ph.shortest_distances("start")
        assert preds["m"] == "start"
        assert preds["end"] == "m"
