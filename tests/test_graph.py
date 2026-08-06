"""Tests for Graph, Zone, Connection, and related model classes."""

import pytest

from src.model.graph import Graph
from src.model.zone import Zone
from src.model.connection import Connection
from src.model.error import Zone_Error, Connection_Error

# ---------------------------------------------------------------------------
# Helpers
# ---------------------------------------------------------------------------

_SENTINEL = object()


def _minimal_config(
    nb_drones: int = 1,
    hubs: list | None = None,
    connections: object = _SENTINEL,
) -> tuple[dict, dict, dict, dict, dict]:
    """Return a minimal parser-like tuple for Graph.load_* methods.

    Pass ``connections=[]`` to get a graph with no edges.
    Omit ``connections`` to get a default direct start->end connection.
    """
    if connections is _SENTINEL:
        connections = [("start", "end", {})]

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

    connection_items = []
    for source, target, metadata in connections:
        connection_items.append(
            {
                "line": 0,
                "source": source,
                "target": target,
                "metadata": metadata,
            }
        )

    return (
        {"line": 1, "value": nb_drones},
        {"line": 2, "name": "start", "x": 0, "y": 0, "zone_type": "start", "metadata": {}},
        {"line": 3, "name": "end", "x": 4, "y": 0, "zone_type": "end", "metadata": {}},
        {"hub": hub_items},
        {"connection": connection_items},
    )


def _build_graph(parsed: tuple[dict, dict, dict, dict, dict]) -> Graph:
    g = Graph()
    _, start_hub, end_hub, hubs, connections = parsed
    g.load_zones(start_hub, end_hub, hubs)
    g.load_connections(connections)
    return g


# ---------------------------------------------------------------------------
# Zone unit tests
# ---------------------------------------------------------------------------


class TestZone:
    def test_defaults(self) -> None:
        z = Zone(name="x")
        assert z.zone_type == "normal"
        assert z.max_drones == 1
        assert z.nb_drones == 0

    def test_explicit_values(self) -> None:
        z = Zone(name="r", zone_type="restricted", max_drones=3, x=1, y=2)
        assert z.zone_type == "restricted"
        assert z.max_drones == 3
        assert z.x == 1
        assert z.y == 2

    def test_move_cost_normal(self) -> None:
        assert Zone(name="n", zone_type="normal").move_cost() == 1

    def test_move_cost_restricted(self) -> None:
        assert Zone(name="r", zone_type="restricted").move_cost() == 2

    def test_move_cost_priority(self) -> None:
        assert Zone(name="p", zone_type="priority").move_cost() == 1

    def test_move_cost_blocked(self) -> None:
        import math

        assert math.isinf(Zone(name="b", zone_type="blocked").move_cost())

    def test_add_nb_drone_within_capacity(self) -> None:
        z = Zone(name="x", max_drones=2)
        z.add_nb_drone()
        assert z.nb_drones == 1
        z.add_nb_drone()
        assert z.nb_drones == 2

    def test_add_nb_drone_exceeds_capacity_raises(self) -> None:
        z = Zone(name="x", max_drones=1)
        z.add_nb_drone()
        with pytest.raises(Zone_Error):
            z.add_nb_drone()

    def test_str(self) -> None:
        z = Zone(name="hub1")
        assert str(z) == "hub1"


# ---------------------------------------------------------------------------
# Connection unit tests
# ---------------------------------------------------------------------------


class TestConnection:
    def _make_conn(self, capacity: int | None = None) -> Connection:
        a = Zone(name="a")
        b = Zone(name="b")
        return Connection(a, b, capacity)

    def test_default_capacity(self) -> None:
        c = self._make_conn()
        assert c.max_capacity == 1

    def test_explicit_capacity(self) -> None:
        c = self._make_conn(capacity=5)
        assert c.max_capacity == 5

    def test_add_and_remove_drone(self) -> None:
        c = self._make_conn(capacity=2)
        c.add_nb_drone()
        assert c.nb_drones == 1
        c.add_nb_drone()
        assert c.nb_drones == 2
        c.remove_nb_drone()
        assert c.nb_drones == 1

    def test_add_drone_exceeds_capacity_raises(self) -> None:
        c = self._make_conn(capacity=1)
        c.add_nb_drone()
        with pytest.raises(Connection_Error):
            c.add_nb_drone()

    def test_remove_drone_below_zero_raises(self) -> None:
        c = self._make_conn()
        with pytest.raises(Connection_Error):
            c.remove_nb_drone()

    def test_str(self) -> None:
        c = self._make_conn(capacity=3)
        assert "a" in str(c) and "b" in str(c)


# ---------------------------------------------------------------------------
# Graph — construction
# ---------------------------------------------------------------------------


class TestGraphConstruction:
    def test_zones_loaded(self) -> None:
        g = _build_graph(_minimal_config())
        assert "start" in g.zones
        assert "end" in g.zones

    def test_start_end_references(self) -> None:
        g = _build_graph(_minimal_config())
        assert g.start_zone is not None
        assert g.start_zone.name == "start"
        assert g.end_zone is not None
        assert g.end_zone.name == "end"

    def test_intermediate_hubs_loaded(self) -> None:
        config = _minimal_config(
            hubs=[
                {"name": "mid", "coordinate": (2, 0), "metadata": {}},
            ],
            connections=[("start", "mid", {}), ("mid", "end", {})],
        )
        g = _build_graph(config)
        assert "mid" in g.zones
        assert len(g.zones) == 3

    def test_connection_stored_bidirectionally(self) -> None:
        g = _build_graph(_minimal_config())
        assert g.get_connection("start", "end") is not None
        assert g.get_connection("end", "start") is not None
        # Same object both directions
        assert g.get_connection("start", "end") is g.get_connection(
            "end", "start"
        )

    def test_connection_missing_zone_raises(self) -> None:
        g = Graph()
        _, start_hub, end_hub, hubs, _ = _minimal_config()
        g.load_zones(start_hub, end_hub, hubs)
        with pytest.raises(KeyError):
            g.add_connection("start", "nonexistent")

    def test_get_neighbors(self) -> None:
        config = _minimal_config(
            hubs=[{"name": "m", "coordinate": (2, 0), "metadata": {}}],
            connections=[("start", "m", {}), ("m", "end", {})],
        )
        g = _build_graph(config)
        neighbors_m = g.get_neighbors("m")
        assert len(neighbors_m) == 2

    def test_get_neighbors_unknown_zone_returns_empty(self) -> None:
        g = _build_graph(_minimal_config())
        assert g.get_neighbors("nowhere") == []

    def test_zone_type_propagated(self) -> None:
        config = _minimal_config(
            hubs=[
                {
                    "name": "r",
                    "coordinate": (1, 0),
                    "metadata": {"zone": "restricted"},
                },
            ],
            connections=[("start", "r", {}), ("r", "end", {})],
        )
        g = _build_graph(config)
        assert g.zones["r"].zone_type == "restricted"

    def test_connection_capacity_propagated(self) -> None:
        config = _minimal_config(
            connections=[("start", "end", {"max_link_capacity": 5})],
        )
        g = _build_graph(config)
        conn = g.get_connection("start", "end")
        assert conn is not None
        assert conn.max_capacity == 5


# ---------------------------------------------------------------------------
# Graph — valid_path
# ---------------------------------------------------------------------------


class TestGraphValidPath:
    def test_direct_path(self) -> None:
        g = _build_graph(_minimal_config())
        assert g.valid_path() is True

    def test_path_through_intermediate(self) -> None:
        config = _minimal_config(
            hubs=[{"name": "m", "coordinate": (2, 0), "metadata": {}}],
            connections=[("start", "m", {}), ("m", "end", {})],
        )
        g = _build_graph(config)
        assert g.valid_path() is True

    def test_no_path_disconnected(self) -> None:
        config = _minimal_config(connections=[])
        g = _build_graph(config)
        assert g.valid_path() is False

    def test_blocked_zone_blocks_only_path(self) -> None:
        config = _minimal_config(
            hubs=[
                {
                    "name": "b",
                    "coordinate": (2, 0),
                    "metadata": {"zone": "blocked"},
                }
            ],
            connections=[("start", "b", {}), ("b", "end", {})],
        )
        g = _build_graph(config)
        assert g.valid_path() is False

    def test_blocked_zone_with_bypass(self) -> None:
        config = _minimal_config(
            hubs=[
                {
                    "name": "b",
                    "coordinate": (2, 1),
                    "metadata": {"zone": "blocked"},
                },
                {"name": "ok", "coordinate": (2, 0), "metadata": {}},
            ],
            connections=[
                ("start", "b", {}),
                ("b", "end", {}),
                ("start", "ok", {}),
                ("ok", "end", {}),
            ],
        )
        g = _build_graph(config)
        assert g.valid_path() is True

    def test_no_start_zone_returns_false(self) -> None:
        g = Graph()
        assert g.valid_path() is False
