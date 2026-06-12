"""
Fichier  : src/pathfinding/cost_model.py
=========================================

Calcule le coût réel g(n → n') d'un déplacement entre deux hubs.
Le coût est basé sur le zone_type de la zone CIBLE :
    normal     → 1  |  restricted → 2  |  priority → 1  |  blocked → inf

Un malus optionnel (1 / max_capacity) peut être activé pour favoriser
les connexions à grande capacité lors de la répartition des drones.
"""

from .graph_adapter import GraphAdapter


class CostModel:
    ZONE_COST = {
        "normal": 1,
        "restricted": 2,
        "priority": 1,
        "blocked": float("inf"),
    }

    def __init__(self, capacity_malus_enabled: bool = False):
        self.capacity_malus_enabled = capacity_malus_enabled

    def compute_cost(
        self,
        source_name: str,
        target_name: str,
        edge_info: "GraphAdapter.EdgeInfo",
        node_meta: dict,
    ) -> float:

        # Étape 1 : Coût de base lié au type de la zone cible
        target_meta = node_meta.get(target_name)
        zone_type = target_meta.zone_type if target_meta else "normal"
        base_cost = self.ZONE_COST.get(zone_type, 1)

        # Si la zone est bloquée, retourner infini immédiatement
        if base_cost == float("inf"):
            return float("inf")

        # Étape 2 : Malus optionnel lié à la capacité de la connexion
        malus = 0
        if self.capacity_malus_enabled:
            max_capacity = edge_info.max_capacity
            if max_capacity <= 0:
                return float("inf")  # Connexion inutilisable
            malus = 1 / max_capacity

        return base_cost + malus
