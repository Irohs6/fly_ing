from .zone import Zone


class Connection:
    __slots__ = ["source", "target", "_max_capacity", "nb_drones"]

    def __init__(self, source: Zone, target: Zone, capacity: int = None):
        self.source = source
        self.target = target
        self._max_capacity = capacity
        self.nb_drones = 0

    @property
    def max_capacity(self) -> int:
        return self._max_capacity if self._max_capacity is not None else 1

    def add_nb_drone(self):
        if self.nb_drones < self.max_capacity:
            self.nb_drones += 1
        else:
            raise ValueError("Maximum number of drones reached")

    def remove_nb_drone(self):
        if self.nb_drones > 0:
            self.nb_drones -= 1
        else:
            raise ValueError("No drones to remove")

    def __str__(self):
        return (
            f"{self.source} -> {self.target} "
            f"(max_capacity: {self.max_capacity})"
        )

    __repr__ = __str__
