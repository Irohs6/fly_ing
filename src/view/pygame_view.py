import math
import os
from src.model.graph import Graph

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
    )
except ImportError:
    print(
        "Pygame is not installed. Please install it to run the visualization."
    )
    exit(1)


# ── Constants

SCREEN_W: int = 1600
SCREEN_H: int = 900
CELL_SIZE: int = 160

BG_COLOR = (20, 20, 25)
TEXT_COLOR = (255, 255, 255)
CONN_FILL = (55, 60, 78)
CONN_BORDER = (40, 45, 60)

BAND_WIDTH: int = 9

HUB_BASE_RADIUS: int = 20
HUB_SCALE: int = 3  # extra px per max_drone unit
HUB_MIN_RADIUS: int = 20
HUB_MAX_RADIUS: int = 55

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


# ── Camera ───────────────────────────────────────────────────────────────────


class Camera:
    ZOOM_MIN: float = 0.15
    ZOOM_MAX: float = 5.0

    def __init__(self) -> None:
        self.zoom: float = 1.0
        self.pan_x: float = 0.0
        self.pan_y: float = 0.0
        self._drag: tuple | None = None

    def handle_event(self, event, sw: int, sh: int) -> None:
        if event.type == MOUSEWHEEL:
            # Zoom centré sur la position de la souris
            mouse_x, mouse_y = pygame.mouse.get_pos()
            # Convertir la position souris en coordonnées monde avant zoom
            world_x = (mouse_x - sw / 2 - self.pan_x) / self.zoom
            world_y = (mouse_y - sh / 2 - self.pan_y) / self.zoom
            factor = 1.15 if event.y > 0 else 1 / 1.15
            self.zoom = max(
                self.ZOOM_MIN, min(self.ZOOM_MAX, self.zoom * factor)
            )
            # Recalculer le pan pour que le point monde reste sous la souris
            self.pan_x = mouse_x - sw / 2 - world_x * self.zoom
            self.pan_y = mouse_y - sh / 2 - world_y * self.zoom
        elif event.type == MOUSEBUTTONDOWN and event.button in (2, 3):
            # Mémoriser le point de départ du drag et le pan courant
            self._drag = (*event.pos, self.pan_x, self.pan_y)
        elif event.type == MOUSEBUTTONUP and event.button in (2, 3):
            self._drag = None
        elif event.type == MOUSEMOTION and self._drag:
            # Déplacer le pan en fonction du déplacement
            # depuis le début du drag
            drag_start_x, drag_start_y, pan_start_x, pan_start_y = self._drag
            self.pan_x = pan_start_x + event.pos[0] - drag_start_x
            self.pan_y = pan_start_y + event.pos[1] - drag_start_y

    def reset(self) -> None:
        self.zoom = 1.0
        self.pan_x = 0.0
        self.pan_y = 0.0

    def to_screen(
        self, world_x: float, world_y: float, sw: int, sh: int
    ) -> tuple[int, int]:
        """Convertit des coordonnées monde en pixels écran."""
        return (
            int(world_x * self.zoom + sw / 2 + self.pan_x),
            int(world_y * self.zoom + sh / 2 + self.pan_y),
        )


# ── HubRenderer


class HubRenderer:
    def __init__(
        self, font: pygame.font.Font, font_small: pygame.font.Font
    ) -> None:
        self.font = font
        self.font_small = font_small

    def radius(self, zone, zoom: float = 1.0) -> int:
        """Calcule le rayon d'un hub en pixels selon sa capacité et le zoom."""
        hub_r = HUB_BASE_RADIUS + zone.max_drones * HUB_SCALE
        hub_r = max(HUB_MIN_RADIUS, min(HUB_MAX_RADIUS, hub_r))
        return max(4, int(hub_r * zoom))

    def draw(
        self,
        screen: pygame.Surface,
        zone,
        pos: tuple[int, int],
        zoom: float = 1.0,
        is_start: bool = False,
        is_end: bool = False,
    ) -> None:
        color = COLOR_MAP.get(zone.color, (200, 200, 200))
        hub_r = self.radius(zone, zoom)

        pygame.draw.circle(screen, color, pos, hub_r)
        if is_start or is_end:
            # Bordure épaisse dorée pour distinguer les hubs de départ/arrivée
            pygame.draw.circle(screen, (255, 215, 0), pos, hub_r, 3)
        else:
            pygame.draw.circle(screen, (255, 255, 255), pos, hub_r, 2)

        # Nom du hub affiché au-dessus
        name_surf = self.font_small.render(zone.name, True, TEXT_COLOR)
        name_rect = name_surf.get_rect(center=(pos[0], pos[1] - hub_r - 11))
        screen.blit(name_surf, name_rect)

        # Capacité affichée en dessous (0/max — simulation non démarrée)
        cap_surf = self.font.render(
            f"0/{zone.max_drones}", True, (255, 255, 255)
        )
        cap_rect = cap_surf.get_rect(center=(pos[0], pos[1] + hub_r + 20))
        screen.blit(cap_surf, cap_rect)


# ── ConnectionRenderer


class ConnectionRenderer:
    def __init__(self, font_small: pygame.font.Font) -> None:
        self.font_small = font_small

    def draw(
        self,
        screen: pygame.Surface,
        connection,
        pos1: tuple[int, int],
        pos2: tuple[int, int],
        zoom: float = 1.0,
    ) -> None:
        capacity = connection.max_capacity
        if math.hypot(pos2[0] - pos1[0], pos2[1] - pos1[1]) == 0:
            return

        # Trait unique, épaisseur mise à l'échelle selon le zoom
        line_w = max(2, int(BAND_WIDTH * zoom))
        pygame.draw.line(screen, CONN_FILL, pos1, pos2, line_w)
        pygame.draw.line(screen, CONN_BORDER, pos1, pos2, max(1, line_w - 2))

        # Capacité affichée au milieu de la connexion
        mid = ((pos1[0] + pos2[0]) // 2, (pos1[1] + pos2[1]) // 2)
        surf = self.font_small.render(f"0/{capacity}", True, (120, 130, 150))
        rect = surf.get_rect(center=mid)
        # Fond sombre derrière le texte pour la lisibilité
        pygame.draw.rect(screen, BG_COLOR, rect.inflate(6, 4), border_radius=3)
        screen.blit(surf, rect)


# ── GraphRenderer


class GraphRenderer:
    def __init__(
        self,
        graph: Graph,
        screen: pygame.Surface,
        font: pygame.font.Font,
        font_small: pygame.font.Font,
    ) -> None:
        self.graph = graph
        self.screen = screen
        self.hub_renderer = HubRenderer(font, font_small)
        self.connection_renderer = ConnectionRenderer(font_small)
        self._base: dict[str, tuple[float, float]] = {}
        self._compute_layout()

    def _compute_layout(self) -> None:
        """Calcule les coordonnées monde de chaque hub,
        centrées sur l'origine."""
        zones = list(self.graph.zones.values())
        if not zones:
            return
        # Centre géométrique de la grille pour centrer la carte à l'écran
        center_x = (max(z.x for z in zones) + min(z.x for z in zones)) / 2
        center_y = (max(z.y for z in zones) + min(z.y for z in zones)) / 2
        for zone in zones:
            self._base[zone.name] = (
                (zone.x - center_x) * CELL_SIZE,
                (zone.y - center_y) * CELL_SIZE,
            )

    def draw(self, camera: Camera) -> None:
        """Efface l'écran et redessine tout le graphe via la caméra."""
        screen_w, screen_h = self.screen.get_size()
        self.screen.fill(BG_COLOR)

        # Convertir toutes les positions monde en pixels écran une seule fois
        positions = {
            name: camera.to_screen(world_x, world_y, screen_w, screen_h)
            for name, (world_x, world_y) in self._base.items()
        }

        # Connexions dessinées en premier (sous les hubs)
        for conn in self.graph.connections:
            pos_source = positions.get(conn.source.name)
            pos_target = positions.get(conn.target.name)
            if pos_source and pos_target:
                self.connection_renderer.draw(
                    self.screen, conn, pos_source, pos_target, camera.zoom
                )

        # Hubs dessinés par-dessus les connexions
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

        pygame.display.flip()


# ── Pygame_view (driver)


class Pygame_view:
    def __init__(self, graph: Graph) -> None:
        self.graph = graph

    def display(self) -> None:
        pygame.init()
        screen = pygame.display.set_mode(
            (SCREEN_W, SCREEN_H), pygame.RESIZABLE
        )
        pygame.display.set_caption("Fly'in")
        font = pygame.font.SysFont("time_new_roman", 30)
        font_small = pygame.font.SysFont("times", 20, bold=True)
        clock = pygame.time.Clock()
        camera = Camera()
        renderer = GraphRenderer(self.graph, screen, font, font_small)

        running = True
        while running:
            screen_w, screen_h = screen.get_size()
            for event in pygame.event.get():
                if event.type == QUIT:
                    running = False
                elif event.type == KEYDOWN:
                    if event.key == K_ESCAPE:  # Quitter
                        running = False
                    elif event.key == K_r:  # Réinitialiser la caméra
                        camera.reset()
                else:
                    # Déléguer zoom et pan à la caméra
                    camera.handle_event(event, screen_w, screen_h)
            renderer.draw(camera)
            clock.tick(60)

        pygame.quit()
