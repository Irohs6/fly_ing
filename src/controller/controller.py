from src.model.graph import Graph
from src.view.pygame_view import Pygame_view
from src.parser.parser import Parser
from src.model.simulation import Simulation


class Controller:
    def __init__(self, file_path: str, debug: bool = False) -> None:
        self.file_path = file_path
        self.debug = debug
        self.config = None
        self.graph = Graph()
        self.load_config()
        self.view = Pygame_view(self.graph)

    def load_config(self) -> None:
        parser = Parser(self.file_path)
        parser.parse()
        self.config = parser.config
        self.graph = Graph()
        self.graph.load_zones(self.config)
        self.graph.load_connections(self.config)
        simulation = Simulation(self.graph, debug=self.debug)
        simulation.load_drones(self.config["nb_drones"])
        simulation.simulate()

    def display(self) -> None:
        self.view.display()
