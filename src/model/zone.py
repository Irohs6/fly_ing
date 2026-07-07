from __future__ import annotations


class Zone:
    def __init__(self, name: str, color: str = "white",
                 zone_type: str = None, max_drones: int = None,
                 x: int = 0, y: int = 0):
        self.name = name
        self.color = color
        self._zone_type = zone_type
        self._max_drones = max_drones
        self.nb_drones = 0
        self.x = x
        self.y = y

    @property
    def max_drones(self) -> int:
        return self._max_drones if self._max_drones is not None else 1

    @property
    def zone_type(self) -> str:
        return self._zone_type if self._zone_type is not None else "normal"

    @zone_type.setter
    def zone_type(self, value: str) -> None:
        self._zone_type = value

    def add_nb_drone(self):
        if self.nb_drones < self.max_drones:
            self.nb_drones += 1
        else:
            raise ValueError("Maximum number of drones reached")

    def move_cost(self) -> int:
        if self.zone_type == "restricted":
            return 2
        elif self.zone_type == "blocked":
            return float("inf")
        else:
            return 1

    def __str__(self):
        return f"{self.name}"
