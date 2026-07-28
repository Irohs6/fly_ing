import math
import os
from src.model.graph import Graph
from .drone_animator import DroneAnimationLayer
from .camera import Camera
from .coordinate_system import CoordinateSystem

os.environ["PYGAME_HIDE_SUPPORT_PROMPT"] = "1"

try:
    import pygame
    from pygame.locals import (
        QUIT,
        KEYDOWN,
        K_ESCAPE,
        K_r,
        MOUSEWHEEL,
        MOUSEBUTTONDOWN,
        MOUSEBUTTONUP,
        MOUSEMOTION,
        K_SPACE,
        K_LEFT,
        K_RIGHT,
    )
except ImportError:
    print("Pygame is not installed. Please install it to run the visualization.")
    exit(1)

# ── Constants ───────────────────────────────────────────────────────────────

BG_COLOR = (20, 20, 25)

COLOR_MAP: dict[str, tuple[int, int, int]] = {
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

# ── HubRenderer ─────────────────────────────────────────────────────────────


class HubRenderer:
    HUB_BASE_RADIUS: int = 20
    HUB_SCALE: int = 3
    HUB_MIN_RADIUS: int = 20
    HUB_MAX_RADIUS: int = 55
    TEXT_COLOR = (255, 255, 255)

    def __init__(self, font: pygame.font.Font, font_small: pygame.font.Font):
        self.font = font
        self.font_small = font_small

    def radius(self, zone, zoom: float = 1.0) -> int:
        hub_r = self.HUB_BASE_RADIUS + zone.max_drones * self.HUB_SCALE
        hub_r = max(self.HUB_MIN_RADIUS, min(self.HUB_MAX_RADIUS, hub_r))
        return max(4, int(hub_r * zoom))

    def draw(self, screen, zone, pos, zoom=1.0, is_start=False, is_end=False):
        color = COLOR_MAP.get(zone.color, (200, 200, 200))
        hub_r = self.radius(zone, zoom)

        pygame.draw.circle(screen, color, pos, hub_r)

        if is_start or is_end:
            pygame.draw.circle(screen, (255, 215, 0), pos, hub_r, 3)
        else:
            pygame.draw.circle(screen, (255, 255, 255), pos, hub_r, 2)

        name_surf = self.font_small.render(zone.name, True, self.TEXT_COLOR)
        name_rect = name_surf.get_rect(center=(pos[0], pos[1] - hub_r - 11))
        screen.blit(name_surf, name_rect)

        cap_surf = self.font.render(
            f"{zone.nb_drones}/{zone.max_drones}", True, self.TEXT_COLOR
        )
        cap_rect = cap_surf.get_rect(center=(pos[0], pos[1] + hub_r + 20))
        screen.blit(cap_surf, cap_rect)


# ── ConnectionRenderer ──────────────────────────────────────────────────────


class ConnectionRenderer:
    CONN_FILL = (55, 60, 78)
    CONN_BORDER = (40, 45, 60)
    BAND_WIDTH: int = 9

    def __init__(self, font_small: pygame.font.Font):
        self.font_small = font_small

    def draw(self, screen, connection, pos1, pos2, zoom=1.0):
        if math.hypot(pos2[0] - pos1[0], pos2[1] - pos1[1]) == 0:
            return

        line_w = max(2, int(self.BAND_WIDTH * zoom))
        pygame.draw.line(screen, self.CONN_FILL, pos1, pos2, line_w)
        pygame.draw.line(screen, self.CONN_BORDER, pos1, pos2, max(1, line_w - 2))

        mid = ((pos1[0] + pos2[0]) // 2, (pos1[1] + pos2[1]) // 2)
        surf = self.font_small.render(
            f"{connection.nb_drones}/{connection.max_capacity}",
            True,
            (120, 130, 150),
        )
        rect = surf.get_rect(center=mid)
        pygame.draw.rect(screen, BG_COLOR, rect.inflate(6, 4), border_radius=3)
        screen.blit(surf, rect)


# ── GraphRenderer ───────────────────────────────────────────────────────────


class GraphRenderer:
    def __init__(self, graph, screen, font, font_small, coordinate_system):
        self.graph = graph
        self.screen = screen
        self.coord = coordinate_system
        self.world_positions = self.coord.world_positions

        self.hub_renderer = HubRenderer(font, font_small)
        self.connection_renderer = ConnectionRenderer(font_small)

    def draw(self, camera):
        screen_w, screen_h = self.screen.get_size()
        self.screen.fill(BG_COLOR)

        positions = {
            name: camera.world_to_screen(x, y, screen_w, screen_h)
            for name, (x, y) in self.world_positions.items()
        }

        for conn in self.graph.connections:
            pos1 = positions.get(conn.source.name)
            pos2 = positions.get(conn.target.name)
            if pos1 and pos2:
                self.connection_renderer.draw(self.screen, conn, pos1, pos2, camera.zoom)

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


# ── Pygame_view ─────────────────────────────────────────────────────────────


class Pygame_view:
    SCREEN_W = 1600
    SCREEN_H = 900
    CELL_SIZE = 160

    def __init__(self, graph: Graph, simulation=None):
        self.graph = graph
        self.simulation = simulation
        self.animation_layer = None

    def display(self):
        pygame.init()
        screen = pygame.display.set_mode((self.SCREEN_W, self.SCREEN_H), pygame.RESIZABLE)
        pygame.display.set_caption("Fly'in")

        font = pygame.font.SysFont("time_new_roman", 30)
        font_small = pygame.font.SysFont("times", 20, bold=True)
        clock = pygame.time.Clock()

        camera = Camera()

        coord = CoordinateSystem(cell_size=self.CELL_SIZE)
        coord.compute(self.graph.zones.values())

        renderer = GraphRenderer(self.graph, screen, font, font_small, coord)

        if self.simulation and self.simulation.tours:
            self.animation_layer = DroneAnimationLayer(
                hub_positions=coord.world_positions,
                tours=self.simulation.tours,
                auto_replay_speed=1.5,
            )

        running = True
        while running:
            dt = clock.tick(60) / 1000.0
            screen_w, screen_h = screen.get_size()

            for event in pygame.event.get():
                if event.type == QUIT:
                    running = False

                elif event.type == KEYDOWN:
                    if event.key == K_ESCAPE:
                        running = False
                    elif event.key == K_r:
                        camera.reset()

                else:
                    # Gestion du zoom
                    if event.type == MOUSEWHEEL:
                        mouse_x, mouse_y = pygame.mouse.get_pos()
                        factor = 1.15 if event.y > 0 else 1 / 1.15
                        camera.apply_zoom(mouse_x, mouse_y, screen_w, screen_h, factor)

                    # Début du drag (bouton milieu ou droit)
                    elif event.type == MOUSEBUTTONDOWN and event.button in (2, 3):
                        camera.start_drag(event.pos[0], event.pos[1])

                    # Fin du drag
                    elif event.type == MOUSEBUTTONUP and event.button in (2, 3):
                        camera.end_drag()

                    # Drag en cours
                    elif event.type == MOUSEMOTION:
                        camera.drag(event.pos[0], event.pos[1])


                if self.animation_layer:
                    self.animation_layer.handle_event(event)

            if self.animation_layer:
                self.animation_layer.update(dt)

            renderer.draw(camera)

            if self.animation_layer:
                self.animation_layer.draw(
                    surface=screen,
                    camera=camera,
                    screen_width=screen_w,
                    screen_height=screen_h,
                    zoom=camera.zoom,
                )
                self.animation_layer.draw_overlay(
                    surface=screen,
                    font=font_small,
                    screen_width=screen_w,
                    screen_height=screen_h,
                )

            pygame.display.flip()

        pygame.quit()
