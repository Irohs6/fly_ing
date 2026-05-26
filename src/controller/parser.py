from pydantic import BaseModel, Field
from typing import Annotated, Any

# Easy Level 1: Simple linear path
# nb_drones: 2

# start_hub: start 0 0 [color=green]
# hub: waypoint1 1 0 [color=blue]
# hub: waypoint2 2 0 [color=blue]
# end_hub: goal 3 0 [color=red]

# connection: start-waypoint1
# connection: waypoint1-waypoint2
# connection: waypoint2-goal

# hub: conv_restricted1 13 2 [zone=restricted color=darkred max_drones=1]
# hub: conv_restricted2 14 2 [zone=restricted color=darkred max_drones=1]
# hub: conv_restricted3 15 2 [zone=restricted color=darkred max_drones=1]

# hub: conv_restricted4 13 0 [zone=restricted color=darkred max_drones=1]
# hub: conv_restricted5 14 0 [zone=restricted color=darkred max_drones=1]
# hub: conv_restricted6 15 0 [zone=restricted color=darkred max_drones=1]

# hub: conv_restricted7 13 -2 [zone=restricted color=darkred max_drones=1]
# hub: conv_restricted8 14 -2 [zone=restricted color=darkred max_drones=1]
# hub: conv_restricted9 15 -2 [zone=restricted color=darkred max_drones=1]
PositiveInt = Annotated[int, Field(gt=0)]


class Parser(BaseModel):

    nb_drones: PositiveInt
    start_hub: dict[str, Any]
    hubs: list[dict[str, Any]]
    end_hub: dict[str, Any]
    connections: list[tuple[str, str, dict[str, Any]]]

    @classmethod
    def read_file(cls, file_path: str) -> "Parser":
        try:
            options = {}
            hubs = []
            connections = []
            with open(file_path, 'r') as f:
                for line in f:
                    if line.startswith("#"):
                        continue  # Skip comments
                    line = line.strip()
                    if line.startswith("nb_drones:"):
                        nb_drones = int(line.split(":")[1].strip())
                    elif line.startswith("start_hub:") or line.startswith(
                            "end_hub:") or line.startswith("hub:"):
                        parts = line.split()
                        name = parts[1]
                        x = int(parts[2])
                        y = int(parts[3])
                        options = {
                                    option.strip('[]').split("=")[0]: option.strip('[]').split("=")[1]
                                    for option in parts[4:]
                                    if '=' in option
                                }
                        if line.startswith("start_hub:"):
                            start_hub = {"name": name, "position": (x, y),
                                         "options": options}
                        elif line.startswith("end_hub:"):
                            end_hub = {"name": name, "position": (x, y),
                                       "options": options}
                        else:
                            hubs.append({"name": name, "position": (x, y),
                                        "options": options})
                    elif line.startswith("connection:"):
                        parts = line.split()
                        hub1, hub2 = parts[1].split("-")
                        conn_options = {
                            opt.strip('[]').split("=")[0]: opt.strip('[]').split("=")[1]
                            for opt in parts[2:]
                            if '=' in opt
                        }
                        connections.append((hub1, hub2, conn_options))
            return cls(
                nb_drones=nb_drones,
                start_hub=start_hub,
                hubs=hubs,
                end_hub=end_hub,
                connections=connections
            )
        except FileNotFoundError:
            print(f"File not found: {file_path}")
        except IOError as e:
            print(f"Error reading file {file_path}: {e}")


if __name__ == "__main__":
    p = Parser.read_file("assets/maps/challenger/01_the_impossible_dream.txt")
    if p:
        print("nb_drones :", p.nb_drones)

        print("=" * 50)
        print("\noptions for start_hub:\n")

        for name, value in p.start_hub.items():
            print(f"start_hub {name}: {value}")
        print("=" * 50)
        print("\noptions for hubs:\n")
        for hub in p.hubs:
            for name, value in hub.items():
                print(f"hub {name}: {value}")
            print()
        print("=" * 50)
        print("\noptions for end_hub:\n")
        for name, value in p.end_hub.items():
            print(f"end_hub {name}: {value}")
        print("=" * 50)
        print("\nconnections:")
        for c in p.connections:
            if len(c) == 3:
                for name, value in c[2].items():
                    print(f"connection: {c[0]} - {c[1]} option: {name}: {value}")
            else:
                print(f"connection: {c[0]} - {c[1]}")
