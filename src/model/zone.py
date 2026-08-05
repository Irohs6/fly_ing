from __future__ import annotations
from .error import Zone_Error


class Zone:
    def __init__(
        self,
        name: str,
        color: str = "white",
        zone_type: str | None = None,
        max_drones: int | None = None,
        x: int = 0,
        y: int = 0,
    ):
        self.name = name
        self.color = color
        self._zone_type = zone_type
        self._max_drones = max_drones
        self.nb_drones = 0
        self.x = x
        self.y = y
        self.is_start = False
        self.is_end = False

    @property
    def max_drones(self):
        return self._max_drones

    @property
    def zone_type(self) -> str:
        return self._zone_type if self._zone_type is not None else "normal"

    @zone_type.setter
    def zone_type(self, value: str) -> None:
        self._zone_type = value

    def add_nb_drone(self) -> None:
        if self.max_drones is None:
            self.nb_drones += 1
            return

        if self.nb_drones < self.max_drones:
            self.nb_drones += 1
        else:
            raise Zone_Error("Maximum number of drones reached")

    def remove_nb_drone(self) -> None:
        if self.nb_drones > 0:
            self.nb_drones -= 1
        else:
            raise Zone_Error("No drones to remove")

    def move_cost(self) -> float:
        if self.zone_type == "restricted":
            return 2.0
        elif self.zone_type == "blocked":
            return float("inf")
        else:
            return 1.0

    def can_accept_drone(self) -> bool:
        if self.is_start or self.is_end:
            return True

        return self.nb_drones < self.max_drones

    def __str__(self) -> str:
        return f"{self.name}"

    def __repr__(self) -> str:
        return f"{self.name}"
