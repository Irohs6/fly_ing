from __future__ import annotations
import re

class ParseError(Exception):
    """Erreur de parsing du fichier de carte Fly-in."""
    pass


class Parser:
    """Parser orienté objet pour les fichiers Fly-in."""

    def __init__(self, file_path: str):
        self.file_path = file_path
        self.lines: list[tuple[int, str]] = []

    # --- Lecture du fichier ---
    def read(self) -> None:
        """Lit le fichier Fly-in, supprime les commentaires et lignes vides."""
        try:
            with open(self.file_path, "r", encoding="utf-8") as f:
                for i, raw in enumerate(f, start=1):
                    line = raw.strip()
                    if not line or line.startswith("#"):
                        continue
                    self.lines.append((i, line))
        except FileNotFoundError:
            raise ParseError(f"Fichier introuvable : {self.file_path}")

    # --- Parsing des métadonnées ---
    def parse_metadata(self, raw: str) -> dict[str, str | int]:
        meta = {}
        if "[" not in raw:
            return meta
        raw = raw.strip("[]")
        for token in raw.split():
            if "=" not in token:
                continue
            key, value = token.split("=", 1)
            meta[key] = int(value) if value.isdigit() else value
        return meta

    # --- Parsing d'une zone ---
    def parse_zone(self, line: str, zone_type: str) -> dict:
        try:
            parts = re.split(r"\s+", line.split(":", 1)[1].strip())
            name, x, y = parts[:3]
            metadata = self.parse_metadata(" ".join(parts[3:]))

            # Capacité par défaut
            if "max_drones" not in metadata:
                if metadata.get("zone") == "restricted":
                    metadata["max_drones"] = 0
                else:
                    metadata["max_drones"] = 1

            # Start et End illimités
            if zone_type in ("start", "end"):
                metadata.pop("max_drones", None)

            return {
                "name": name,
                "x": int(x),
                "y": int(y),
                "zone_type": zone_type,
                "metadata": metadata,
            }
        except Exception:
            raise ParseError(f"Syntaxe invalide pour la zone : {line}")

    # --- Parsing d'une connexion ---
    def parse_connection(self, line: str) -> dict:
        try:
            body = line.split(":", 1)[1].strip()
            parts = body.split("[", 1)
            zones = parts[0].strip().split("-")
            if len(zones) != 2:
                raise ParseError(f"Connexion invalide : {line}")
            metadata = self.parse_metadata(parts[1]) if len(parts) > 1 else {}
            if "max_link_capacity" not in metadata:
                metadata["max_link_capacity"] = 1
            return {"source": zones[0], "target": zones[1], "metadata": metadata}
        except Exception:
            raise ParseError(f"Syntaxe invalide pour la connexion : {line}")

    # --- Parsing complet ---
    def parse(self):
        self.read()
        nb_drones = {}
        start_hub = {}
        end_hub = {}
        hubs = []
        connections = []

        for i, line in self.lines:
            if line.startswith("nb_drones:"):
                nb_drones = {"line": i, "value": int(line.split(":")[1].strip())}
            elif line.startswith("start_hub:"):
                start_hub = {"line": i, **self.parse_zone(line, "start")}
            elif line.startswith("end_hub:"):
                end_hub = {"line": i, **self.parse_zone(line, "end")}
            elif line.startswith("hub:"):
                hubs.append({"line": i, **self.parse_zone(line, "hub")})
            elif line.startswith("connection:"):
                connections.append({"line": i, **self.parse_connection(line)})
            else:
                raise ParseError(f"Ligne {i} : syntaxe inconnue -> {line}")

        if not start_hub or not end_hub:
            raise ParseError("start_hub ou end_hub manquant dans le fichier.")

        return nb_drones, start_hub, end_hub, {"hub": hubs}, {"connection": connections}


if __name__ == "__main__":
    parser = Parser("assets/maps/challenger/01_the_impossible_dream.txt")
    nb_drones, start, end, hubs, conns = parser.parse()
    
     # Validation
    from .validator import MapValidator
    validator = MapValidator(nb_drones, start, end, hubs, conns)
    validator.validate()

    print("\n=== 🛰️  Configuration de la carte Fly-in ===\n")
    print(f"Nombre de drones : {nb_drones['value']} (ligne {nb_drones['line']})\n")

    print("🚀 Zone de départ :")
    print(f"  Nom : {start['name']}  |  Coordonnées : ({start['x']}, {start['y']})")
    for k, v in start["metadata"].items():
        print(f"    {k}: {v}")
    print()

    print("🎯 Zone d'arrivée :")
    print(f"  Nom : {end['name']}  |  Coordonnées : ({end['x']}, {end['y']})")
    for k, v in end["metadata"].items():
        print(f"    {k}: {v}")
    print()

    print("🏗️  Zones intermédiaires (hubs) :")
    for hub in hubs["hub"]:
        print(f"  [{hub['line']}] {hub['name']}  ({hub['x']}, {hub['y']})  type={hub['zone_type']}")
        for k, v in hub["metadata"].items():
            print(f"    {k}: {v}")
        print()

    print("🔗 Connexions :")
    for conn in conns["connection"]:
        print(f"  [{conn['line']}] {conn['source']} -> {conn['target']}")
        for k, v in conn["metadata"].items():
            print(f"    {k}: {v}")
        print()

    print("✅ Fin du parsing — toutes les données ont été affichées.\n")
