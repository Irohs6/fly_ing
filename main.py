import sys
from src.controller.controller import Controller


def main() -> None:
    if len(sys.argv) < 2:
        print("Usage: python main.py <path/to/map_file.txt> [--debug]")
        sys.exit(1)

    map_path = sys.argv[1]
    debug = "--debug" in sys.argv

    try:
        controller = Controller(map_path, debug=debug)
        controller.display()
    except (ValueError, FileNotFoundError, IOError) as e:
        print(f"Error: {e}", file=sys.stderr)
        sys.exit(1)


if __name__ == "__main__":
    main()
