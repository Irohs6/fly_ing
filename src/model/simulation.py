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
        # Initialise la simulation : calcule le chemin optimal et positionne chaque drone sur la zone de départ
        start = self.graph.start_zone
        pathfinder = Djikstra(self.graph)
        path = pathfinder.shortest_path() or []
        for drone in self.drones:
            drone.current_zone = start
            start.nb_drones += 1
            drone.path = list(path)[
                1:
            ]  # on ignore la zone de départ (déjà présent)

    def plan_moves(self) -> list[tuple[Drone, Zone | None]]:
        # Planifie le prochain mouvement de chaque drone actif (ignore ceux qui ont terminé)
        # Retourne une liste de tuples (drone, prochaine_zone) où prochaine_zone peut être None si le drone est bloqué
        planned_moves = []
        for drone in self.drones:

            if drone.status in ("finished", "in_transit"):
                continue

            # Récupère le nom de la prochaine zone dans le chemin du drone
            next_zone_name = drone.path[0] if drone.path else None
            next_zone = (
                self.graph.zones[next_zone_name] if next_zone_name else None
            )
            planned_moves.append((drone, next_zone))

        return planned_moves

    def resolve_conflicts(
        self, planned_moves: list[tuple[Drone, Zone | None]]
    ) -> list[tuple[Drone, Zone | None]]:
        # Résout les conflits de capacité : si une zone est pleine, le drone est bloqué (None)
        resolved_moves = []

        # Capacité des zones : lit nb_drones mais exclut les drones finished
        # qui ne bloquent plus la zone
        finished_per_zone: dict[str, int] = {}
        for d in self.drones:
            if d.status == "finished" and d.current_zone is not None:
                finished_per_zone[d.current_zone.name] = (
                    finished_per_zone.get(d.current_zone.name, 0) + 1
                )
        zone_capacity: dict[str, int] = {
            name: max(0, zone.nb_drones - finished_per_zone.get(name, 0))
            for name, zone in self.graph.zones.items()
        }

        # Suivi de l'usage prévu des connexions CE tour (conn.nb_drones reflète le transit existant)
        conn_planned: dict[int, int] = {}

        for drone, next_zone in planned_moves:
            if next_zone is None:
                resolved_moves.append((drone, None))
                continue

            conn = self.graph.get_connection(
                drone.current_zone.name, next_zone.name
            )
            # conn.nb_drones = drones en transit via cette connexion (persistant entre tours)
            # conn_planned  = usage supplémentaire prévu ce tour
            conn_current = (
                (conn.nb_drones if conn else 0)
                + conn_planned.get(id(conn), 0)
            )
            conn_ok = conn is None or conn_current < conn.max_capacity

            if zone_capacity[next_zone.name] < next_zone.max_drones and conn_ok:
                zone_capacity[next_zone.name] += 1
                zone_capacity[drone.current_zone.name] -= 1
                if conn is not None:
                    conn_planned[id(conn)] = conn_planned.get(id(conn), 0) + 1
                resolved_moves.append((drone, next_zone))
            else:
                # Zone ou connexion pleine : recalcule un chemin alternatif
                pathfinder = Djikstra(self.graph)
                new_path = pathfinder.shortest_path(
                    drone.current_zone.name, blocked_zone=next_zone.name)
                if new_path is not None:
                    drone.path = list(new_path)[1:]
                # si new_path is None : on conserve le chemin, la zone se libèrera
                drone.status = "waiting"
                resolved_moves.append((drone, None))

        return resolved_moves

    def apply_moves(
        self, planned_moves: list[tuple[Drone, Zone | None]]
    ) -> list[str]:
        # Applique les mouvements résolus : déplace les drones, marque ceux arrivés à destination
        # Retourne la liste des mouvements effectués sous forme "ID-zone"
        movements: list[str] = []

        for drone, next_zone in planned_moves:
            if next_zone is not None:
                if next_zone.zone_type == "restricted":
                    # Entrée dans une zone restreinte : transit de 2 tours
                    # La connexion reste occupée pendant tout le transit
                    conn = self.graph.get_connection(
                        drone.current_zone.name, next_zone.name
                    )
                    drone.move_to_zone(next_zone, conn)
                    drone.path.pop(0)
                    drone.transit_turns = 0
                    drone.status = "in_transit"
                    movements.append(
                        f"{drone.drone_id}-{next_zone.name}(transit)"
                    )
                    continue
                # Déplacement normal : la connexion est libérée immédiatement
                conn = self.graph.get_connection(
                    drone.current_zone.name, next_zone.name
                )
                drone.move_to_zone(next_zone, None)
                # libère la connexion : elle n'est utilisée qu'un seul tour
                if conn is not None:
                    conn.nb_drones -= 1
                drone.path.pop(0)
                drone.status = "moving"

                # Si le drone atteint la zone de fin, il est marqué comme terminé
                if drone.current_zone == self.graph.end_zone:
                    drone.status = "finished"
                    # Libère connexion + ne bloque plus la zone pour les suivants
                    if drone.entry_connection is not None:
                        drone.entry_connection.nb_drones -= 1
                        drone.entry_connection = None
                    drone.current_zone.nb_drones -= 1
                movements.append(f"{drone.drone_id}-{next_zone.name}")
            else:
                # Aucun mouvement possible ce tour : le drone attend
                drone.status = "waiting"
        return movements

    def advance_transit(self) -> None:
        # Avance le compteur des drones en transit ; les libère quand le coût est atteint
        for drone in self.drones:
            if drone.status != "in_transit":
                continue
            drone.transit_turns += 1
            zone_obj = drone.current_zone
            cost = zone_obj.move_cost() if zone_obj else 1
            if drone.transit_turns >= cost:
                drone.transit_turns = 0
                drone.status = "moving"
                # Libère la connexion d'entrée : le transit est terminé
                if drone.entry_connection is not None:
                    drone.entry_connection.nb_drones -= 1
                    drone.entry_connection = None

    def execute(self) -> None:
        # Boucle principale : exécute les tours jusqu'à ce que tous les drones aient terminé
        while not all(drone.status == "finished" for drone in self.drones):
            self.turn += 1

            planned_moves = self.plan_moves()
            planned_moves = self.resolve_conflicts(planned_moves)
            movements = self.apply_moves(planned_moves)
            self.advance_transit()

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
