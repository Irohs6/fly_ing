from src.model.graph import Graph
from src.model.pathfinder import Dijkstra
from src.view.pygame_view import Pygame_view
from src.parser.parser import Parser
from src.model.simulation import Simulation


class Controller:
    def __init__(self, file_path: str, debug: bool = False) -> None:
        self.file_path = file_path
        self.debug = debug

        self.config: dict | None = None
        self.graph: Graph | None = None
        self.simulation: Simulation | None = None

        self._initialize()
        self.view = Pygame_view(self.graph, simulation=self.simulation)

    def _initialize(self) -> None:
        parser = Parser(self.file_path)
        self.config = parser.parse()

        self.graph = Graph()
        self.graph.load_zones(self.config)
        self.graph.load_connections(self.config)

        if not self.graph.valid_path():
            raise ValueError("No valid path from start to end zone.")

        pathfinder = Dijkstra(self.graph)
        self.simulation = Simulation(
            self.graph, debug=self.debug, pathfinder=pathfinder
        )
        self.simulation.load_drones(self.config["nb_drones"])
        self.simulation.simulate()

    def run(self) -> None:
        if self.view is not None:
            self.view.display()
