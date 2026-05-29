from .connection import Connection
from .zone import Zone


class Graph:
    def __init__(self,):
        self.zones: dict[str, Zone] = {}
        self.connections: list[Connection] = []
        self.start_zone: Zone | None = None
        self.end_zone: Zone | None = None

    def add_zone(self, zone: Zone) -> None:
        self.zones[zone.name] = zone

    def add_connection(self, source: str, target: str,
                       metadata: dict | None = None) -> None:
        connection = Connection(source, target, metadata)
        self.connections.append(connection)

    def load_zones(self, config: dict) -> None:
        start = (Zone(config["start_hub"]["name"],
                 config["start_hub"].get("metadata")))
        end = (Zone(config["end_hub"]["name"],
               config["end_hub"].get("metadata")))
        self.start_zone = start
        self.end_zone = end
        self.add_zone(start)
        self.add_zone(end)
        for hub in config["hub"]:
            self.add_zone(Zone(hub["name"], hub.get("metadata")))

    def load_connections(self, config: dict) -> None:
        for source, target, metadata in config["connection"]:
            self.add_connection(source, target, metadata)

    def __str__(self):
        result = "Graph:\n"
        for connection in self.connections:
            result += f"{connection}\n"
        return result
