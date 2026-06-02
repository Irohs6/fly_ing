from .connection import Connection
from .zone import Zone


class Graph:
    def __init__(
        self,
        zones: dict[str, Zone] = None,
        connections: list[Connection] = None,
    ):
        self.zones: dict[str, Zone] = zones if zones is not None else {}
        self.connections: list[Connection] = (
            connections if connections is not None else []
        )
        self.start_zone: Zone | None = None
        self.end_zone: Zone | None = None

    def add_zone(self, zone: Zone) -> None:
        self.zones[zone.name] = zone

    def add_connection(
        self, source: str, target: str, max_capacity: int = None
    ) -> None:
        connection = Connection(source, target, max_capacity)
        self.connections.append(connection)

    def load_zones(self, config: dict) -> None:
        start_hub_data = config["start_hub"]
        end_hub_data = config["end_hub"]
        start = Zone(
            start_hub_data["name"],
            color=start_hub_data.get("metadata", {}).get("color", "white"),
            zone_type=start_hub_data.get("metadata", {}).get("zone"),
            max_drones=start_hub_data.get("metadata", {}).get("max_drones"),
            x=start_hub_data["coordinate"][0],
            y=start_hub_data["coordinate"][1],
        )
        end = Zone(
            end_hub_data["name"],
            color=end_hub_data.get("metadata", {}).get("color", "white"),
            zone_type=end_hub_data.get("metadata", {}).get("zone"),
            max_drones=end_hub_data.get("metadata", {}).get("max_drones"),
            x=end_hub_data["coordinate"][0],
            y=end_hub_data["coordinate"][1],
        )
        self.start_zone = start
        self.end_zone = end
        self.add_zone(start)
        self.add_zone(end)
        for hub in config["hub"]:
            self.add_zone(
                Zone(
                    hub["name"],
                    color=hub.get("metadata", {}).get("color", "white"),
                    zone_type=hub.get("metadata", {}).get("zone"),
                    max_drones=hub.get("metadata", {}).get("max_drones"),
                    x=hub["coordinate"][0],
                    y=hub["coordinate"][1],
                )
            )

    def load_connections(self, config: dict) -> None:
        for source, target, metadata in config["connection"]:
            max_capacity = metadata.get("max_link_capacity")
            self.add_connection(source, target, max_capacity)

    def __str__(self):
        result = "Graph:\n"
        for connection in self.connections:
            result += f"{connection}\n"
        return result
