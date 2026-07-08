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
        # Ajoute un drone à la liste des drones de la simulation
        self.drones.append(drone)

    def load_drones(self, nb_drones: int) -> None:
        # Crée et ajoute un nombre donné de drones avec des identifiants séquentiels
        for i in range(nb_drones):
            self.add_drone(Drone(f"D{i + 1}"))

    def start(self) -> None:
        start = self.graph.start_zone
        pathfinder = Djikstra(self.graph)
        path = pathfinder.shortest_path() or []
        for drone in self.drones:
            drone.current_zone = start
            start.nb_drones += 1
            drone.path = list(path)[1:]

    def _try_move(self, drone: Drone) -> str | None:
        # Tente de déplacer le drone vers sa prochaine zone.
        # Retourne la description du mouvement ou None si impossible.
        next_zone = drone.path[0] if drone.path else None
        if next_zone is None:
            drone.status = "waiting"
            return None

        conn = self.graph.get_connection(drone.current_zone.name, next_zone.name)
        conn_ok = conn is None or conn.nb_drones < conn.max_capacity
        zone_ok = next_zone.nb_drones < next_zone.max_drones

        if zone_ok and conn_ok:
            if next_zone.zone_type == "restricted":
                drone.move_to_zone(next_zone, conn)
                drone.path.pop(0)
                drone.transit_turns = 0
                drone.status = "in_transit"
                return f"{drone.drone_id}-{next_zone.name}(transit)"
            else:
                drone.move_to_zone(next_zone, None)
                drone.path.pop(0)
                drone.status = "moving"
                if drone.current_zone == self.graph.end_zone:
                    drone.status = "finished"
                    if drone.entry_connection is not None:
                        drone.entry_connection.nb_drones -= 1
                        drone.entry_connection = None
                    drone.current_zone.nb_drones -= 1
                return f"{drone.drone_id}-{next_zone.name}"
        else:
            # Bloqué : cherche un voisin accessible plus proche ou aussi proche du goal
            pf = Djikstra(self.graph)
            goal_dist = pf.distance_to(next_zone.name, self.graph.end_zone.name)
            best_nbr = None
            best_conn = None
            best_dist = goal_dist
            for nc in self.graph.get_neighbors(drone.current_zone.name):
                nbr = nc.target if nc.source.name == drone.current_zone.name else nc.source
                if nbr.name == next_zone.name:
                    continue
                if nc.nb_drones >= nc.max_capacity:
                    continue
                if nbr.nb_drones >= nbr.max_drones:
                    continue
                d = pf.distance_to(nbr.name, self.graph.end_zone.name)
                if d <= best_dist:
                    best_dist = d
                    best_nbr = nbr
                    best_conn = nc
            if best_nbr is not None:
                new_path = pf.shortest_path(best_nbr.name)
                drone.path = [best_nbr] + (list(new_path)[1:] if new_path else [])
                return self._try_move(drone)
            else:
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
                drone.status = "moving"
                if drone.entry_connection is not None:
                    drone.entry_connection.nb_drones -= 1
                    drone.entry_connection = None

    def execute(self) -> None:
        while not all(drone.status == "finished" for drone in self.drones):
            self.turn += 1

            if self.turn > 200:
                print("DEADLOCK DETECTED — drones bloqués :")
                for d in self.drones:
                    if d.status != "finished":
                        print(f"  {d.drone_id} status={d.status} zone={d.current_zone} path={d.path[:3]}")
                break

            self.advance_transit()

            movements = []
            for drone in self.drones:
                if drone.status in ("finished", "in_transit"):
                    continue
                result = self._try_move(drone)
                if result:
                    movements.append(result)

            if self.debug:
                waiting = [
                    f"{d.drone_id}(waiting {d.current_zone})"
                    for d in self.drones
                    if d.status == "waiting"
                ]
                print(f"Turn {self.turn}: {' '.join(movements)}")
                if waiting:
                    print("Waiting:", ", ".join(waiting))
            else:
                print(f"Turn {self.turn:>3}: " + " ".join(movements))

    def stop(self) -> None:
        # Point d'arrêt de la simulation (extensible pour un nettoyage futur)
        pass

    def simulate(self) -> None:
        # Lance la simulation complète : initialisation, exécution puis arrêt
        self.start()
        self.execute()
        self.stop()
