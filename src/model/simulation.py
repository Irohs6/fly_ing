from .drone import Drone
from .graph import Graph
from .pathfinder import Dijkstra
from .error import Graph_Error


class Simulation:
    def __init__(self, graph: Graph, debug: bool,
                 pathfinder: Dijkstra | None = None) -> None:
        self.graph = graph
        self.drones: list[Drone] = []
        self.turn = 0
        self.debug = debug
        self.ph = pathfinder if pathfinder is not None else Dijkstra(graph)
        self.tours: list[dict[str, str]] = []  # Historique des positions
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
            raise Graph_Error("Start zone is not defined in the graph.")

        path = self.ph.shortest_path() or []

        for drone in self.drones:
            drone.current_zone = start
            start.add_nb_drone()
            drone.path = list(path)[1:]
            drone.status = "moving"
        # Enregistrer l'état initial (tour 0)
        self._record_tour()

    def _try_move(self, drone: Drone) -> str | None:
        # Tente de déplacer le drone vers sa prochaine zone.
        # Retourne la description du mouvement ou None si impossible.
        blocked_candidates: set[str] = set()
        max_iter = len(self.graph.zones) + 1

        for _ in range(max_iter):
            next_zone = drone.path[0] if drone.path else None
            if next_zone is None:
                drone.status = "waiting"
                return None

            conn = self.graph.get_connection(
                drone.current_zone.name, next_zone.name
            )

            if conn is None:
                drone.status = "waiting"
                return None

            conn_ok = conn.nb_drones < conn.max_capacity
            zone_ok = next_zone.nb_drones < next_zone.max_drones

            if zone_ok and conn_ok:
                drone.move_to_zone(next_zone, conn)
                conn.add_nb_drone()
                next_zone.add_nb_drone()  # réserve la place dès maintenant
                drone.path.pop(0)
                drone.moving_connection = (True, conn)

                if next_zone.zone_type == "restricted":
                    drone.status = "in_transit"
                    drone.transit_turns = 0
                    return f"{drone.drone_id}-{next_zone.name}(transit)"

                drone.status = "moving"
                if drone.current_zone == self.graph.end_zone:
                    drone.status = "finished"
                    drone.current_zone.remove_nb_drone()
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

        drone.status = "waiting"
        return None

    def advance_transit(self) -> None:
        for drone in self.drones:
            if drone.status != "in_transit":
                continue
            drone.transit_turns += 1
            zone_obj = drone.current_zone
            cost = zone_obj.move_cost() if zone_obj else 1
            if drone.transit_turns >= cost:
                drone.transit_turns = 0
                conn = drone.moving_connection[1]
                if conn:
                    conn.remove_nb_drone()
                drone.moving_connection = (False, None)
                # La place est déjà réservée depuis l'entrée en transit.
                drone.status = "moving"

    def execute(self) -> None:
        max_stall = len(self.drones) * len(self.graph.zones) + 1
        stalled_turns = 0
        while not all(drone.status == "finished" for drone in self.drones):
            self.turn += 1
            self.advance_transit()

            movements: list[str] = []
            used_connections: list[Drone] = []

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

            # Deadlock detection: if no drone moved and none are in transit,
            # no progress is possible.
            any_progress = bool(movements) or any(
                d.status == "in_transit" for d in self.drones
            )
            if not any_progress:
                stalled_turns += 1
                if stalled_turns >= max_stall:
                    raise Graph_Error(
                        f"Deadlock: no progress after {max_stall} "
                        f"stalled turns."
                    )
            else:
                stalled_turns = 0

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
        tour_data: dict[str, str] = {}
        drone_states: dict[str, dict[str, object]] = {}

        for drone in self.drones:
            if drone.current_zone:
                tour_data[drone.drone_id] = drone.current_zone.name

            conn = drone.moving_connection[1]
            drone_states[drone.drone_id] = {
                "zone": drone.current_zone.name if drone.current_zone else None,
                "status": drone.status,
                "transit_turns": drone.transit_turns,
                "connection": {
                    "source": conn.source.name,
                    "target": conn.target.name,
                } if conn is not None else None,
            }

        self.tours.append(tour_data)
        self.replay_frames.append({
            "turn": self.turn,
            "drones": drone_states,
            "zones": {
                name: {"count": zone.nb_drones, "max": zone.max_drones}
                for name, zone in self.graph.zones.items()
            },
            "connections": {
                f"{c.source.name}->{c.target.name}": {
                    "source": c.source.name,
                    "target": c.target.name,
                    "count": c.nb_drones,
                    "max": c.max_capacity,
                }
                for c in self.graph.connections
            },
        })

    def stop(self) -> None:
        # Point d'arrêt de la simulation (extensible pour un nettoyage futur)
        pass

    def simulate(self) -> None:
        # Lance la simulation complète : initialisation, exécution puis arrêt
        self.start()
        self.execute()
        self.stop()
