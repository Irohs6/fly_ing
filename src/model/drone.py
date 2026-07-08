from __future__ import annotations
from .zone import Zone
from .connection import Connection


class Drone:
    def __init__(
        self, drone_id: str, current_zone: Zone | None = None
    ) -> None:
        self.drone_id = drone_id
        self.current_zone = current_zone
        self.path: list[Zone] = []
        self.status: str = "waiting"
        self.transit_turns: int = 0
        self.entry_connection: Connection | None = None

    def __str__(self):
        return self.drone_id

    def move_to_zone(
        self, zone: Zone, connection: Connection | None = None
    ) -> None:
        if self.current_zone is not None:
            self.current_zone.nb_drones -= 1
        if self.entry_connection is not None:
            self.entry_connection.nb_drones -= 1
        self.current_zone = zone
        zone.nb_drones += 1
        self.entry_connection = connection
        if connection is not None:
            connection.nb_drones += 1
