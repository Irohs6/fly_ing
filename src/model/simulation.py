from .drone import Drone
from .graph import Graph


class Simulation:
    def __init__(self, graph: Graph) -> None:
        self.graph = graph
        self.drones: list[Drone] = []

    def add_drone(self, drone: Drone) -> None:
        self.drones.append(drone)

    def load_drones(self, nb_drones: int) -> None:
        for i in range(nb_drones):
            self.add_drone(Drone(f"D{i + 1}"))

    def start(self) -> None:
        pass