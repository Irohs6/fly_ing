from .connection import Connection
from .zone import Zone

from collections import defaultdict


class Graph:
    def __init__(
        self,
        zones: dict[str, Zone] = None,
        connections: list[Connection] = None,
    ):
        self.zones: dict[str, Zone] = zones or {}
        self.connections: list[Connection] = connections or []
        self.start_zone: Zone | None = None
        self.end_zone: Zone | None = None
        self.adjacency: dict[str, list[Connection]] = defaultdict(list)

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

        for node in (source, target):
            self.adjacency[node].append(connection)

    def _create_zone(self, data: dict[str, any]) -> Zone:
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
            self.add_connection(source, target,
                                metadata.get("max_link_capacity"))

    def get_neighbors(self, zone_name: str) -> list[Connection]:
        return self.adjacency[zone_name]

    def get_connection(self, source: str, target: str) -> "Connection | None":
        for conn in self.adjacency.get(source, []):
            if conn.source.name == target or conn.target.name == target:
                return conn
        return None

    def __str__(self):
        return "Graph:\n" + "\n".join(map(str, self.connections))

    def valid_path(self) -> bool:
        # Collecte des zones bloquées (inaccessibles aux drones)
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

        # Construction de la liste d'adjacence (hors zones bloquées)
        adjacency = {
            zone.name: []
            for zone in self.zones.values()
            if zone.name not in blocked_zones
        }
        adjacency[start] = []
        adjacency[end] = []

        for conn in self.connections:
            hub1 = conn.source.name
            hub2 = conn.target.name
            # N'ajouter que les connexions entre hubs non bloqués
            if hub1 not in blocked_zones and hub2 not in blocked_zones:
                adjacency[hub1].append(hub2)
                adjacency[hub2].append(hub1)

        while stack:
            current = stack.pop()
            if current == end:
                return True  # Chemin trouvé
            if current not in visited:
                visited.add(current)
                for neighbor in adjacency[current]:
                    if neighbor not in visited:
                        stack.append(neighbor)
        return False  # Aucun chemin possible
