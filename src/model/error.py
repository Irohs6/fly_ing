class Drone_Error(Exception):
    """Custom exception for drone-related errors."""
    def __init__(self, message: str = "Drone error") -> None:
        self.message = message
        super().__init__(self.message)


class Connection_Error(Exception):
    """Custom exception for connection-related errors."""
    def __init__(self, message: str = "Connection error") -> None:
        self.message = message
        super().__init__(self.message)


class Zone_Error(Exception):
    """Custom exception for zone-related errors."""
    def __init__(self, message: str = "Zone error") -> None:
        self.message = message
        super().__init__(self.message)


class Graph_Error(Exception):
    """Custom exception for graph-related errors."""
    def __init__(self, message: str = "Graph error") -> None:
        self.message = message
        super().__init__(self.message)
