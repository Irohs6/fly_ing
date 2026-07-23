from .drone import Drone
from .graph import Graph
from .pathfinder import Dijktra


class Simulation:
    def __init__(self, graph: Graph, debug: bool) -> None:
        self.graph = graph
        self.drones: list[Drone] = []
        self.turn = 0
        self.debug = debug
        self.ph = Dijktra(graph)
        self.tours: list[dict[str, str]] = []  # Historique des positions

    def add_drone(self, drone: Drone) -> None:
        # Ajoute un drone à la liste des drones de la simulation
        self.drones.append(drone)

    def load_drones(self, nb_drones: int) -> None:
        for i in range(nb_drones):
            self.add_drone(Drone(f"D{i + 1}"))

    def start(self) -> None:
        start = self.graph.start_zone
        path = self.ph.shortest_path() or []
        for drone in self.drones:
            drone.current_zone = start
            start.nb_drones += 1
            drone.path = list(path)[1:]
        # Enregistrer l'état initial (tour 0)
        self._record_tour()

    def _try_move(self, drone: Drone) -> str | None:
        # Tente de déplacer le drone vers sa prochaine zone.
        # Retourne la description du mouvement ou None si impossible.
        blocked_candidates: set[str] = set()

        while True:
            next_zone = drone.path[0] if drone.path else None
            if next_zone is None:
                drone.status = "waiting"
                return None

            conn = self.graph.get_connection(
                drone.current_zone.name, next_zone.name
            )
            conn_ok = conn is None or conn.nb_drones < conn.max_capacity
            zone_ok = next_zone.nb_drones < next_zone.max_drones

            if zone_ok and conn_ok:
                if next_zone.zone_type == "restricted":
                    drone.move_to_zone(next_zone, conn)
                    drone.moving_connection = (True, conn)
                    if conn:
                        conn.add_nb_drone()
                    drone.path.pop(0)
                    drone.transit_turns = 0
                    drone.status = "in_transit"
                    return f"{drone.drone_id}-{next_zone.name}(transit)"

                drone.move_to_zone(next_zone, conn)
                if conn:
                    conn.add_nb_drone()
                drone.path.pop(0)
                drone.moving_connection = (True, conn)
                drone.status = "moving"
                if drone.current_zone == self.graph.end_zone:
                    drone.status = "finished"
                    drone.current_zone.nb_drones -= 1
                return f"{drone.drone_id}-{next_zone.name}"

            if next_zone.zone_type == "priority":
                drone.status = "waiting"
                return None

            blocked_candidates.add(next_zone.name)
            new_path = self.ph.shortest_path(
                source=drone.current_zone.name,
                blocked_zones=blocked_candidates,
            )
            if not new_path or len(new_path) <= 1:
                drone.status = "waiting"
                return None
            drone.path = new_path[1:]

    def advance_transit(self) -> None:
        for drone in self.drones:
            if drone.status != "in_transit":
                continue
            drone.transit_turns += 1
            zone_obj = drone.current_zone
            cost = zone_obj.move_cost() if zone_obj else 1
            if drone.transit_turns >= cost:
                drone.transit_turns = 0
                if drone.moving_connection[1]:
                    drone.moving_connection[1].remove_nb_drone()
                    drone.moving_connection = (False, None)
                    drone.status = "moving"

    def execute(self) -> None:
        while not all(drone.status == "finished" for drone in self.drones):
            self.turn += 1
            self.advance_transit()

            movements = []
            used_connections = []
            for drone in self.drones:
                if drone.status in ("finished", "in_transit"):
                    continue
                result = self._try_move(drone)

                if result:
                    movements.append(result)

                if drone.moving_connection[0]:
                    used_connections.append(drone)
            for drone in used_connections:
                if drone.status != "in_transit":
                    conn = drone.moving_connection[1]
                    if conn:
                        conn.remove_nb_drone()
                    drone.moving_connection = (False, None)

            if self.debug:
                waiting = [
                    f"{d.drone_id}(waiting {d.current_zone} "
                    f"{d.moving_connection[1]})"
                    for d in self.drones
                    if d.status == "waiting"
                ]
                print(f"Turn {self.turn}: {' '.join(movements)}")
                if waiting:
                    print("Waiting:", ", ".join(waiting))
            else:
                print(f"Turn {self.turn:>3}: " + " ".join(movements))

            # Enregistrer l'état du tour
            self._record_tour()

    def _record_tour(self) -> None:
        """Enregistre la position de chaque drone pour le tour courant."""
        tour_data = {}
        for drone in self.drones:
            if drone.current_zone:
                tour_data[drone.drone_id] = drone.current_zone.name
        self.tours.append(tour_data)

    def stop(self) -> None:
        # Point d'arrêt de la simulation (extensible pour un nettoyage futur)
        pass

    def simulate(self) -> None:
        # Lance la simulation complète : initialisation, exécution puis arrêt
        self.start()
        self.execute()
        self.stop()
