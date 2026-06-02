import math

import os

os.environ["PYGAME_HIDE_SUPPORT_PROMPT"] = "1"

try:
    import pygame  # noqa : F402
    from pygame.locals import *
except ImportError:
    print(
        "Pygame is not installed. Please install it to run the visualization."
    )
    exit(1)

from src.model.graph import Graph

# Display constants
# ---------------------------------------------------------------------------

SCREEN_W: int = 2000
SCREEN_H: int = 1800
MARGIN: int = 120
ZONE_RADIUS: int = 36
BG_COLOR: tuple[int, int, int] = (15, 15, 25)
TEXT_COLOR: tuple[int, int, int] = (220, 220, 230)
LINE_COLOR: tuple[int, int, int] = (90, 90, 110)

COLOR_MAP: dict[str, tuple[int, int, int]] = {
    "black": (20, 20, 20),
    "blue": (23, 37, 60),
    "brown": (50, 26, 12),
    "crimson": (220, 20, 60),
    "cyan": (43, 255, 255),
    "darkred": (139, 0, 0),
    "gold": (255, 215, 0),
    "green": (50, 200, 80),
    "lime": (150, 255, 50),
    "magenta": (200, 0, 200),
    "maroon": (128, 0, 0),
    "orange": (220, 140, 30),
    "purple": (160, 60, 200),
    "rainbow": (255, 100, 150),
    "red": (220, 70, 60),
    "violet": (130, 80, 220),
    "yellow": (220, 200, 30),
    "white": (200, 200, 200),
}


class Pygame_view:
    def __init__(self, graph: Graph) -> None:
        self.graph = graph
        self.screen = None
        self.font = None
        self.font_small = None
        self.clock = None
        self.zones = graph.zones
        self.connections = graph.connections

    def display(self) -> None:
        pygame.init()
        screen = pygame.display.set_mode((3700, 2000))
        pygame.display.set_caption("Fly'in")

        running = True
        while running:
            for event in pygame.event.get():
                if event.type == KEYDOWN and event.key == K_ESCAPE:
                    running = False
            self.display_map(screen)

        pygame.quit()

    def grid_to_pixel(
        self, x: int, y: int, cell_size: int = 150
    ) -> tuple[int, int]:
        zones = self.graph.zones.values()
        max_x = max(zone.x for zone in zones)
        max_y = max(zone.y for zone in zones)
        offset_x = SCREEN_W // 2 - (max_x * cell_size) // 2
        offset_y = SCREEN_H // 2 - (max_y * cell_size) // 2
        return (offset_x + x * cell_size, offset_y + y * cell_size)

    def draw_start_zone(
        self, screen: pygame.Surface, color: str, pos: tuple[int, int]
    ) -> None:
        N_BLADES = 8
        OUTER_R = ZONE_RADIUS
        PERIOD_MS = 3000

        t = (
            1 - math.cos(2 * math.pi * pygame.time.get_ticks() / PERIOD_MS)
        ) / 2

        inner_r = OUTER_R * (0.08 + t * 0.90)
        angle_step = 2 * math.pi / N_BLADES
        blade_span = angle_step * 0.98
        twist = angle_step * 0.35

        cx, cy = pos
        pygame.draw.circle(screen, (20, 22, 32), pos, OUTER_R)

        for i in range(N_BLADES):
            base = i * angle_step
            oa1 = base - blade_span / 2
            oa2 = base + blade_span / 2
            ia1 = oa1 + twist
            ia2 = oa2 + twist
            points = [
                (cx + OUTER_R * math.cos(oa1), cy + OUTER_R * math.sin(oa1)),
                (cx + OUTER_R * math.cos(oa2), cy + OUTER_R * math.sin(oa2)),
                (cx + inner_r * math.cos(ia2), cy + inner_r * math.sin(ia2)),
                (cx + inner_r * math.cos(ia1), cy + inner_r * math.sin(ia1)),
            ]
            color_ = COLOR_MAP.get(color, (200, 200, 200))
            pygame.draw.polygon(screen, color_, points)

        pygame.draw.circle(screen, (255, 255, 255), pos, OUTER_R, 2)

    def draw_zone(
        self, screen: pygame.Surface, zone_color: str, pos: tuple[int, int]
    ) -> None:
        color = COLOR_MAP.get(zone_color, (200, 200, 200))
        pygame.draw.circle(screen, color, pos, ZONE_RADIUS)
        pygame.draw.circle(screen, (255, 255, 255), pos, ZONE_RADIUS, 2)

    def draw_connection(
        self,
        screen: pygame.Surface,
        pos1: tuple[int, int],
        pos2: tuple[int, int],
    ) -> None:
        pygame.draw.line(screen, LINE_COLOR, pos1, pos2, 3)

    def display_map(self, screen: pygame.Surface) -> None:
        screen.fill(BG_COLOR)
        start_zone = self.graph.start_zone

        self.draw_start_zone(
            screen,
            start_zone.color,
            self.grid_to_pixel(start_zone.x, start_zone.y),
        )
        for zone in self.graph.zones.values():
            if zone != start_zone and zone != self.graph.end_zone:
                self.draw_zone(
                    screen, zone.color, self.grid_to_pixel(zone.x, zone.y)
                )
        for connection in self.graph.connections:
            source_zone = self.graph.zones[connection.source]
            target_zone = self.graph.zones[connection.target]
            self.draw_connection(
                screen,
                self.grid_to_pixel(source_zone.x, source_zone.y),
                self.grid_to_pixel(target_zone.x, target_zone.y),
            )
        self.draw_start_zone(
            screen,
            self.graph.end_zone.color,
            self.grid_to_pixel(self.graph.end_zone.x, self.graph.end_zone.y),
        )

        pygame.display.flip()
