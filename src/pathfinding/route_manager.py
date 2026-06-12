"""
Fichier  : src/pathfinding/route_manager.py
============================================

RÔLE
----
Interface principale du module de pathfinding.
RouteManager est le seul objet que la Simulation doit instancier et appeler.
Il orchestre tous les autres composants (GraphAdapter, CostModel,
AStarSolver, PathGenerator) et expose une API simple à la Simulation.

C'est le "chef d'orchestre" : il assemble les dépendances, les injecte
dans les bons endroits, et expose des méthodes de haut niveau.

ENTRÉES (constructeur)
-----------------------
- graph : Graph   → le graphe complet du projet

MÉTHODES PUBLIQUES
------------------

1. prepare() → None
   ----------------
   Initialise tous les composants internes.
   Doit être appelée une fois après la construction, avant tout calcul.

   Logique :
       a. Créer un GraphAdapter à partir du graph.
       b. Créer un CostModel.
       c. Créer un AStarSolver avec l'adapter, le cost_model,
          et la fonction heuristique (manhattan par défaut).
       d. Créer un PathGenerator avec le solver.

2. compute_routes(nb_drones: int) → list[ list[str] ]
   ---------------------------------------------------
   Génère autant de routes que nécessaire pour nb_drones drones.
   Retourne une liste de chemins (un par drone si possible).

   Logique :
       a. Appeler PathGenerator.generate(start, end, k=nb_drones).
       b. Si moins de K chemins sont disponibles, certains drones
          partageront le même chemin.
          → Répéter les chemins disponibles en round-robin pour
            atteindre nb_drones routes.
       c. Retourner la liste finale de nb_drones routes.

   Exemple avec 5 drones et 2 chemins disponibles :
       Drone 1 → chemin A
       Drone 2 → chemin B
       Drone 3 → chemin A
       Drone 4 → chemin B
       Drone 5 → chemin A

3. assign_routes(drones: list[Drone]) → None
   ------------------------------------------
   Calcule les routes et les assigne directement aux objets Drone.

   Logique :
       a. Appeler compute_routes(len(drones)).
       b. Pour chaque drone à l'index i :
            drone.path = routes[i]

   Note : cela suppose que l'objet Drone possède un attribut `path`.

4. get_best_path() → list[str] | None
   ------------------------------------
   Retourne uniquement le meilleur chemin (coût minimal) sans gestion
   de flotte. Utile pour le débogage ou les cas à un seul drone.

INTERACTIONS
------------
- Instancié et appelé par Simulation (src/model/simulation.py)
- Crée et possède : GraphAdapter, CostModel, AStarSolver, PathGenerator
- Lit : Graph, Zone, Connection (via GraphAdapter)
- Écrit sur : Drone.path (via assign_routes)

STRUCTURES DE DONNÉES INTERNES
--------------------------------
- _adapter       : GraphAdapter
- _cost_model    : CostModel
- _solver        : AStarSolver
- _generator     : PathGenerator
- _routes_cache  : list[list[str]] | None
      Cache des dernières routes calculées.
      Invalidé si le graphe change (mais dans ce projet le graphe est statique,
      donc le cache est toujours valide une fois calculé).

EDGE CASES IMPORTANTS
---------------------
- prepare() non appelée avant compute_routes() → lever une RuntimeError
  avec message explicite ("RouteManager not prepared")
- Aucun chemin possible (graphe disconnecté) → compute_routes retourne []
  et assign_routes ne modifie aucun drone
- nb_drones = 0 → retourner [] sans calcul
- graph.start_zone ou graph.end_zone est None → lever une ValueError
  ("Graph has no start or end zone defined")
- Le cache évite de recalculer les routes si assign_routes est appelé
  plusieurs fois (scénario de reset de simulation)
"""
class RouteManager:

    def __init__(self, graph):
        self.graph = graph
        self._adapter = None
        self._cost_model = None
        self._solver = None
        self._generator = None
        self._routes_cache = None

    def prepare(self):
        self._adapter = GraphAdapter(self.graph)
        self._cost_model = CostModel()
        self._solver = AStarSolver(
            adapter=self._adapter,
            cost_model=self._cost_model,
            heuristic_fn=self.manhattan_heuristic,
        )
        self._generator = PathGenerator(solver=self._solver)

    def compute_routes(self, nb_drones: int) -> list[list[str]]:
        if self._generator is None:
            raise RuntimeError("RouteManager not prepared. Call prepare() first.")
        if nb_drones <= 0:
            return []

        start_zone = self.graph.start_zone
        end_zone = self.graph.end_zone
        if start_zone is None or end_zone is None:
            raise ValueError("Graph has no start or end zone defined.")

        # Si les routes sont déjà calculées, les retourner depuis le cache
        if self._routes_cache is not None:
            return self._routes_cache[:nb_drones]

        # Générer les routes avec PathGenerator
        routes = self._generator.generate(start_zone.name, end_zone.name, nb_drones)

        # Si moins de K routes sont disponibles, répéter en round-robin
        if len(routes) < nb_drones:
            full_routes = []
            for i in range(nb_drones):
                full_routes.append(routes[i % len(routes)])
            routes = full_routes

        # Cacher les routes calculées pour réutilisation future
        self._routes_cache = routes

        return routes
