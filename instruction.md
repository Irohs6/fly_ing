Je développe un projet Python/Pygame appelé "Fly-in" qui simule le déplacement de plusieurs drones dans un graphe de hubs connectés.

IMPORTANT :
Ce n'est PAS un jeu RTS, ce n'est PAS une simulation militaire, ce n'est PAS une carte géographique réaliste.

L'objectif est de visualiser un réseau de hubs et de connexions tout en montrant l'état de la simulation en temps réel.

Le sujet impose :

* Un graphe composé de hubs (nodes).
* Des connexions bidirectionnelles (edges).
* Plusieurs drones se déplaçant simultanément.
* Des capacités sur les hubs (max_drones).
* Des capacités sur les connexions (max_link_capacity).
* Des zones de type normal, restricted, priority et blocked.
* Les hubs possèdent une couleur définie dans le fichier de configuration.
* Les drones doivent être routés du start_hub vers le end_hub en minimisant le nombre total de tours.

Je veux une interface Pygame moderne inspirée d'un logiciel de supervision réseau ou de simulation logistique.

CONTRAINTES VISUELLES :

1. HUBS

* Représenter les hubs par des cercles.
* Utiliser la couleur définie dans le fichier.
* Afficher le nom du hub.
* Afficher l'occupation actuelle sous la forme :
  current_drones/max_drones
* La taille du cercle peut être proportionnelle à max_drones.

Exemple :

```
  🔵
[2/5]
```

2. CONNEXIONS

Les connexions ne doivent pas être de simples lignes.

Comme chaque connexion possède une capacité :

max_link_capacity = 1
=> ligne simple

max_link_capacity = 2
=> double bande parallèle

max_link_capacity = 3
=> triple bande parallèle

L'épaisseur ou le nombre de bandes doit permettre de comprendre immédiatement la capacité de la connexion.

Afficher également :

current_usage/max_capacity

au milieu de la connexion.

3. DRONES

Les drones doivent être représentés par de petits points animés.

Ne pas afficher les identifiants en permanence.

Les identifiants D1, D2, etc. doivent apparaître uniquement au survol ou lorsqu'un drone est sélectionné.

Les drones doivent se déplacer visuellement le long des connexions.

4. ZONES RESTRICTED

Les déplacements vers une zone restricted prennent 2 tours.

Je veux une représentation visuelle montrant :

* le drone en transit
* la connexion occupée pendant les 2 tours

Le drone doit apparaître entre les hubs pendant son déplacement.

5. PANNEAU DE STATISTIQUES

Ajouter un panneau latéral affichant :

* Tour actuel
* Nombre de drones livrés
* Nombre de drones restants
* Drones en attente
* Connexions saturées
* Temps moyen de trajet
* Nombre total de mouvements

6. MODE DEBUG

Prévoir un mode debug permettant :

* de sélectionner un drone
* d'afficher son chemin complet
* de mettre en surbrillance toutes les connexions de sa route

Exemple :

Start -> A -> C -> F -> Goal

7. STYLE

Je veux un style :

* sombre
* professionnel
* proche d'un visualiseur réseau
* proche de Gephi, Grafana ou d'un logiciel de supervision

Palette recommandée :

Fond :
(20, 20, 25)

Connexions :
gris foncé

Texte :
gris clair

Drones :
blanc ou cyan

Éviter toute esthétique militaire ou RTS.

OBJECTIF :

Propose une architecture Pygame propre orientée objet avec :

* GraphRenderer
* HubRenderer
* ConnectionRenderer
* DroneRenderer
* StatsPanel
* SimulationView

Explique les responsabilités de chaque classe et propose une maquette visuelle ASCII de l'interface finale.
