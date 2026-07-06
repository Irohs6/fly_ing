# Easy Level 3: Basic capacity management
# nb_drones: 4

# start_hub: start 0 0 [color=green max_drones=4]
# hub: bottleneck 1 0 [color=orange max_drones=2]
# hub: wide_area 2 0 [color=blue max_drones=3]
# end_hub: goal 3 0 [color=red max_drones=4]

# connection: start-bottleneck [max_link_capacity=4]
# connection: bottleneck-wide_area [max_link_capacity=4]
# connection: wide_area-goal [max_link_capacity=4]


# --- Parseur de fichiers de carte pour le routage de drones ---
# Structure attendue du fichier :
#   nb_drones: <entier positif>
#   start_hub: <nom> <x> <y> [métadonnées optionnelles]
#   hub: <nom> <x> <y> [métadonnées optionnelles]
#   end_hub: <nom> <x> <y> [métadonnées optionnelles]
#   connection: <hub1>-<hub2> [métadonnées optionnelles]
class Parser:
    """Parses drone routing map files into a structured config dict."""

    # Clés autorisées dans les métadonnées d'un hub
    VALID_HUB_METADATA_KEYS = {"zone", "color", "max_drones"}
    # Clés autorisées dans les métadonnées d'une connexion
    VALID_CONNECTION_METADATA_KEYS = {"max_link_capacity"}
    # Types de zones valides
    VALID_ZONE_TYPES = {"normal", "blocked", "restricted", "priority"}

    def __init__(self, file_path: str) -> None:
        """Initialize the parser with the path to the map file.

        Args:
            file_path: Path to the map file to parse.
        """
        # Chemin vers le fichier de carte à analyser
        self.file_path = file_path
        # Dictionnaire de configuration résultant du parsing
        # start_hub  : hub de départ (unique)
        # end_hub    : hub d'arrivée (unique)
        # hub        : liste des hubs intermédiaires
        # connection : liste des connexions entre hubs
        # nb_drones  : nombre de drones à simuler
        self.config = {
            "start_hub": None,
            "end_hub": None,
            "hub": [],
            "connection": [],
            "nb_drones": None,
        }

    def parse(self) -> dict:
        """Parse the map file and return the structured config dict.

        Returns:
            A dict with keys: nb_drones, start_hub, end_hub, hub, connection.

        Raises:
            FileNotFoundError: If the file does not exist.
            ValueError: If the file format is invalid.
            IOError: If the file cannot be read.
        """

        try:
            # Étape 1 : lecture du fichier (suppression des commentaires/lignes vides)
            lines = self._read_file()
            # Étape 2 : analyse ligne par ligne et remplissage de self.config
            self._parse_lines(lines)
            # Étape 3 : validation globale de la cohérence du graphe
            self._validate()
        except FileNotFoundError:
            raise FileNotFoundError(f"File not found: {self.file_path}")
        except ValueError as e:
            raise ValueError(f"Parse error: {e}") from e
        except IOError as e:
            raise IOError(f"Error reading file {self.file_path}: {e}") from e
        return self.config

    def _read_file(self) -> list[tuple[int, str]]:
        """Read the file and return meaningful (line_number, content) pairs.

        Skips comment lines (starting with #) and empty lines.

        Returns:
            List of (line_number, line_content)
            for non-comment, non-empty lines.

        Raises:
            FileNotFoundError: If the file does not exist.
            IOError: If the file cannot be read.
        """
        result: list[tuple[int, str]] = []
        with open(self.file_path, "r") as file:
            for number_ligne, line in enumerate(file, start=1):
                # Ignorer les lignes de commentaires (commençant par #)
                if line.startswith("#"):
                    continue
                line = line.strip()
                # Ignorer les lignes vides après nettoyage
                if not line:
                    continue
                # Conserver le numéro de ligne pour les messages d'erreur
                result.append((number_ligne, line))
        return result

    def _parse_lines(self, lines: list[tuple[int, str]]) -> None:
        """Iterate meaningful lines and dispatch to hub/connection parsers.

        Args:
            lines: List of (line_number, line_content) pairs.

        Returns:
            None

        Raises:
            ValueError: If a line has invalid format or content.
        """
        nb_drones: int | None = None
        for number_ligne, line in lines:
            # La première ligne utile doit obligatoirement déclarer nb_drones
            if nb_drones is None and not line.startswith("nb_drones:"):
                raise ValueError(
                    f"Line {number_ligne}: expected 'nb_drones:'"
                    f", got: {line!r}"
                )
            if line.startswith(
                "nb_drones:"
            ):  # Déclaration du nombre de drones
                raw = line.split(":")[1].strip()
                if not raw.isdigit() or int(raw) < 1:
                    raise ValueError(
                        f"Line {number_ligne}: "
                        f"nb_drones must be a positive integer, "
                        f"got: {raw!r}"
                    )
                nb_drones = int(raw)
                self.config["nb_drones"] = nb_drones
            elif (
                line.startswith("start_hub:")  # Hub de départ
                or line.startswith("hub:")  # Hub intermédiaire
                or line.startswith("end_hub:")  # Hub d'arrivée
            ):
                self._parse_hub_line(line, number_ligne)
            elif line.startswith("connection:"):  # Connexion entre deux hubs
                self._parse_connection_line(line, number_ligne)
            else:
                # Type de ligne inconnu → erreur de format
                raise ValueError(
                    f"Line {number_ligne}: "
                    f"unrecognized line format: {line!r}"
                )
        if nb_drones is None:
            raise ValueError("Missing nb_drones definition")
        self.config["nb_drones"] = nb_drones

    def _validate(self) -> None:
        """Run all post-parse validation checks on self.config.

        Raises:
            ValueError: If any validation fails.
        """
        # Vérification de la présence obligatoire du hub de départ et d'arrivée
        if self.config["start_hub"] is None or self.config["end_hub"] is None:
            raise ValueError("Missing start_hub or end_hub definition")
        # Vérification de l'unicité des noms de hubs
        self._check_duplicate_hub_names()
        # Vérification de l'absence de connexions dupliquées
        self._check_duplicate_connections()
        # Vérification que chaque connexion pointe vers des hubs existants
        self._check_name_connections()
        # Vérification qu'un chemin existe entre départ et arrivée
        if not self._valid_path():
            raise ValueError(
                "No valid path exists between start_hub and end_hub"
                " considering blocked zones"
            )

    def _parse_hub_line(self, line: str, number_ligne: int) -> None:
        """Parse a hub line and add the zone to self.config.

        Args:
            line: The raw line from the file.
            number_ligne: Physical line number used for error messages.

        Raises:
            ValueError: If the line format or metadata is invalid.
        """
        # Exemple de ligne attendue : start_hub: depart 0 0 [color=green max_drones=4]
        # Décomposition : <type>: <nom> <x> <y> [clé=valeur ...]
        parts = line.split()
        if len(parts) < 4:
            raise ValueError(
                f"Line {number_ligne}: hub line must have format "
                f"'<type>: <name> <x> <y> [metadata]'"
            )
        # Récupération du type de hub (start_hub / hub / end_hub)
        hub_type = parts[0].rstrip(":")  # start_hub, hub, or end_hub
        name = parts[1]  # Nom unique du hub
        if "-" in name:
            raise ValueError(
                f"Line {number_ligne}: "
                f"zone name {name!r} cannot contain dashes"
            )
        try:
            # Coordonnées (x, y) en entiers
            x, y = int(parts[2]), int(parts[3])
        except ValueError:
            raise ValueError(
                f"Line {number_ligne}: invalid coordinates: {parts[2]!r}, "
                f"{parts[3]!r}"
            )
        metadata: dict[str, str | int] = {}
        if len(parts) > 4:
            # Reconstruction de la partie métadonnées (ex: [color=blue max_drones=3])
            metadata_part = " ".join(parts[4:])
            if metadata_part.startswith("[") and metadata_part.endswith("]"):
                metadata_part = metadata_part[1:-1]  # Suppression des crochets
                for option in metadata_part.split():
                    key, value = option.split("=", 1)
                    if key not in self.VALID_HUB_METADATA_KEYS:
                        raise ValueError(
                            f"Line {number_ligne}: unknown hub metadata key "
                            f"{key!r}, allowed: "
                            f"{sorted(self.VALID_HUB_METADATA_KEYS)}"
                        )
                    if key == "zone" and value not in self.VALID_ZONE_TYPES:
                        raise ValueError(
                            f"Line {number_ligne}: invalid zone type {value!r}"
                        )
                    if key == "max_drones":
                        if not value.isdigit() or int(value) < 1:
                            raise ValueError(
                                f"Line {number_ligne}: "
                                f"{key} must be a positive integer"
                            )
                        metadata[key] = int(value)
                    else:
                        metadata[key] = value
            else:
                raise ValueError(
                    f"Line {number_ligne}: "
                    f"metadata must be enclosed in [...], got: "
                    f"{metadata_part!r}"
                )
        if hub_type in ("start_hub", "end_hub"):
            if self.config[hub_type] is not None:
                raise ValueError(
                    f"Line {number_ligne}: duplicate {hub_type} definition"
                )
            self.config[hub_type] = {
                "name": name,
                "coordinate": (x, y),
                "metadata": metadata,
            }
        else:
            self.config["hub"].append(
                {"name": name, "coordinate": (x, y), "metadata": metadata}
            )

    def _parse_connection_line(self, line: str, number_ligne: int) -> None:
        """Parse a connection line and add it to self.config.

        Args:
            line: The raw line from the file.
            number_ligne: Physical line number used for error messages.

        Raises:
            ValueError: If the line format or metadata is invalid.
        """
        # Exemple de ligne attendue : connection: depart-arrivee [max_link_capacity=4]
        # Décomposition : connection: <hub1>-<hub2> [clé=valeur ...]
        parts = line.split()
        if len(parts) < 2:
            raise ValueError(
                f"Line {number_ligne}: invalid connection format: {line!r}"
            )
        # La partie connexion est au format "hub1-hub2"
        connection_part = parts[1]
        if "-" not in connection_part:
            raise ValueError(
                f"Line {number_ligne}: "
                f"connection must be in format 'hub1-hub2'"
            )
        hub1, hub2 = connection_part.split("-", 1)  # Séparation des deux hubs
        metadata: dict[str, str | int] = {}
        if len(parts) > 2:
            # Reconstruction de la partie métadonnées (ex: [max_link_capacity=4])
            metadata_part = " ".join(parts[2:])
            if metadata_part.startswith("[") and metadata_part.endswith("]"):
                metadata_part = metadata_part[1:-1]  # Suppression des crochets
                for option in metadata_part.split():
                    key, value = option.split("=", 1)
                    if key not in self.VALID_CONNECTION_METADATA_KEYS:
                        raise ValueError(
                            f"Line {number_ligne}: unknown connection "
                            f"metadata key {key!r}, allowed: "
                            f"{sorted(self.VALID_CONNECTION_METADATA_KEYS)}"
                        )
                    if key == "max_link_capacity":
                        if not value.isdigit() or int(value) < 1:
                            raise ValueError(
                                f"Line {number_ligne}: "
                                f"{key} must be a positive integer"
                            )
                        metadata[key] = int(value)
                    else:
                        metadata[key] = value
            else:
                raise ValueError(
                    f"Line {number_ligne}: "
                    f"metadata must be enclosed in [...], got: "
                    f"{metadata_part!r}"
                )
        self.config["connection"].append((hub1, hub2, metadata))

    def _check_duplicate_hub_names(self) -> None:
        """Check that all zone names are unique across hubs.

        Raises:
            ValueError: If two zones share the same name.
        """
        names: set[str] = set()
        for hub in self.config["hub"]:
            if hub["name"] in names:
                raise ValueError(f"Duplicate hub name: {hub['name']!r}")
            names.add(hub["name"])
        if self.config["start_hub"]["name"] in names:
            raise ValueError(
                f"Duplicate hub name: {self.config['start_hub']['name']!r}"
            )
        names.add(self.config["start_hub"]["name"])
        if self.config["end_hub"]["name"] in names:
            raise ValueError(
                f"Duplicate hub name: {self.config['end_hub']['name']!r}"
            )

    def _check_duplicate_connections(self) -> None:
        """Check that no connection is defined twice
        (a-b and b-a are duplicates).

        Raises:
            ValueError: If a duplicate connection is found.
        """
        connections: set[tuple[str, str]] = set()
        for c in self.config["connection"]:
            hub1, hub2 = c[0], c[1]
            if (hub1, hub2) in connections or (hub2, hub1) in connections:
                raise ValueError(f"Duplicate connection: {hub1!r} - {hub2!r}")
            connections.add((hub1, hub2))

    def _check_name_connections(self) -> None:
        """Check that all connection endpoints reference defined zones.

        Raises:
            ValueError: If a connection references an undefined zone.
        """
        known_names: set[str] = set()
        known_names.add(self.config["start_hub"]["name"])
        known_names.add(self.config["end_hub"]["name"])
        for hub in self.config["hub"]:
            known_names.add(hub["name"])
        for hub1, hub2, _ in self.config["connection"]:
            if hub1 not in known_names:
                raise ValueError(
                    f"Connection references undefined zone: {hub1!r}"
                )
            if hub2 not in known_names:
                raise ValueError(
                    f"Connection references undefined zone: {hub2!r}"
                )

    def _valid_path(self) -> bool:
        # Collecte des zones bloquées (inaccessibles aux drones)
        blocked_zones = {
            hub["name"]
            for hub in self.config["hub"]
            if hub["metadata"].get("zone") == "blocked"
        }
        start = self.config["start_hub"]["name"]
        end = self.config["end_hub"]["name"]

        # Parcours en profondeur (DFS) pour vérifier l'existence d'un chemin
        stack: list[str] = [start]
        visited: set[str] = set()

        # Construction de la liste d'adjacence (hors zones bloquées)
        adjacency = {
            hub["name"]: []
            for hub in self.config["hub"]
            if hub["name"] not in blocked_zones
        }
        adjacency[start] = []
        adjacency[end] = []

        for hub1, hub2, _ in self.config["connection"]:
            # N'ajouter que les connexions entre hubs non bloqués
            if hub1 not in blocked_zones and hub2 not in blocked_zones:
                adjacency[hub1].append(hub2)
                adjacency[hub2].append(hub1)

        while stack:
            current = stack.pop()
            if current == end:
                return True  # Chemin trouvé
            if current not in visited:
                visited.add(current)
                for neighbor in adjacency[current]:
                    if neighbor not in visited:
                        stack.append(neighbor)
        return False  # Aucun chemin possible


if __name__ == "__main__":
    import sys
    import os

    # Fichier de carte par défaut (utilisé si aucun argument n'est fourni)
    _default = os.path.join(
        os.path.dirname(__file__),
        "../../assets/maps/challenger/01_the_impossible_dream.txt",
    )
    # Utilisation : python parser.py [chemin_du_fichier]
    path = sys.argv[1] if len(sys.argv) > 1 else _default
    try:
        p = Parser(path)
        config = p.parse()  # Lancement du parsing complet

        if config:
            # -------------------------------------------------------
            # Affichage du résultat du parsing
            # -------------------------------------------------------
            SEP = "=" * 55

            print(SEP)
            print(f"  RÉSULTAT DU PARSING : {os.path.basename(path)}")
            print(SEP)

            # Nombre de drones
            # Exemple de valeur : 4
            print(f"\n  Nombre de drones    : {config['nb_drones']}")

            # --- Hub de départ ---
            # Exemple : {'name': 'depart', 'coordinate': (0, 0), 'metadata': {'color': 'green', 'max_drones': 4}}
            print(f"\n{SEP}")
            print("  HUB DE DÉPART (start_hub)")
            print(SEP)
            start_hub = config["start_hub"]
            print(f"  Nom         : {start_hub['name']}")
            print(
                f"  Coordonnées : x={start_hub['coordinate'][0]}, y={start_hub['coordinate'][1]}"
            )
            if start_hub["metadata"]:
                print(f"  Métadonnées :")
                for k, v in start_hub["metadata"].items():
                    print(f"    - {k} = {v}")
            else:
                print("  Métadonnées : aucune")

            # --- Hubs intermédiaires ---
            # Exemple : [{'name': 'carrefour', 'coordinate': (1, 0), 'metadata': {'max_drones': 2}}]
            print(f"\n{SEP}")
            print(f"  HUBS INTERMÉDIAIRES ({len(config['hub'])} hub(s))")
            print(SEP)
            if config["hub"]:
                for i, hub in enumerate(config["hub"], start=1):
                    print(f"  Hub #{i}")
                    print(f"    Nom         : {hub['name']}")
                    print(
                        f"    Coordonnées : x={hub['coordinate'][0]}, y={hub['coordinate'][1]}"
                    )
                    if hub["metadata"]:
                        print(f"    Métadonnées :")
                        for k, v in hub["metadata"].items():
                            print(f"      - {k} = {v}")
                    else:
                        print("    Métadonnées : aucune")
            else:
                print("  (aucun hub intermédiaire)")

            # --- Hub d'arrivée ---
            # Exemple : {'name': 'arrivee', 'coordinate': (3, 0), 'metadata': {'color': 'red', 'max_drones': 4}}
            print(f"\n{SEP}")
            print("  HUB D'ARRIVÉE (end_hub)")
            print(SEP)
            eh = config["end_hub"]
            print(f"  Nom         : {eh['name']}")
            print(
                f"  Coordonnées : x={eh['coordinate'][0]}, y={eh['coordinate'][1]}"
            )
            if eh["metadata"]:
                print(f"  Métadonnées :")
                for k, v in eh["metadata"].items():
                    print(f"    - {k} = {v}")
            else:
                print("  Métadonnées : aucune")

            # --- Connexions ---
            # Exemple : [('depart', 'carrefour', {'max_link_capacity': 4}), ('carrefour', 'arrivee', {})]
            print(f"\n{SEP}")
            print(f"  CONNEXIONS ({len(config['connection'])} connexion(s))")
            print(SEP)
            for i, c in enumerate(config["connection"], start=1):
                hub1, hub2, meta = c
                opts = (
                    ", ".join(f"{k}={v}" for k, v in meta.items())
                    if meta
                    else "aucune"
                )
                print(f"  #{i:>2}  {hub1} ──► {hub2}  [options: {opts}]")

            print(f"\n{SEP}")
            print("  Parsing terminé avec succès.")
            print(SEP)

    except Exception as e:
        print(f"Erreur lors du parsing : {e}")
