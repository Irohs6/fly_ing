from heapq import heappop, heappush

from .graph import Graph
from .zone import Zone


class Dijkstra:
    """Pathfinding algorithm using Dijkstra's shortest path algorithm."""

    def __init__(self, graph: Graph):
        """Initialize Dijkstra with a graph.

        Args:
            graph: Graph containing zones and connections.
        """
        self.graph = graph

    def shortest_distances(
        self,
        source: str,
        blocked_zones: set[str] | None = None,
        saturated_conns: set[int] | None = None,
    ) -> tuple[dict[str, float], dict[str, str | None]]:
        """
        Calculate shortest distances from a source zone.

        Args:
            source: Starting zone name.
            blocked_zones: Zones that cannot be crossed.
            saturated_conns: Connections that cannot be used.

        Returns:
            Tuple containing:
                - distances: minimum distance for each zone.
                - predecessors: previous zone for path reconstruction.
        """

        distances = {
            node: float("inf")
            for node in self.graph.zones
        }

        predecessors: dict[str, str | None] = {
            node: None
            for node in self.graph.zones
        }

        distances[source] = 0

        priority_queue: list[tuple[float, str]] = [
            (0, source)
        ]

        visited: set[str] = set()

        while priority_queue:
            current_distance, current_node = heappop(
                priority_queue
            )

            if current_node in visited:
                continue

            visited.add(current_node)

            for connection in self.graph.get_neighbors(
                current_node
            ):
                if connection.source.name == current_node:
                    neighbor_zone = connection.target
                else:
                    neighbor_zone = connection.source

                neighbor = neighbor_zone.name

                if (
                    blocked_zones
                    and neighbor in blocked_zones
                ):
                    continue

                if (
                    saturated_conns
                    and id(connection) in saturated_conns
                ):
                    continue

                weight = neighbor_zone.move_cost()

                new_distance = (
                    current_distance + weight
                )

                if new_distance < distances[neighbor]:
                    distances[neighbor] = new_distance
                    predecessors[neighbor] = current_node

                    heappush(
                        priority_queue,
                        (new_distance, neighbor)
                    )

        return distances, predecessors

    def shortest_path(
        self,
        source: str | None = None,
        blocked_zones: set[str] | None = None,
        saturated_conns: set[int] | None = None,
    ) -> list[Zone]:
        """
        Find the shortest path between two zones.

        Args:
            source: Starting zone name.
            blocked_zones: Zones to avoid.
            saturated_conns: Connections to avoid.

        Returns:
            List of zones forming the shortest path.
            Empty list if no path exists.
        """

        if source is None:
            if self.graph.start_zone is None:
                return []
            source = self.graph.start_zone.name

        if self.graph.end_zone is None:
            return []

        target = self.graph.end_zone.name

        distances, predecessors = self.shortest_distances(
            source,
            blocked_zones,
            saturated_conns,
        )

        if distances[target] == float("inf"):
            return []

        path_names: list[str] = []

        current: str | None = target

        while current is not None:
            path_names.append(current)
            current = predecessors[current]

        path_names.reverse()

        return [
            self.graph.zones[name]
            for name in path_names
        ]

    def distance_to(
        self,
        source: str,
        target: str,
    ) -> float:
        """
        Return shortest distance between two zones.

        Args:
            source: Starting zone.
            target: Destination zone.

        Returns:
            Minimal distance.
        """

        distances, _ = self.shortest_distances(source, blocked_zones=None,
                                               saturated_conns=None)

        return distances[target]
