class Connection:
    __slots__ = ["source", "target", "_max_capacity"]

    def __init__(self, source: str, target: str, capacity: int = None):
        self.source = source
        self.target = target
        self._max_capacity = capacity

    @property
    def max_capacity(self) -> int:
        return self._max_capacity if self._max_capacity is not None else 1

    def __str__(self):
        return (f"{self.source} -> {self.target} "
                f"(max_capacity: {self.max_capacity})")
