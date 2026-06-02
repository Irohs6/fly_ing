import sys
from src.controller.controller import Controller


def main() -> None:
    if len(sys.argv) < 2:
        print("Usage: python main.py <path/to/map_file.txt>")
        sys.exit(1)

    map_path = sys.argv[1]

    controller = Controller(map_path)
    controller.display()


if __name__ == "__main__":
    main()
