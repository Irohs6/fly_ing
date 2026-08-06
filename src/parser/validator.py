from __future__ import annotations
from src.parser.parser import ParseError

class MapValidator:
    """Valide la configuration issue du parser selon les règles Fly-in."""

    VALID_ZONE_TYPES = {"normal", "blocked", "restricted", "priority"}
    VALID_HUB_KEYS = {"zone", "color", "max_drones"}
    VALID_CONN_KEYS = {"max_link_capacity"}

    def __init__(self, nb_drones, start_hub, end_hub, hubs, connections):
        self.nb_drones = nb_drones
        self.start_hub = start_hub
        self.end_hub = end_hub
        self.hubs = hubs["hub"]
        self.connections = connections["connection"]

    def validate(self):
        """Valide toutes les sections du fichier."""
        self._validate_nb_drones()
        self._validate_zones()
        self._validate_connections()
        self._check_duplicates()
        print("✅ Validation terminée — configuration conforme au sujet Fly-in.\n")

    def _validate_nb_drones(self):
        if self.nb_drones["value"] <= 0:
            raise ParseError("Le nombre de drones doit être positif.")

    def _validate_zones(self):
        for hub in self.hubs + [self.start_hub, self.end_hub]:
            meta = hub["metadata"]
            zone_type = meta.get("zone", "normal")
            if zone_type not in self.VALID_ZONE_TYPES:
                raise ParseError(f"Zone invalide '{zone_type}' à la ligne {hub['line']}")
            for key in meta:
                if key not in self.VALID_HUB_KEYS:
                    raise ParseError(f"Clé de métadonnée inconnue '{key}' à la ligne {hub['line']}")
            if "max_drones" in meta and meta["max_drones"] < 0:
                raise ParseError(f"Capacité négative à la ligne {hub['line']}")

    def _validate_connections(self):
        for conn in self.connections:
            meta = conn["metadata"]
            for key in meta:
                if key not in self.VALID_CONN_KEYS:
                    raise ParseError(f"Clé de métadonnée inconnue '{key}' à la ligne {conn['line']}")
            if "max_link_capacity" in meta and meta["max_link_capacity"] <= 0:
                raise ParseError(f"Capacité de lien invalide à la ligne {conn['line']}")

    def _check_duplicates(self):
        seen = set()
        for conn in self.connections:
            pair = tuple(sorted([conn["source"], conn["target"]]))
            if pair in seen:
                raise ParseError(f"Connexion dupliquée entre {pair[0]} et {pair[1]} (ligne {conn['line']})")
            seen.add(pair)
