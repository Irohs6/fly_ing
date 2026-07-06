# Différences entre subject_en v1.4 et subject_en_v2 v1.5

---

## 1. Version

| v1.4 | v1.5 |
|------|------|
| Version: 1.4 | Version: 1.5 |

---

## 2. AI Instructions — 2 nouveaux exemples

### Ajout dans v1.5

Deux nouveaux couples bon/mauvais exemple ont été ajoutés à la section "Comments and Examples" :

**Bon exemple (nouveau) :**
> I use AI to help design a parser. Then I walk through the logic with a peer. We catch two bugs and rewrite it together — better, cleaner, and fully understood.

**Mauvais exemple (nouveau) :**
> I let Copilot generate my code for a key part of my project. It compiles, but I can't explain how it handles pipes. During the evaluation, I fail to justify and I fail my project.

### Impact sur le projet
Aucun impact technique. C'est un renforcement du message pédagogique autour de l'utilisation responsable de l'IA.

---

## 3. Constraints — Démonstration en peer review

### Ajout dans v1.5

La phrase suivante a été ajoutée après la liste des contraintes :

> *"This will have to be demonstrated during the peer review."*

### Impact sur le projet
Pas d'impact sur le code, mais important pour l'évaluation : tu devras être capable de **montrer et expliquer** en live que ton projet est type-safe et orienté objet. Prépare-toi à justifier tes choix de types et d'architecture.

---

## 4. Let the Drone Fly — Support des commentaires `#`

### Ajout dans v1.5

Une nouvelle règle a été ajoutée dans la description du format de fichier :

> *"Comments start with `#` and are ignored."*

### Impact sur le projet
**Impact direct sur le parser.** Les fichiers map peuvent désormais contenir des lignes commençant par `#`. Le parser doit les ignorer sans erreur. Il faut vérifier que `src/parser/parser.py` gère bien ce cas.

---

## 5. Colors — Clarification de la valeur acceptée

### Avant (v1.4)
> *"Accepted values: any valid (e.g., `red`, `blue`, `gray`)."*
> *(phrase incomplète)*

### Après (v1.5)
> *"Accepted values: any valid single-word string (e.g., `red`, `blue`, `gray`). There is no fixed list of allowed colors."*

### Impact sur le projet
Clarification seulement. La couleur est une chaîne quelconque d'un mot. Le parser ne doit pas valider ou rejeter une couleur inconnue.

---

## 6. Parser Constraints — 2 nouvelles règles importantes

### 6a. Nombre de drones illimité

**Ajout dans v1.5 :**
> *"The program must be able to handle any number of drones."*

**Impact :** Pas de limite hardcodée sur le nombre de drones. Le code ne doit pas supposer un maximum (pas de `if nb_drones > 100` par exemple).

---

### 6b. `max_drones` ignoré sur `start_hub` et `end_hub`

**Ajout dans v1.5 :**
> *"The `max_drones` capacity is ignored on `start_hub` and `end_hub` zones — these have no capacity limit. If such metadata is present on those zones, it is ignored and is not a validation error."*

**Impact direct sur le code :**

- La zone de départ peut contenir **tous les drones** au début sans limite de capacité.
- La zone d'arrivée peut recevoir **tous les drones** sans limite.
- Si un fichier map contient `start_hub: hub 0 0 [max_drones=1]`, ce n'est **pas** une erreur de parsing — la valeur est simplement ignorée.
- À vérifier dans `src/model/simulation.py` : la logique de `resolve_conflicts` ne doit pas bloquer les drones sur la zone de départ, et ne doit pas comptabiliser les arrivées à la zone finale.

---

## 7. Scoring — Nouvelle métrique secondaire

### Ajout dans v1.5

Dans la section "Secondary metrics" :

> *"Quality and usefulness of visual representation"*

### Impact sur le projet
La représentation visuelle est maintenant **évaluée** comme critère secondaire en cas d'égalité de tours. Investir dans un affichage clair (couleurs terminal, interface graphique) peut faire la différence.

---

## 8. Performance Benchmarks — Catégories globales ajoutées

### Ajout dans v1.5

Des seuils globaux par niveau ont été introduits avant les cibles spécifiques :

| Niveau | Seuil global (v1.5) |
|--------|---------------------|
| Easy | < 10 turns |
| Medium | 10–30 turns |
| Hard | < 60 turns |
| Challenger | Beat 45 turns (optionnel) |

Les cibles spécifiques par map restent identiques à v1.4.

### Impact sur le projet
Utile pour évaluer rapidement si une solution est dans la bonne plage, même sur des maps custom. Lors de la peer review, si tu es dans les seuils globaux tu es "acceptable", si tu atteins les cibles spécifiques tu es "bien optimisé".

---

## 9. Submission — Détails sur la "brief modification"

### Avant (v1.4)
Vague mention qu'une modification peut être demandée pendant l'évaluation.

### Après (v1.5)
Précisions complètes :
- Faisable en **quelques minutes** dans l'environnement de ton choix.
- Peut varier entre évaluateurs (scope et cible définis dans les guidelines d'évaluation).
- Exemples : *"update a function, modify a display, adjust a data structure."*
- But : vérifier la **compréhension réelle** d'une partie spécifique du projet.

### Impact sur le projet
Prépare-toi à pouvoir modifier rapidement une portion de code en live. Assure-toi de comprendre chaque partie du projet, pas seulement de l'avoir écrite.

---

## Résumé des impacts sur le code

| Changement | Fichier(s) concerné(s) | Priorité |
|---|---|---|
| Support commentaires `#` | `src/parser/parser.py` | **Obligatoire** |
| `max_drones` ignoré sur start/end | `src/model/simulation.py`, `src/model/graph.py` | **Obligatoire** |
| Nombre de drones illimité | Vérification globale (pas de limite hardcodée) | **Obligatoire** |
| Métrique visuelle évaluée | `src/view/` | Recommandé |
