import math
import pygame

from src.view.utils.camera import Camera
from src.view.utils.coordinate_system import CoordinateSystem


# ───────────────────────────────────────────────
# HubRenderer
# ───────────────────────────────────────────────

class HubRenderer:
    BG_COLOR = (20, 20, 25)

    COLOR_MAP = {
        "black": (40, 40, 45),
        "blue": (0, 128, 255),
        "brown": (120, 70, 30),
        "crimson": (220, 20, 60),
        "cyan": (43, 220, 255),
        "darkred": (139, 0, 0),
        "gold": (255, 215, 0),
        "green": (50, 200, 80),
        "lime": (150, 255, 50),
        "magenta": (200, 0, 200),
        "maroon": (128, 0, 0),
        "orange": (255, 128, 0),
        "purple": (160, 60, 200),
        "rainbow": (255, 100, 150),
        "red": (220, 50, 50),
        "violet": (130, 80, 220),
        "yellow": (220, 200, 30),
        "white": (200, 200, 200),
    }

    HUB_BASE_RADIUS = 20
    HUB_SCALE = 3
    HUB_MIN_RADIUS = 20
    HUB_MAX_RADIUS = 55
    TEXT_COLOR = (255, 255, 255)

    def __init__(self, font, font_small):
        self.font = font
        self.font_small = font_small

    def radius(self, zone, zoom):
        r = self.HUB_BASE_RADIUS + zone.max_drones * self.HUB_SCALE
        r = max(self.HUB_MIN_RADIUS, min(self.HUB_MAX_RADIUS, r))
        return max(4, int(r * zoom))

    def draw(self, screen, zone, pos, zoom, is_start=False, is_end=False):
        color = self.COLOR_MAP.get(zone.color, (200, 200, 200))
        r = self.radius(zone, zoom)

        pygame.draw.circle(screen, color, pos, r)

        if is_start or is_end:
            pygame.draw.circle(screen, (255, 215, 0), pos, r, 3)
        else:
            pygame.draw.circle(screen, (255, 255, 255), pos, r, 2)

        name_surf = self.font_small.render(zone.name, True, self.TEXT_COLOR)
        name_rect = name_surf.get_rect(center=(pos[0], pos[1] - r - 11))
        screen.blit(name_surf, name_rect)

        cap_surf = self.font.render(
            f"{zone.nb_drones}/{zone.max_drones}", True, self.TEXT_COLOR
        )
        cap_rect = cap_surf.get_rect(center=(pos[0], pos[1] + r + 20))
        screen.blit(cap_surf, cap_rect)


# ───────────────────────────────────────────────
# ConnectionRenderer
# ───────────────────────────────────────────────

class ConnectionRenderer:
    BG_COLOR = (20, 20, 25)
    CONN_FILL = (55, 60, 78)
    CONN_BORDER = (40, 45, 60)
    BAND_WIDTH = 9

    def __init__(self, font_small):
        self.font_small = font_small

    def draw(self, screen, connection, pos1, pos2, zoom):
        if math.hypot(pos2[0] - pos1[0], pos2[1] - pos1[1]) == 0:
            return

        w = max(2, int(self.BAND_WIDTH * zoom))
        pygame.draw.line(screen, self.CONN_FILL, pos1, pos2, w)
        pygame.draw.line(screen, self.CONN_BORDER, pos1, pos2, max(1, w - 2))

        mid = ((pos1[0] + pos2[0]) // 2, (pos1[1] + pos2[1]) // 2)
        surf = self.font_small.render(
            f"{connection.nb_drones}/{connection.max_capacity}",
            True,
            (120, 130, 150),
        )
        rect = surf.get_rect(center=mid)
        pygame.draw.rect(screen, self.BG_COLOR, rect.inflate(6, 4), border_radius=3)
        screen.blit(surf, rect)


# ───────────────────────────────────────────────
# GraphRenderer
# ───────────────────────────────────────────────

class GraphRenderer:
    BG_COLOR = (20, 20, 25)

    def __init__(self, graph, screen, font, font_small, coordinate_system):
        self.graph = graph
        self.screen = screen
        self.coord = coordinate_system
        self.world_positions = self.coord.world_positions

        self.hub_renderer = HubRenderer(font, font_small)
        self.connection_renderer = ConnectionRenderer(font_small)

    def draw(self, camera):
        screen_w, screen_h = self.screen.get_size()
        self.screen.fill(self.BG_COLOR)

        positions = {
            name: camera.world_to_screen(x, y, screen_w, screen_h)
            for name, (x, y) in self.world_positions.items()
        }

        for conn in self.graph.connections:
            pos1 = positions.get(conn.source.name)
            pos2 = positions.get(conn.target.name)
            if pos1 and pos2:
                self.connection_renderer.draw(
                    self.screen, conn, pos1, pos2, camera.zoom
                )

        for zone in self.graph.zones.values():
            pos = positions.get(zone.name)
            if pos:
                self.hub_renderer.draw(
                    self.screen,
                    zone,
                    pos,
                    zoom=camera.zoom,
                    is_start=(zone == self.graph.start_zone),
                    is_end=(zone == self.graph.end_zone),
                )
