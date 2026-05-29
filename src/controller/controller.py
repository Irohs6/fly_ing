from src.model.graph import Graph
from src.view.view import View
from src.model.simulation import Simulation
from src.parser.parser import Parser


class Controller:
    def __init__(self, file_path: str) -> None:
        config = Parser(file_path).parse()
        self.graph = self.__create_graph()
        self.simulation = self.__create_simulation()
        self.view = self.__create_view()
        self.graph.load_zones(config)
        self.graph.load_connections(config)
        self.simulation.load_drones(config["nb_drones"])

    def __create_graph(self) -> Graph:
        return Graph()

    def __create_simulation(self) -> Simulation:
        return Simulation(self.graph)

    def __create_view(self) -> View:
        return View(self.simulation)

    def start_simulation(self) -> None:
        self.simulation.start()
