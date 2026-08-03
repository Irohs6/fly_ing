
from __future__ import annotations
from typing import TypedDict, cast


class ZoneConfig(TypedDict):
    """Typed configuration for a zone/hub."""

    name: str
    coordinate: tuple[int, int]
    metadata: dict[str, str | int]


class MapConfig(TypedDict):
    """Fully-parsed and validated map configuration."""

    nb_drones: int
    start_hub: ZoneConfig
    end_hub: ZoneConfig
    hub: list[ZoneConfig]
    connection: list[tuple[str, str, dict[str, str | int]]]


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
        self._nb_drones: int | None = None
        self._start_hub: ZoneConfig | None = None
        self._end_hub: ZoneConfig | None = None
        self._hub: list[ZoneConfig] = []
        self._connection: list[tuple[str, str, dict[str, str | int]]] = []
        self._connection_line_numbers: list[int] = []

    def parse(self) -> MapConfig:
        """Parse the map file and return the structured config dict.

        Returns:
            A MapConfig with keys: nb_drones,
            start_hub, end_hub, hub, connection.

        Raises:
            FileNotFoundError: If the file does not exist.
            ValueError: If the file format is invalid.
            IOError: If the file cannot be read.
        """

        try:
            # Étape 1 : lecture du fichier
            # (suppression des commentaires/lignes vides)
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
        return MapConfig(
            nb_drones=cast(int, self._nb_drones),
            start_hub=cast(ZoneConfig, self._start_hub),
            end_hub=cast(ZoneConfig, self._end_hub),
            hub=self._hub,
            connection=self._connection,
        )

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
                self._nb_drones = nb_drones
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
        self._nb_drones = nb_drones

    def _validate(self) -> None:
        """Run all post-parse validation checks on self.config.

        Raises:
            ValueError: If any validation fails.
        """
        # Vérification de la présence obligatoire du hub de départ et d'arrivée
        if self._start_hub is None or self._end_hub is None:
            raise ValueError("Missing start_hub or end_hub definition")
        # Vérification de l'unicité des noms de hubs
        self._check_duplicate_hub_names()
        # Vérification de l'absence de connexions dupliquées
        self._check_duplicate_connections()
        # Vérification que chaque connexion pointe vers des hubs existants
        self._check_name_connections()

    def _parse_hub_line(self, line: str, number_ligne: int) -> None:
        """Parse a hub line and add the zone to self.config.

        Args:
            line: The raw line from the file.
            number_ligne: Physical line number used for error messages.

        Raises:
            ValueError: If the line format or metadata is invalid.
        """
        # Exemple de ligne attendue : start_hub: depart 0 0
        # [color=green max_drones=4]
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
        if "-" in name or " " in name:
            raise ValueError(
                f"Line {number_ligne}: "
                f"zone name {name!r} cannot contain dashes or spaces"
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
            # Reconstruction de la partie métadonnées
            # (ex: [color=blue max_drones=3])
            metadata_part = " ".join(parts[4:])
            if metadata_part.startswith("[") and metadata_part.endswith("]"):
                metadata_part = metadata_part[1:-1]  # Suppression des crochets
                for option in metadata_part.split():
                    if "=" not in option:
                        raise ValueError(
                            f"Line {number_ligne}: malformed metadata option "
                            f"{option!r}, expected 'key=value'"
                        )
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
                        if hub_type in ("start_hub", "end_hub"):
                            # Ignore user value: start/end capacity = nb_drones
                            metadata["max_drones"] = cast(
                                int, self._nb_drones
                            )
                        elif not value.isdigit() or int(value) < 1:
                            raise ValueError(
                                f"Line {number_ligne}: "
                                f"{key} must be a positive integer"
                            )
                        else:
                            metadata[key] = int(value)
                    else:
                        metadata[key] = value
            else:
                raise ValueError(
                    f"Line {number_ligne}: "
                    f"metadata must be enclosed in [...], got: "
                    f"{metadata_part!r}"
                )
        zone_data: ZoneConfig = {
            "name": name,
            "coordinate": (x, y),
            "metadata": metadata,
        }
        if hub_type == "start_hub":
            if self._start_hub is not None:
                raise ValueError(
                    f"Line {number_ligne}: duplicate {hub_type} definition"
                )
            self._start_hub = zone_data
        elif hub_type == "end_hub":
            if self._end_hub is not None:
                raise ValueError(
                    f"Line {number_ligne}: duplicate {hub_type} definition"
                )
            self._end_hub = zone_data
        else:
            self._hub.append(zone_data)

    def _parse_connection_line(self, line: str, number_ligne: int) -> None:
        """Parse a connection line and add it to self.config.

        Args:
            line: The raw line from the file.
            number_ligne: Physical line number used for error messages.

        Raises:
            ValueError: If the line format or metadata is invalid.
        """
        # Exemple de ligne attendue : connection: depart-arrivee
        # [max_link_capacity=4]
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
            # Reconstruction de la partie métadonnées (ex: [max_link_capacity=
            # 4])
            metadata_part = " ".join(parts[2:])
            if metadata_part.startswith("[") and metadata_part.endswith("]"):
                metadata_part = metadata_part[1:-1]  # Suppression des crochets
                for option in metadata_part.split():
                    if "=" not in option:
                        raise ValueError(
                            f"Line {number_ligne}: malformed metadata option "
                            f"{option!r}, expected 'key=value'"
                        )
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
        self._connection.append((hub1, hub2, metadata))
        self._connection_line_numbers.append(number_ligne)

    def _check_duplicate_hub_names(self) -> None:
        """Check that all zone names are unique across hubs.

        Raises:
            ValueError: If two zones share the same name.
        """
        hubs: list[ZoneConfig] = [
            cast(ZoneConfig, self._start_hub),
            *self._hub,
            cast(ZoneConfig, self._end_hub),
        ]

        names: set[str] = set()
        for hub in hubs:
            name = hub["name"]
            if name in names:
                raise ValueError(f"Duplicate hub name: {name!r}")
            names.add(name)

    def _check_duplicate_connections(self) -> None:
        """Check that no connection is defined twice
        (a-b and b-a are duplicates).

        Raises:
            ValueError: If a duplicate connection is found.
        """
        connections: set[tuple[str, str]] = set()
        for c in self._connection:
            hub1, hub2 = c[0], c[1]
            if (hub1, hub2) in connections or (hub2, hub1) in connections:
                raise ValueError(f"Duplicate connection: {hub1!r} - {hub2!r}")
            connections.add((hub1, hub2))

    def _check_name_connections(self) -> None:
        """Check that all connection endpoints reference defined zones.

        Raises:
            ValueError: If a connection references an undefined zone.
        """
        known_names = {
            cast(ZoneConfig, self._start_hub)["name"],
            cast(ZoneConfig, self._end_hub)["name"],
        }
        known_names.update(hub["name"] for hub in self._hub)

        for (hub1, hub2, _), line_number in zip(
            self._connection, self._connection_line_numbers
        ):
            if hub1 not in known_names:
                raise ValueError(
                    f"Line {line_number}: "
                    f"Connection references undefined zone: {hub1!r}"
                )
            if hub2 not in known_names:
                raise ValueError(
                    f"Line {line_number}: "
                    f"Connection references undefined zone: {hub2!r}"
                )
