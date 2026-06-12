"""
Fichier  : src/pathfinding/heuristic.py
========================================

RÔLE
----
Fournir la fonction heuristique h(n) utilisée par A* pour estimer le
coût restant entre un nœud courant et le nœud destination.

Une bonne heuristique est :
  - Admissible   : ne surestime jamais le coût réel (garantit l'optimalité)
  - Consistante  : h(n) ≤ cost(n→n') + h(n') pour tout voisin n'
                   (garantit qu'on ne repousse pas un nœud déjà visité)

Dans ce projet, les coordonnées (x, y) sont en grille entière,
et le coût minimal d'un déplacement est 1 (zone normale).
La distance de Manhattan est donc une heuristique admissible naturelle.

ENTRÉES
-------
- node_name    : str         → nom du hub courant
- target_name  : str         → nom du hub destination (end_hub)
- node_meta    : dict        → issu de GraphAdapter, contient les (x, y)
                               de chaque hub

SORTIES
-------
- h : float  → estimation du coût minimal pour aller de node à target

FONCTIONS À IMPLÉMENTER
-----------------------

1. manhattan(node_name, target_name, node_meta) → float
   ---------------------------------------------------
   Calcule |x_node - x_target| + |y_node - y_target|.
   Adaptée quand les déplacements sont uniquement horizontaux/verticaux.
   Coût minimal supposé = 1 par case.

2. euclidean(node_name, target_name, node_meta) → float
   -----------------------------------------------------
   Calcule sqrt((x_node - x_target)² + (y_node - y_target)²).
   Adaptée si les connexions peuvent être diagonales.
   Légèrement sous-estimée par rapport à Manhattan → toujours admissible.

3. zero(node_name, target_name, node_meta) → float
   -------------------------------------------------
   Retourne toujours 0.
   Transforme A* en Dijkstra (optimal mais plus lent).
   Utile pour le débogage ou les petits graphes.

LOGIQUE DE CHOIX
----------------
- Dans Fly-in, la grille est carrée et les connexions semblent orthogonales
  → Manhattan est le choix par défaut recommandé.
- Si des connexions "en diagonale" existent dans le graphe,
  passer en euclidean.
- La fonction active est injectée dans AStarSolver au moment de
  sa construction, via un paramètre `heuristic_fn`.

INTERACTIONS
------------
- Appelé à chaque itération de A* dans AStarSolver
- Lit node_meta depuis GraphAdapter (coordonnées x, y)
- Ne modifie aucun état → fonctions pures

EDGE CASES IMPORTANTS
---------------------
- Si un hub n'a pas de coordonnées dans node_meta → retourner 0
  (dégradation gracieuse en Dijkstra pour ce nœud)
- Si node == target → retourner 0 immédiatement
- Les coordonnées sont des entiers (pas de sous-grille) → pas de flottants
  dans le calcul Manhattan
"""

from typing import Callable

HeuristicFunction = Callable[[str, str, dict], float]


class Heuristic:

    @staticmethod
    def manhattan(node_name: str, target_name: str, node_meta: dict) -> float:
        node_info = node_meta.get(node_name)
        target_info = node_meta.get(target_name)
        if not node_info or not target_info:
            return 0  # Dégradation gracieuse
        x1, y1 = node_info.x, node_info.y
        x2, y2 = target_info.x, target_info.y
        return abs(x1 - x2) + abs(y1 - y2)

    @staticmethod
    def euclidean(node_name: str, target_name: str, node_meta: dict) -> float:
        node_info = node_meta.get(node_name)
        target_info = node_meta.get(target_name)
        if not node_info or not target_info:
            return 0  # Dégradation gracieuse
        x1, y1 = node_info.x, node_info.y
        x2, y2 = target_info.x, target_info.y
        return ((x1 - x2) ** 2 + (y1 - y2) ** 2) ** 0.5

    @staticmethod
    def zero(node_name: str, target_name: str, node_meta: dict) -> float:
        return 0
