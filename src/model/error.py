class ConnectionError(Exception):
    """Custom exception for connection-related errors."""
    def __init__(self, message: str = "Connection error") -> None:
        self.message = message
        super().__init__(self.message)


Connection_Error = ConnectionError


class ZoneError(Exception):
    """Custom exception for zone-related errors."""
    def __init__(self, message: str = "Zone error") -> None:
        self.message = message
        super().__init__(self.message)


Zone_Error = ZoneError


class GraphError(Exception):
    """Custom exception for graph-related errors."""
    def __init__(self, message: str = "Graph error") -> None:
        self.message = message
        super().__init__(self.message)


Graph_Error = GraphError
