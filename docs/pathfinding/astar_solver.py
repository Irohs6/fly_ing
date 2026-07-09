from .cost_model import CostModel
from .graph_adapter import GraphAdapter
from .heuristic import HeuristicFunction
import heapq


class AStarSolver:
    def __init__(
        self,
        adapter: GraphAdapter,
        cost_model: CostModel,
        heuristic_fn: HeuristicFunction,
    ):
        self.adapter = adapter
        self.cost_model = cost_model
        self.heuristic_fn = heuristic_fn

    def solve(
        self, start: str, end: str, excluded_edges: set[tuple[str, str]]
    ) -> tuple[list[str] | None, float | None]:
        if start == end:
            return [start], 0

        if (
            start not in self.adapter.node_meta
            or end not in self.adapter.node_meta
        ):
            return None, None

        open_set: list[tuple[float, str]] = []

        came_from: dict[str, str] = {}

        g_score: dict[str, float] = {start: 0}
        f_score: dict[str, float] = {
            start: self.heuristic_fn(start, end, self.adapter.node_meta)
        }

        heapq.heappush(open_set, (f_score[start], start))

        while open_set:
            current_f, current = heapq.heappop(open_set)

            if current_f != f_score.get(current, float("inf")):
                continue
            if current == end:
                path = self._reconstruct_path(came_from, current)
                return path, g_score[current]

            for edge in self.adapter.get_neighbors(current):
                neighbor = edge.target

                if (current, neighbor) in excluded_edges or (
                    neighbor,
                    current,
                ) in excluded_edges:
                    continue

                tentative_g = g_score.get(
                    current, float("inf")
                ) + self.cost_model.compute_cost(
                    current, neighbor, edge, self.adapter.node_meta
                )

                if tentative_g < g_score.get(neighbor, float("inf")):
                    came_from[neighbor] = current
                    g_score[neighbor] = tentative_g

                    f_score[neighbor] = tentative_g + self.heuristic_fn(
                        neighbor, end, self.adapter.node_meta
                    )

                    heapq.heappush(open_set, (f_score[neighbor], neighbor))
        return None, None

    def _reconstruct_path(
        self, came_from: dict[str, str], current: str
    ) -> list[str]:
        # Reconstruit le chemin de end à start en utilisant came_from
        path = [current]
        while current in came_from:
            current = came_from[current]
            path.append(current)
        path.reverse()
        return path
