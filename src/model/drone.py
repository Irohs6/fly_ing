class Drone:
    def __init__(self, drone_id: str, current_zone: str | None = None) -> None:
        self.drone_id = drone_id
        self.current_zone = current_zone
        self.path: list[str] = []
        self.status: str = "waiting"
        self.transit_turns: int = 0

    def __str__(self):
        return self.drone_id

    def move_to_zone(self, zone_name: str) -> None:
        self.current_zone = zone_name
