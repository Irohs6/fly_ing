"""
Fichier  : src/pathfinding/path_generator.py
=============================================

RÔLE
----
Générer plusieurs chemins alternatifs entre start_hub et end_hub,
en s'appuyant sur AStarSolver appelé de façon répétée avec des
contraintes progressivement plus restrictives.

Ce fichier répond à la question :
"Comment trouver K chemins différents pour répartir les drones ?"

L'algorithme utilisé est une version simplifiée de Yen's K-Shortest Paths.

ENTRÉES
-------
- start     : str           → nom du hub de départ
- end       : str           → nom du hub d'arrivée
- k         : int           → nombre de chemins alternatifs souhaités
- solver    : AStarSolver   → instance d'AStarSolver à réutiliser

SORTIES
-------
- paths : list[ list[str] ]
      Liste de K chemins (ou moins si le graphe ne permet pas K chemins).
      Chaque chemin est une liste ordonnée de noms de hubs.
      Exemple :
          [
              ["start", "A", "C", "end"],
              ["start", "B", "D", "end"],
              ["start", "A", "D", "end"],
          ]

ALGORITHME : VARIANTE SIMPLIFIÉE DE YEN'S K-SHORTEST PATHS
------------------------------------------------------------

Objectif : Trouver K chemins distincts en évitant les répétitions de routes.

Étape 1 — Trouver le chemin optimal (chemin 1) :
    Appeler solver.solve(start, end, excluded_edges=set()).
    Si aucun chemin → retourner liste vide.
    Ajouter ce chemin à la liste results.

Étape 2 — Pour chaque chemin supplémentaire i de 2 à K :
    Pour chaque arête (u, v) du dernier chemin trouvé :
        a. Créer excluded_edges contenant (u, v).
        b. Appeler solver.solve(start, end, excluded_edges).
        c. Si un chemin valide est trouvé ET qu'il n'est pas déjà dans results :
             - L'ajouter à un ensemble de chemins candidats.

    Parmi les candidats, sélectionner celui avec le coût total le plus bas.
    L'ajouter à results.
    Si aucun candidat → s'arrêter (plus de chemins possibles).

NOTE sur l'implémentation complète de Yen's :
    Yen's algorithmcomplet utilise un "spur node" qui varie à chaque itération
    et construit des "spur paths" + "root paths". La variante simplifiée
    ci-dessus est moins optimale mais plus simple à implémenter en premier.
    Elle peut être améliorée si les performances sont insuffisantes.

DÉDUPLICATION DES CHEMINS
--------------------------
Deux chemins sont considérés identiques si leurs listes de hubs sont égales.
Utiliser un set de tuples pour la comparaison rapide :
    seen = set()
    seen.add(tuple(path))
    if tuple(candidate) in seen → ignorer ce candidat

INTERACTIONS
------------
- Créé et appelé par RouteManager
- Dépend de AStarSolver pour chaque calcul de chemin
- Ne connaît pas directement GraphAdapter ou CostModel
  (délégués à AStarSolver)

STRUCTURES DE DONNÉES
---------------------
- results   : list[list[str]]    → chemins retenus dans l'ordre de qualité
- seen      : set[tuple[str]]    → pour la déduplication
- candidates: list[(cost, path)] → chemins candidats pour l'itération courante

EDGE CASES IMPORTANTS
---------------------
- K = 1 → simplement retourner le meilleur chemin A*
- Graphe avec peu d'arêtes → moins de K chemins possibles,
  retourner ce qu'on a trouvé sans erreur
- Chemins de même coût → les deux sont valides, garder les deux
- excluded_edges peut complètement couper start de end
  → solver retourne None → ce candidat est ignoré
- Si start == end → retourner [[ start ]] (chemin de longueur 1, coût 0)
"""

from .a_star_solver import AStarSolver


class PathGenerator:

    def __init__(self, solver: AStarSolver):
        self.solver = solver

    def generate(self, start: str, end: str, k: int) -> list[list[str]]:
        if k <= 0:
            return []
        if start == end:
            return [[start]]

        results = []
        seen = set()

        # Étape 1 : Trouver le chemin optimal
        best_path, _ = self.solver.solve(start, end, excluded_edges=set())
        if best_path is None:
            return []  # Aucun chemin possible
        results.append(best_path)
        seen.add(tuple(best_path))

        # Étape 2 : Trouver les chemins alternatifs
        for _ in range(1, k):
            candidates = []
            last_path = results[-1]

            # chaque arête du dernier chemin trouvé devient une "arête interdite"
            for i in range(len(last_path) - 1):
                root_path = last_path[: i + 1]

                excluded_edges = set()

                # bloquer les arêtes déjà utilisées dans les anciens chemins
                for path in results:
                    if len(path) > i and path[: i + 1] == root_path:
                        u = path[i]
                        v = path[i + 1]
                        excluded_edges.add((u, v))
                        excluded_edges.add((v, u))

                spur_path, cost = self.solver.solve(start, end, excluded_edges)

                if spur_path is None:
                    continue

                candidate_tuple = tuple(spur_path)

                if candidate_tuple in seen:
                    continue

                candidates.append((cost, spur_path))

            if not candidates:
                break

            # choisir le meilleur candidat
            candidates.sort(key=lambda x: x[0])
            best_cost, best_path = candidates[0]

            results.append(best_path)
            seen.add(tuple(best_path))

        return results

