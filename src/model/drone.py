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

        self.status = "idle"

        self.transit_turns = 0

        self.moving_connection: tuple[bool, Connection | None] = (False, None)

    def __str__(self) -> str:
        return self.drone_id

    def next_zone(self) -> Zone | None:
        """
        Return next destination zone.
        """

        if not self.path:
            return None

        return self.path[0]

    def enter_zone(self, zone: Zone, connection: Connection) -> None:
        """
        Move the drone to a new zone.
        """

        self.current_zone = zone

        self.path.pop(0)

        self.moving_connection = (True, connection)

        self.status = "moving"

    def finish_if_arrived(self, end_zone: Zone) -> None:

        if self.current_zone == end_zone:

            self.status = "finished"

        else:

            self.status = "waiting"

    def wait(self) -> None:

        self.status = "waiting"

    def start_transit(self) -> None:

        self.status = "in_transit"

        self.transit_turns = 0
