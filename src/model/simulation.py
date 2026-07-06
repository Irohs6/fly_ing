from .drone import Drone
from .graph import Graph
from .pathfinder import Djikstra
from .zone import Zone


class Simulation:
    def __init__(self, graph: Graph, debug: bool) -> None:
        self.graph = graph
        self.drones: list[Drone] = []
        self.turn = 0
        self.debug = debug

    def add_drone(self, drone: Drone) -> None:
        self.drones.append(drone)

    def load_drones(self, nb_drones: int) -> None:
        for i in range(nb_drones):
            self.add_drone(Drone(f"D{i + 1}"))

    def start(self) -> None:
        start = self.graph.start_zone
        pathfinder = Djikstra(self.graph)
        path = pathfinder.shortest_path() or []
        for drone in self.drones:
            drone.current_zone = start.name
            drone.path = list(path)[1:]  # skip start zone, drone is already there

    def plan_moves(self) -> list[tuple[Drone, Zone | None]]:
        planned_moves = []
        for drone in self.drones:
            if drone.status == "finished":
                continue
            next_zone_name = drone.path[0] if drone.path else None
            next_zone = self.graph.zones[next_zone_name] if next_zone_name else None
            planned_moves.append((drone, next_zone))
        return planned_moves

    def resolve_conflicts(self, planned_moves: list[tuple[Drone, Zone | None]]) -> list[tuple[Drone, Zone | None]]:
        zone_occupancy = {}
        resolved_moves = []

        for drone, next_zone in planned_moves:
            if next_zone is None:
                resolved_moves.append((drone, None))
                continue

            if next_zone.name not in zone_occupancy:
                zone_occupancy[next_zone.name] = 0

            if zone_occupancy[next_zone.name] < next_zone.max_drones:
                zone_occupancy[next_zone.name] += 1
                resolved_moves.append((drone, next_zone))
            else:
                resolved_moves.append((drone, None))

        return resolved_moves

    def apply_moves(self, planned_moves: list[tuple[Drone, Zone | None]]) -> list[str]:
        movements: list[str] = []

        for drone, next_zone in planned_moves:
            if next_zone is not None:
                drone.move_to_zone(next_zone.name)
                drone.path.pop(0)

                if drone.current_zone == self.graph.end_zone.name:
                    drone.status = "finished"
                movements.append(f"{drone.drone_id}-{next_zone.name}")
            else:
                drone.status = "waiting"
        return movements

    def execute(self) -> None:
        while not all(drone.status == "finished" for drone in self.drones):
            self.turn += 1

            planned_moves = self.plan_moves()
            planned_moves = self.resolve_conflicts(planned_moves)
            movements = self.apply_moves(planned_moves)

            if self.debug:
                waiting = [
                    f"{d.drone_id}(waitting {d.current_zone})"
                    for d in self.drones
                    if d.status == "waiting"
                ]
                print(f"Turn {self.turn}: {' '.join(movements)}")
                if waiting:
                    print("Waiting:", ", ".join(waiting))
            else:
                print(f"Turn {self.turn:>3}: " + " ".join(movements))
           
    def stop(self) -> None:
        pass

    def simulate(self) -> None:
        self.start()
        self.execute()
        self.stop()
