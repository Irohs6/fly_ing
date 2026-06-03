Je travaille sur un projet Python appelé "Fly-in" (42 project).
Je ne veux PAS que tu écrives du code.

Je veux uniquement :

1. Une architecture de fichiers claire pour le module de pathfinding.
2. Une explication détaillée du rôle de chaque fichier.
3. Une explication de comment implémenter chaque fichier (logique, algorithmes, structures de données, flux).
4. Aucun code source, uniquement des explications et pseudo-logique.

---

### Contexte du projet

Je développe un simulateur de drones sur un graphe.

Le système doit :

* Trouver des chemins entre un start_hub et un end_hub
* Gérer plusieurs drones simultanément
* Gérer des coûts de déplacement différents (normal, priority, restricted)
* Gérer des capacités de zones et de connexions (Reservation System déjà géré ailleurs)
* Utiliser A* comme algorithme principal
* Générer plusieurs chemins possibles pour la répartition des drones

---

### Architecture attendue

Je veux que tu proposes une architecture de module de pathfinding uniquement, par exemple :

* astar_solver.py
* path_generator.py
* heuristic.py
* graph_adapter.py
* cost_model.py
* route_manager.py

---

### Pour chaque fichier, tu dois expliquer :

* Son rôle précis dans le système
* Les données qu’il reçoit en entrée
* Les données qu’il produit en sortie
* Comment il interagit avec les autres modules
* La logique interne à implémenter (sans code)
* Les structures de données nécessaires
* Les edge cases importants

---

### Contraintes importantes

* Ne jamais écrire de code Python
* Ne jamais donner d’implémentation complète
* Se limiter à une explication technique claire et structurée
* Rester dans une logique de conception logicielle (niveau architecture)
* Adapter la solution à un A* avec gestion de coûts et multi-path generation

---

### Objectif final

Le but est que je puisse implémenter moi-même le module après ta réponse en ayant une compréhension complète de :

* comment A* est utilisé dans ce projet
* comment générer plusieurs chemins alternatifs
* comment connecter ça à une gestion de flotte de drones

Merci de structurer la réponse comme une mini documentation technique de module.
