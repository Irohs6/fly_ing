from .graph import Graph
from heapq import heappush, heappop


class Dijktra:
    def __init__(self, graph: Graph):
        self.graph = graph

    def shortest_distances(
        self,
        source: str,
        blocked_zones: set[str] | None = None,
        saturated_conns: set[int] | None = None,
    ) -> tuple[dict[str, float], dict[str, str | None]]:
        """
        Retourne :
            distances : dict {noeud: distance_min}
            predecessors : dict {noeud: noeud_precedent}
        """

        distances = {node: float("inf") for node in self.graph.zones}
        predecessors = {node: None for node in self.graph.zones}

        distances[source] = 0

        priority_queue = [(0, source)]
        visited = set()

        while priority_queue:
            current_distance, current_node = heappop(priority_queue)

            if current_node in visited:
                continue

            visited.add(current_node)
            for connection in self.graph.get_neighbors(current_node):
                # Connections are stored bidirectionally
                # — find the actual neighbor
                if connection.source.name == current_node:
                    neighbor = connection.target.name
                    neighbor_zone = connection.target
                else:
                    neighbor = connection.source.name
                    neighbor_zone = connection.source
                if blocked_zones and neighbor in blocked_zones:
                    continue
                if saturated_conns and id(connection) in saturated_conns:
                    continue
                weight = neighbor_zone.move_cost()
                new_distance = current_distance + weight
                if new_distance < distances[neighbor]:
                    distances[neighbor] = new_distance
                    predecessors[neighbor] = current_node
                    heappush(priority_queue, (new_distance, neighbor))
        return distances, predecessors

    def shortest_path(
        self,
        source: str | None = None,
        blocked_zones: set[str] | None = None,
        saturated_conns: set[int] | None = None,
    ) -> list:
        """
        Retourne la liste des zones du plus court chemin.
        """

        source = source or self.graph.start_zone.name
        target = self.graph.end_zone.name
        distances, predecessors = self.shortest_distances(
            source, blocked_zones, saturated_conns
        )

        if distances[target] == float("inf"):
            return None

        path = []
        current = target

        while current is not None:
            path.append(current)
            current = predecessors[current]
        path.reverse()

        return [self.graph.zones[name] for name in path]

    def distance_to(self, source: str, target: str) -> float:
        """
        Retourne uniquement la distance minimale.
        """

        distances, _ = self.shortest_distances(source)
        return distances[target]
