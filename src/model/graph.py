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
        self.adjacency: dict[str, list[Connection]] = {}

    def add_zone(self, zone: Zone) -> None:
        self.zones[zone.name] = zone

    def add_connection(
        self,
        source: str,
        target: str,
        max_capacity: int | None = None,
    ) -> None:
        source_zone = self.zones.get(source)
        target_zone = self.zones.get(target)
        if source_zone is None or target_zone is None:
            raise ValueError("Source or target zone not found")

        connection = Connection(source_zone, target_zone, max_capacity)

        self.connections.append(connection)

        self.adjacency.setdefault(source, []).append(connection)
        self.adjacency.setdefault(target, []).append(connection)

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

    def get_neighbors(self, zone_name: str) -> list[Connection]:
        return self.adjacency.get(zone_name, [])

    def __str__(self):
        result = "Graph:\n"
        for connection in self.connections:
            result += f"{connection}\n"
        return result


if __name__ == "__main__":
    graph = Graph()
    graph.load_zones({
        "start_hub": {
            "name": "A",
            "coordinate": [0, 0],
            "metadata": {"color": "red", "zone": "normal", "max_drones": 2},
        },
        "end_hub": {
            "name": "B",
            "coordinate": [1, 1],
            "metadata": {"color": "blue", "zone": "restricted", "max_drones": 3},
        },
        "hub": [
            {
                "name": "C",
                "coordinate": [0, 1],
                "metadata": {"color": "green", "zone": "blocked"},
            }
        ],
    })
    graph.load_connections({
        "connection": [
            ["A", "C", {"max_link_capacity": 2}],
            ["C", "B", {"max_link_capacity": 3}],
        ]
    })
    print(graph)
