# Easy Level 3: Basic capacity management
# nb_drones: 4

# start_hub: start 0 0 [color=green max_drones=4]
# hub: bottleneck 1 0 [color=orange max_drones=2]
# hub: wide_area 2 0 [color=blue max_drones=3]
# end_hub: goal 3 0 [color=red max_drones=4]

# connection: start-bottleneck [max_link_capacity=4]
# connection: bottleneck-wide_area [max_link_capacity=4]
# connection: wide_area-goal [max_link_capacity=4]


class Parser:
    """Parses drone routing map files into a structured config dict."""

    VALID_HUB_METADATA_KEYS = {"zone", "color", "max_drones"}
    VALID_CONNECTION_METADATA_KEYS = {"max_link_capacity"}
    VALID_ZONE_TYPES = {"normal", "blocked", "restricted", "priority"}

    def __init__(self, file_path: str) -> None:
        """Initialize the parser with the path to the map file.

        Args:
            file_path: Path to the map file to parse.
        """
        self.file_path = file_path
        self.config = {
            "start_hub": None,
            "end_hub": None,
            "hub": [],
            "connection": [],
            "nb_drones": None
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
            lines = self._read_file()
            self._parse_lines(lines)
            self._validate()
        except FileNotFoundError:
            raise FileNotFoundError(f"File not found: {self.file_path}")
        except ValueError as e:
            raise ValueError(f"Parse error: {e}") from e
        except IOError as e:
            raise IOError(f"Error reading file {self.file_path}: {e}") from e

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
                if line.startswith("#"):
                    continue
                line = line.strip()
                if not line:
                    continue
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
            if nb_drones is None and not line.startswith("nb_drones:"):
                raise ValueError(
                    f"Line {number_ligne}: expected 'nb_drones:'"
                    f", got: {line!r}"
                )
            if line.startswith("nb_drones:"):
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
                line.startswith("start_hub:")
                or line.startswith("hub:")
                or line.startswith("end_hub:")
            ):
                self._parse_hub_line(line, number_ligne)
            elif line.startswith("connection:"):
                self._parse_connection_line(line, number_ligne)
            else:
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
        if self.config["start_hub"] is None or self.config["end_hub"] is None:
            raise ValueError("Missing start_hub or end_hub definition")
        self._check_duplicate_hub_names()
        self._check_duplicate_connections()
        self._check_name_connections()

    def _parse_hub_line(self, line: str, number_ligne: int) -> None:
        """Parse a hub line and add the zone to self.config.

        Args:
            line: The raw line from the file.
            number_ligne: Physical line number used for error messages.

        Raises:
            ValueError: If the line format or metadata is invalid.
        """
        # Example: start_hub: start 0 0 [color=green max_drones=4]
        parts = line.split()
        if len(parts) < 4:
            raise ValueError(
                f"Line {number_ligne}: hub line must have format "
                f"'<type>: <name> <x> <y> [metadata]'"
            )
        hub_type = parts[0].rstrip(":")  # start_hub, hub, or end_hub
        name = parts[1]
        if "-" in name:
            raise ValueError(
                f"Line {number_ligne}: "
                f"zone name {name!r} cannot contain dashes"
            )
        try:
            x, y = int(parts[2]), int(parts[3])
        except ValueError:
            raise ValueError(
                f"Line {number_ligne}: invalid coordinates: {parts[2]!r}, "
                f"{parts[3]!r}"
            )
        metadata: dict[str, str | int] = {}
        if len(parts) > 4:
            metadata_part = " ".join(parts[4:])
            if metadata_part.startswith("[") and metadata_part.endswith("]"):
                metadata_part = metadata_part[1:-1]  # Remove brackets
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
        # Example: connection: start-bottleneck [max_link_capacity=4]
        parts = line.split()
        if len(parts) < 2:
            raise ValueError(
                f"Line {number_ligne}: invalid connection format: {line!r}"
            )
        connection_part = parts[1]
        if "-" not in connection_part:
            raise ValueError(
                f"Line {number_ligne}: "
                f"connection must be in format 'hub1-hub2'"
            )
        hub1, hub2 = connection_part.split("-", 1)
        metadata: dict[str, str | int] = {}
        if len(parts) > 2:
            metadata_part = " ".join(parts[2:])
            if metadata_part.startswith("[") and metadata_part.endswith("]"):
                metadata_part = metadata_part[1:-1]  # Remove brackets
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


if __name__ == "__main__":
    import sys

    path = (
        sys.argv[1]
        if len(sys.argv) > 1
        else "assets/maps/challenger/01_the_impossible_dream.txt"
    )
    try:
        p = Parser(path)
        config = p.parse()
        if config:
            print("nb_drones :", config["nb_drones"])

            print("=" * 50)
            print("\noptions for start_hub:\n")

            for name, value in config["start_hub"].items():
                print(f"start_hub {name}: {value}")
            print("=" * 50)
            print("\noptions for hubs:\n")
            for hub in config["hub"]:
                for name, value in hub.items():
                    print(f"hub {name}: {value}")
                print()
            print("=" * 50)
            print("\noptions for end_hub:\n")
            for name, value in config["end_hub"].items():
                print(f"end_hub {name}: {value}")
            print("=" * 50)
            print("\nconnections:")
            for c in config["connection"]:
                if len(c) == 3:
                    for name, value in c[2].items():
                        print(
                            f"connection: {c[0]} - {c[1]} option: "
                            f"{name}: {value}"
                        )
                else:
                    print(f"connection: {c[0]} - {c[1]}")
    except Exception as e:
        print(f"Error: {e}")
