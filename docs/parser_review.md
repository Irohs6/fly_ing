# Code Review — `src/controller/parser.py`

## Notation globale : 8.5 / 10

---

## SOLID

### S — Single Responsibility ✅ 8/10

Bien appliqué après refactoring :

| Méthode | Responsabilité |
|---|---|
| `parse()` | orchestration uniquement |
| `_read_file()` | lecture fichier uniquement |
| `_parse_lines()` | dispatch ligne par ligne |
| `_validate()` | appel des 3 checks |
| `_parse_hub_line()` | parsing + écriture dans `self.config` |
| `_check_duplicate_*()` | validation ciblée |

**Point faible :** `_parse_hub_line` et `_parse_connection_line` font deux choses : elles parsent *et* mutent `self.config`. Idéalement elles retourneraient un dict/objet et c'est `_parse_lines` qui ferait le `append`.

---

### O — Open/Closed ⚠️ 5/10

Le parser n'est **pas extensible sans modification**. Ajouter un nouveau type de ligne (`waypoint:`, `checkpoint:`) oblige à toucher `_parse_lines`. Ajouter une clé de métadonnée oblige à modifier `VALID_HUB_METADATA_KEYS` et le bloc `if key == ...`.

**Piste d'amélioration :** une table de dispatch `{ "hub:": self._parse_hub_line, ... }` dans `_parse_lines` rendrait l'ajout de types sans toucher le code existant.

---

### L — Liskov Substitution ➖ N/A

Pas d'héritage dans le parser → non applicable.

---

### I — Interface Segregation ➖ N/A

Pas d'interface/protocole défini → non applicable à ce stade.

---

### D — Dependency Inversion ⚠️ 5/10

`Parser` est couplé directement à un fichier disque via `open(self.file_path)`. Il est impossible de lui passer du contenu en mémoire (pour les tests, par exemple) sans passer par un fichier temporaire.

**Piste d'amélioration :** accepter aussi une `list[str]` ou un `IO` en alternative au chemin :
```python
def __init__(self, file_path: str | None = None, lines: list[str] | None = None)
```
Ou mieux, `_read_file` pourrait être remplacée par injection d'une liste de lignes.

---

## OOP

### Encapsulation ✅ 9/10
- API publique réduite à `parse()` — parfait.
- Toutes les méthodes internes sont préfixées `_`.
- Les constantes de validation sont des attributs de classe (`VALID_HUB_METADATA_KEYS`, `VALID_CONNECTION_METADATA_KEYS`).

### Cohérence des constantes ✅
Toutes les constantes de validation sont désormais des **attributs de classe** :
```python
VALID_HUB_METADATA_KEYS = {"zone", "color", "max_drones"}
VALID_CONNECTION_METADATA_KEYS = {"max_link_capacity"}
VALID_ZONE_TYPES = {"normal", "blocked", "restricted", "priority"}
```
`valid_zone_types` a été retiré de `__init__` et promu en `VALID_ZONE_TYPES` au niveau classe.

### Réutilisabilité ✅
`self.config` est maintenant **réinitialisé au début de `parse()`**. Appeler `parse()` deux fois sur la même instance repart d'un état propre — aucun doublon possible. `__init__` ne stocke plus que `self.file_path`.

### Type hints ✅ 9/10
Bien présents partout. `dict` non typé pour `self.config` est le seul point faible — un `TypedDict` serait plus robuste mais non obligatoire à ce stade.

### Docstrings ✅ 10/10
Format Google respecté sur toutes les méthodes publiques et privées.

---

## Efficacité

| Point | Évaluation |
|---|---|
| Lecture fichier en un seul passage | ✅ |
| Sets pour les checks de doublons (O(1)) | ✅ |
| `_check_name_connections` : set construit avant la boucle | ✅ |
| `sorted()` dans les messages d'erreur | ✅ (chemin d'erreur seulement) |
| Lignes chargées en mémoire avant parsing | ✅ (taille fichiers négligeable) |
| `line.split()` sans cache dans `_parse_hub_line` | ➖ mineur |

**Score efficacité : 9/10** — aucun problème réel pour la taille de fichiers attendue.

---

## Résumé des points à corriger

| Priorité | Action | État |
|---|---|---|
| ✅ Fait | `VALID_ZONE_TYPES` en constante de classe | Corrigé |
| ✅ Fait | `self.config` réinitialisé dans `parse()` | Corrigé |
| 🟡 Moyenne | `_parse_hub_line` retourner un dict plutôt que muter `self.config` directement | Ouvert |
| 🟡 Moyenne | Table de dispatch dans `_parse_lines` pour respecter OCP | Ouvert |
| 🟢 Faible | Supprimer les commentaires en tête de fichier (lignes 1-11, reste d'un ancien test) | Ouvert |
| 🟢 Faible | Envisager injection de données pour découpler du fichier disque (DIP) | Ouvert |
