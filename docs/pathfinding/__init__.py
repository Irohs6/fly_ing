"""
Module : src/pathfinding
========================

Point d'entrée du module de pathfinding du projet Fly-in.

Ce module expose les éléments publics utiles au reste de l'application :
    - RouteManager  : interface principale à utiliser par la Simulation
    - PathGenerator : génération de chemins alternatifs
    - AStarSolver   : algorithme A* brut
    - CostModel     : modèle de coûts de déplacement
    - Heuristic     : fonctions heuristiques pour A*
    - GraphAdapter  : vue navigable du graphe (liste d'adjacence + capacités)

Flux général d'utilisation
--------------------------
1. La Simulation crée un RouteManager en lui passant le Graph.
2. RouteManager demande à GraphAdapter de préparer une représentation
   interne du graphe navigable.
3. RouteManager appelle PathGenerator pour obtenir N chemins entre
   start_hub et end_hub.
4. PathGenerator appelle AStarSolver plusieurs fois avec des contraintes
   différentes (yen's algorithm ou variante) pour obtenir des alternatives.
5. AStarSolver utilise CostModel pour pondérer les arêtes et Heuristic
   pour estimer la distance restante.
6. RouteManager reçoit la liste de chemins et les distribue aux drones.

Dépendances externes au module
-------------------------------
- src.model.graph.Graph     : source de vérité du graphe
- src.model.zone.Zone       : informations sur les hubs (type, capacité)
- src.model.connection.Connection : informations sur les arêtes (capacité)
"""
