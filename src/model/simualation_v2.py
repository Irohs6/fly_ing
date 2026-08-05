from .drone import Drone
from .graph import Graph
from .pathfinder import Dijkstra
from .error import GraphError
from .zone import Zone


class Simulation:
    def __init__(self, graph: Graph, debug: bool,
                 pathfinder: Dijkstra | None = None) -> None:
        self.graph = graph
        self.drones: list[Drone] = []
        self.turn = 0
        self.debug = debug
        self.ph = pathfinder if pathfinder is not None else Dijkstra(graph)
        self.replay_frames: list[dict[str, object]] = []

    def add_drone(self, drone: Drone) -> None:
        # Ajoute un drone à la liste des drones de la simulation
        self.drones.append(drone)

    def load_drones(self, nb_drones: int) -> None:
        for i in range(nb_drones):
            self.add_drone(Drone(f"D{i + 1}"))

    def start(self) -> None:
        start = self.graph.start_zone
        if start is None:
            raise GraphError("Start zone is not defined in the graph.")

        path = self.ph.shortest_path() or []

        for drone in self.drones:
            drone.current_zone = start
            start.add_nb_drone()
            drone.path = list(path)[1:]
            drone.status = "moving"
        # Enregistrer l'état initial (tour 0)
        self._record_tour()

    def _reroute(self, drone: Drone, blocked_zone: Zone) -> str | None:
        """
        Try to find a new path avoiding a blocked zone.

        Args:
            drone: Drone that needs a new route.
            blocked_zone: Zone currently preventing movement.

        Returns:
            None because the drone does not move this turn.
        """

        new_path = self.ph.shortest_path(
            source=drone.current_zone.name,
            blocked_zones={blocked_zone.name},
        )

        # Aucun nouveau chemin possible
        if not new_path or len(new_path) <= 1:
            drone.wait()
            return None

        # On retire la zone actuelle du chemin
        drone.path = new_path[1:]

        return None

    def _try_move(self, drone: Drone) -> str | None:
        next_zone = drone.next_zone()

        if next_zone is None:
            drone.finish_if_arrived(self.graph.end_zone)
            return None

        conn = self.graph.get_connection(
            drone.current_zone.name,
            next_zone.name
        )

        if conn is None:
            drone.wait()
            return None

        if not next_zone.can_accept_drone():
            return self._reroute(drone, next_zone)

        if not conn.can_accept_drone():
            return self._reroute(drone, next_zone)

        drone.enter_zone(next_zone, conn)

        if next_zone.zone_type == "restricted":
            drone.start_transit()

        if drone.current_zone == self.graph.end_zone:
            drone.status = "finished"

        return f"{drone.drone_id}-{next_zone.name}"
