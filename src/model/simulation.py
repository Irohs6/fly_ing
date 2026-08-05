from .drone import Drone
from .graph import Graph
from .pathfinder import Dijkstra
from .error import GraphError


class Simulation:

    def __init__(
        self, graph: Graph, debug: bool, pathfinder: Dijkstra | None = None
    ) -> None:

        self.graph = graph
        self.drones: list[Drone] = []
        self.turn = 0
        self.debug = debug

        self.ph = pathfinder if pathfinder is not None else Dijkstra(graph)

        self.tours: list[dict[str, str]] = []
        self.replay_frames: list[dict[str, object]] = []

    def add_drone(self, drone: Drone) -> None:

        self.drones.append(drone)

    def load_drones(self, nb_drones: int) -> None:

        for i in range(nb_drones):

            self.add_drone(Drone(f"D{i + 1}"))

    def start(self) -> None:

        start = self.graph.start_zone

        if start is None:

            raise GraphError("Start zone is not defined")

        path = self.ph.shortest_path()

        if not path:

            raise GraphError("No valid path found")

        for drone in self.drones:

            drone.current_zone = start

            start.add_nb_drone()

            drone.path = list(path[1:])

            drone.status = "moving"

        self._record_tour()

    def execute(self) -> None:

        max_stall = len(self.drones) * len(self.graph.zones) + 1

        stalled_turns = 0

        while not self.finished():

            self.turn += 1

            self.advance_transit()

            movements = self.move_drones()

            self.release_connections()

            if self.no_progress(movements):

                stalled_turns += 1

                if stalled_turns >= max_stall:

                    raise GraphError(
                        f"Deadlock detected after "
                        f"{max_stall} stalled turns"
                    )

            else:

                stalled_turns = 0

            self.display_turn(movements)

            self._record_tour()

    def finished(self) -> bool:

        return bool(self.drones) and all(
            drone.status == "finished" for drone in self.drones
        )

    def advance_transit(self) -> None:

        for drone in self.drones:

            if drone.status != "in_transit":

                continue

            drone.transit_turns += 1

            # Une zone restricted demande un tour
            # supplémentaire avant de continuer

            if drone.transit_turns >= 1:

                drone.status = "moving"

                drone.transit_turns = 0

    def move_drones(self) -> list[str]:

        movements: list[str] = []

        for drone in self.drones:

            if drone.status in ("finished", "in_transit"):

                continue

            result = self._try_move(drone)

            if result:

                movements.append(result)

        return movements

    def _try_move(self, drone: Drone) -> str | None:
        blocked_candidates: set[str] = set()
        max_iter = len(self.graph.zones) + 1

        for _ in range(max_iter):

            next_zone = drone.next_zone()

            if next_zone is None:

                drone.finish_if_arrived(self.graph.end_zone)

                return None

            conn = self.graph.get_connection(
                drone.current_zone.name, next_zone.name
            )

            if conn is None:

                drone.wait()

                return None

            if next_zone.can_accept_drone() and conn.can_accept_drone():

                previous_zone = drone.current_zone

                conn.add_nb_drone()
                next_zone.add_nb_drone()

                drone.enter_zone(next_zone, conn)

                if previous_zone is not None:

                    previous_zone.remove_nb_drone()

                if next_zone.zone_type == "restricted":

                    drone.start_transit()

                    return f"{drone.drone_id}-{next_zone.name}(transit)"

                if drone.current_zone == self.graph.end_zone:

                    drone.status = "finished"

                return f"{drone.drone_id}-{next_zone.name}"

            if next_zone.zone_type == "priority":

                drone.wait()

                return None

            blocked_candidates.add(next_zone.name)

            new_path = self.ph.shortest_path(
                source=drone.current_zone.name,
                blocked_zones=blocked_candidates,
            )

            if not new_path or len(new_path) <= 1:

                drone.wait()

                return None

            drone.path = list(new_path[1:])

        drone.wait()

        return None

    def release_connections(self) -> None:

        for drone in self.drones:

            if not drone.moving_connection[0]:

                continue

            if drone.status == "in_transit":

                continue

            connection = drone.moving_connection[1]

            if connection:

                connection.remove_nb_drone()

            drone.moving_connection = (False, None)

    def no_progress(self, movements: list[str]) -> bool:

        return not movements and not any(
            drone.status == "in_transit" for drone in self.drones
        )

    def display_turn(self, movements: list[str]) -> None:

        if self.debug:

            waiting = [
                drone.drone_id
                for drone in self.drones
                if drone.status == "waiting"
            ]

            print(f"Turn {self.turn}: " + " ".join(movements))

            if waiting:

                print("Waiting:", ", ".join(waiting))

        else:

            print(f"Turn {self.turn:>3}: " + " ".join(movements))

    def _record_tour(self) -> None:

        tour_data: dict[str, str] = {}

        drone_states: dict[str, dict[str, object]] = {}

        for drone in self.drones:

            if drone.current_zone:

                tour_data[drone.drone_id] = drone.current_zone.name

            conn = drone.moving_connection[1]

            drone_states[drone.drone_id] = {
                "zone": (
                    drone.current_zone.name if drone.current_zone else None
                ),
                "status": drone.status,
                "transit_turns": drone.transit_turns,
                "connection": (
                    {
                        "source": conn.source.name,
                        "target": conn.target.name,
                    }
                    if conn
                    else None
                ),
            }

        self.tours.append(tour_data)

        self.replay_frames.append(
            {
                "turn": self.turn,
                "drones": drone_states,
                "zones": {
                    name: {
                        "count": zone.nb_drones,
                        "max": zone.max_drones,
                    }
                    for name, zone in self.graph.zones.items()
                },
                "connections": {
                    f"{c.source.name}->{c.target.name}": {
                        "count": c.nb_drones,
                        "max": c.max_capacity,
                    }
                    for c in self.graph.connections
                },
            }
        )

    def stop(self) -> None:

        pass

    def simulate(self) -> None:

        self.start()

        self.execute()

        self.stop()
