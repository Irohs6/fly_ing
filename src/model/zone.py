class Zone:
    def __init__(self, name: str,
                 metadata: dict[str, str | int] | None = None):
        self.name = name
        self.metadata = metadata

    @property
    def max_drones(self) -> int:
        return int(self.metadata.get("max_drones", 1)) if self.metadata else 1

    @property
    def zone_type(self) -> str:
        return str(
            self.metadata.get("zone", "normal")) if self.metadata else "normal"

    def __str__(self):
        return f"{self.name}"
