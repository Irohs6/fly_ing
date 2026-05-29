class Connection:
    def __init__(self, source: str, target: str, 
                 metadata: dict[str, str | int] | None = None):
        self.source = source
        self.target = target
        self.metadata = metadata

    @property
    def max_capacity(self) -> int:
        return int(
            self.metadata.get("max_link_capacity", 1)) if self.metadata else 1

    def __str__(self):
        return f"{self.source} -> {self.target} ({self.metadata})"
