"""
Fichier  : src/pathfinding/graph_adapter.py
===========================================

Transforme le Graph brut en liste d'adjacence navigable pour A*.
Ce fichier est le seul du module à connaître Zone et Connection.
Tous les autres travaillent uniquement avec des str (noms de hubs)
et des objets EdgeInfo / NodeInfo.

Exposé par :
    adapter.adjacency  → dict[str, list[EdgeInfo]]
    adapter.node_meta  → dict[str, NodeInfo]
"""

from src.model.graph import Graph
from collections import namedtuple


class GraphAdapter:
    def __init__(self, graph: Graph):

        self.EdgeInfo = namedtuple(
            "EdgeInfo", ["target", "max_capacity", "source"]
        )
        self.NodeInfo = namedtuple(
            "NodeInfo", ["zone_type", "max_drones", "x", "y"]
        )
        self.adjacency = {}  # dict[str, list[EdgeInfo]]
        self.node_meta = {}  # dict[str, NodeInfo]
        self._build(graph)

    def _build(self, graph: Graph):
        # Construire adjacency
        for conn in graph.connections:
            source = conn.source_zone
            target = conn.target_zone
            capacity = conn.max_capacity

            edge_to_target = self.EdgeInfo(
                target=target, max_capacity=capacity, source=source
            )
            edge_to_source = self.EdgeInfo(
                target=source, max_capacity=capacity, source=target
            )

            self.adjacency.setdefault(source, []).append(edge_to_target)
            self.adjacency.setdefault(target, []).append(edge_to_source)

        # Construire node_meta
        for zone_name, zone in graph.zones.items():
            self.node_meta[zone_name] = self.NodeInfo(
                zone_type=zone.zone_type,
                max_drones=zone.max_drones,
                x=zone.x,
                y=zone.y,
            )

    def get_neighbors(self, node: str) -> list:
        return self.adjacency.get(node, [])
