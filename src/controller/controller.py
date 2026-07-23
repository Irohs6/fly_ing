from src.model.graph import Graph
from src.view.pygame_view import Pygame_view
from src.parser.parser import Parser
from src.model.simulation import Simulation


class Controller:
    def __init__(self, file_path: str, debug: bool = False) -> None:
        self.file_path = file_path
        self.debug = debug
        self.config = None
        self.graph = None
        self.simulation = None
        self.load_config()
        self.view = Pygame_view(self.graph, simulation=self.simulation)

    def load_config(self) -> None:
        parser = Parser(self.file_path)
        self.config = parser.parse()
        self.graph = Graph()
        self.graph.load_zones(self.config)
        self.graph.load_connections(self.config)
        if not self.graph.valid_path():
            raise ValueError("No valid path from start to end zone.")
        self.simulation = Simulation(self.graph, debug=self.debug)
        self.simulation.load_drones(self.config["nb_drones"])
        self.simulation.simulate()

    def display(self) -> None:
        self.view.display()
