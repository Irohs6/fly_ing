# Parser - Points à améliorer

## Problèmes actuels

### 1. Trop de responsabilités
Le `Parser` s'occupe actuellement de :
- lire le fichier ;
- parser les données ;
- valider le contenu ;
- construire la structure de données.

Il ne respecte donc pas le principe de responsabilité unique (SRP).

---

### 2. Utilisation de dictionnaires à la place d'objets
Le parser retourne un gros dictionnaire de configuration.

Actuellement :

```python
config["hub"]
config["connection"]
config["start_hub"]
```

Il serait préférable de manipuler directement des objets :

```python
graph.hubs
graph.connections
graph.start
graph.end
```

---

### 3. Les hubs sont représentés par des dictionnaires
Chaque hub est stocké sous la forme :

```python
{
    "name": "...",
    "coordinate": (...),
    "metadata": {...}
}
```

Il serait plus propre d'avoir une classe `Hub` contenant directement ces informations.

---

### 4. Les connexions sont représentées par des tuples
Une connexion est actuellement stockée sous la forme :

```python
(hub1, hub2, metadata)
```

Une classe `Connection` permettrait un code plus lisible et plus orienté objet.

---

### 5. Les métadonnées ne sont pas structurées
Les informations d'un hub sont regroupées dans un dictionnaire `metadata`.

Exemple :

```python
hub["metadata"]["zone"]
```

Il serait préférable d'avoir des attributs explicites :

```python
hub.zone
hub.color
hub.max_drones
```

---

### 6. Absence d'un objet représentant la carte
Le parser devrait retourner un objet `Map` (ou `Graph`) plutôt qu'un dictionnaire.

Exemple :

```python
graph = Parser(path).parse()
```

---

### 7. Validation trop liée au parser
Les méthodes de validation sont directement intégrées au parser.

Créer une classe dédiée (`MapValidator` par exemple) permettrait une meilleure séparation des responsabilités.

---

## Objectif

Faire évoluer le parser pour qu'il construise directement les objets métier du projet :

```
Parser
    ↓
Hub
Connection
Map
    ↓
Simulation
```

Cette architecture est plus conforme à la programmation orientée objet, facilite la maintenance du projet et sera plus simple à faire évoluer pour le moteur de simulation.
