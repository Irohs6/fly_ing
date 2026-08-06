from src.model.graph import Graph
from src.model.pathfinder import Dijkstra
from src.view.pygame_view import Pygame_view
from src.parser.parser import Parser
from src.model.simulation import Simulation


class Controller:
    def __init__(self, file_path: str, debug: bool = False) -> None:
        self.file_path = file_path
        self.debug = debug

        self.graph: Graph | None = None
        self.simulation: Simulation | None = None

        self._initialize()
        assert self.graph is not None
        self.view = Pygame_view(self.graph, simulation=self.simulation)

    def _initialize(self) -> None:
        parser = Parser(self.file_path)
        nb_drones, start_hub, end_hub, hubs, connections = parser.parse()

        self.graph = Graph()
        self.graph.load_zones(start_hub, end_hub, hubs)
        self.graph.load_connections(connections)

        if not self.graph.valid_path():
            raise ValueError("No valid path from start to end zone.")

        pathfinder = Dijkstra(self.graph)
        self.simulation = Simulation(
            self.graph, debug=self.debug, pathfinder=pathfinder
        )
        self.simulation.load_drones(nb_drones["value"])
        self.simulation.simulate()

    def run(self) -> None:
        if self.view is not None:
            self.view.display()
