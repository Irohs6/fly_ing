from collections import defaultdict
from .connection import Connection
from .zone import Zone


class Graph:
    def __init__(
        self,
        zones: dict[str, Zone] | None = None,
        connections: list[Connection] | None = None,
    ):
        self.zones: dict[str, Zone] = zones or {}
        self.connections: list[Connection] = connections or []
        self.start_zone: Zone | None = None
        self.end_zone: Zone | None = None
        self.adjacency: dict[str, list[Connection]] = defaultdict(list)
        self.connection_map: dict[tuple[str, str], Connection] = {}

    def add_zone(self, zone: Zone) -> None:
        self.zones[zone.name] = zone

    def add_connection(self, source: str, target: str,
                       max_capacity: int | None = None) -> None:
        try:
            source_zone = self.zones[source]
            target_zone = self.zones[target]
        except KeyError as e:
            raise ValueError(f"Unknown zone: {e.args[0]}")

        connection = Connection(source_zone, target_zone, max_capacity)
        self.connections.append(connection)

        self.adjacency[source].append(connection)
        self.adjacency[target].append(connection)

        self.connection_map[(source, target)] = connection
        self.connection_map[(target, source)] = connection

    def _create_zone(self, data: dict[str, object]) -> Zone:
        metadata = data.get("metadata", {})

        return Zone(
            name=data["name"],
            color=metadata.get("color", "white"),
            zone_type=metadata.get("zone", "normal"),
            max_drones=metadata.get("max_drones", 1),
            x=data["coordinate"][0],
            y=data["coordinate"][1],
        )

    def load_zones(self, config: dict) -> None:
        self.start_zone = self._create_zone(config["start_hub"])
        self.end_zone = self._create_zone(config["end_hub"])

        for zone in (self.start_zone, self.end_zone):
            self.add_zone(zone)

        for hub in config.get("hub", []):
            self.add_zone(self._create_zone(hub))

    def load_connections(self, config: dict) -> None:
        for source, target, metadata in config["connection"]:
            self.add_connection(
                source,
                target,
                metadata.get("max_link_capacity")
                )

    def get_neighbors(self, zone_name: str) -> list[Connection]:
        return self.adjacency.get(zone_name, [])

    def get_connection(self, source: str, target: str) -> "Connection | None":
        return self.connection_map.get((source, target))

    def __str__(self):
        return "Graph:\n" + "\n".join(map(str, self.connections))

    def valid_path(self) -> bool:
        # Collecte des zones bloquées (inaccessibles aux drones)
        if self.start_zone is None or self.end_zone is None:
            return False  # Si les zones de départ ou d'arrivée ne sont pas définies

        blocked_zones = {
            zone.name
            for zone in self.zones.values()
            if zone.zone_type == "blocked"
        }
        start = self.start_zone.name
        end = self.end_zone.name

        # Parcours en profondeur (DFS) pour vérifier l'existence d'un chemin
        stack: list[str] = [start]
        visited: set[str] = set()

        while stack:
            current = stack.pop()
            if current == end:
                return True  # Chemin trouvé
            if current in visited:
                continue
            visited.add(current)

            for conn in self.get_neighbors(current):
                if conn.source.name == current:
                    neighbor = conn.target.name
                else:
                    neighbor = conn.source.name

                if neighbor in blocked_zones:
                    continue  # Ignorer les zones bloquées
                if neighbor not in visited:
                    stack.append(neighbor)
        return False  # Aucun chemin possible
