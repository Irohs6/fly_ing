import sys
import math
from dataclasses import dataclass, field
import pygame

# ---------------------------------------------------------------------------
# Map data — easy_01 (linear path, 2 drones, target ≤ 6 turns)
# ---------------------------------------------------------------------------

ZONES: dict[str, dict] = {
    "start": {"x": 0, "y": 2, "type": "start",  "color": (50,  200, 80)},
    "zoneA": {"x": 2, "y": 2, "type": "normal", "color": (80,  120, 220)},
    "zoneB": {"x": 4, "y": 2, "type": "normal", "color": (80,  120, 220)},
    "zoneC": {"x": 6, "y": 2, "type": "normal", "color": (80,  120, 220)},
    "end":   {"x": 8, "y": 2, "type": "end",    "color": (220, 180,  30)},
}

CONNECTIONS: list[tuple[str, str]] = [
    ("start", "zoneA"),
    ("zoneA", "zoneB"),
    ("zoneB", "zoneC"),
    ("zoneC", "end"),
]

SIMULATION: list[dict[str, str]] = [
    {"D1": "start", "D2": "start", "D3": "start", "D4": "start"},
    {"D1": "zoneA", "D2": "start", "D3": "start", "D4": "start"},
    {"D1": "zoneB", "D2": "zoneA", "D3": "start", "D4": "start"},
    {"D1": "zoneC", "D2": "zoneB", "D3": "zoneA", "D4": "start"},
    {"D1": "end",   "D2": "zoneC", "D3": "zoneB", "D4": "zoneA"},
    {"D1": "end",   "D2": "end",   "D3": "zoneC", "D4": "zoneB"},
]

DRONE_COLORS: list[tuple[int, int, int]] = [
    (255, 80,  80),
    (80,  200, 255),
]

# ---------------------------------------------------------------------------
# Layout & animation constants
# ---------------------------------------------------------------------------

SCREEN_W:       int = 3000
SCREEN_H:       int = 1000
MARGIN_X:       int = 160
MARGIN_Y:       int = 320
MAP_X_MAX:      int = 8
MAP_Y_MAX:      int = 4
ZONE_RADIUS:    int = 70
DRONE_RADIUS:   int = 24
BG_COLOR:       tuple[int, int, int] = (15, 15, 25)
CORRIDOR_W_OUT: int = 44
CORRIDOR_W_IN:  int = 28
TEXT_COLOR:     tuple[int, int, int] = (220, 220, 230)
AUTO_DELAY:     int = 900
TRANS_DURATION: int = 450
BTN_H:          int = 100
BTN_W:          int = 340
BTN_GAP:        int = 30
BTN_MARGIN_Y:   int = 20

# ---------------------------------------------------------------------------
# Geometry helpers
# ---------------------------------------------------------------------------


def lerp(a: float, b: float, t: float) -> float:
    """Linear interpolation."""
    return a + (b - a) * t


def ease_in_out(t: float) -> float:
    """Smooth cubic ease-in-out."""
    return t * t * (3.0 - 2.0 * t)


def world_to_screen(x: float, y: float) -> tuple[int, int]:
    """Convert map coordinates to screen pixels."""
    scale_x: float = (SCREEN_W - 2 * MARGIN_X) / MAP_X_MAX
    scale_y: float = (SCREEN_H - 2 * MARGIN_Y) / MAP_Y_MAX
    return int(MARGIN_X + x * scale_x), int(MARGIN_Y + y * scale_y)


def hexagon_points(
    center: tuple[int, int],
    radius: int,
    angle_offset: float = 0.0,
) -> list[tuple[float, float]]:
    """Return 6 vertices of a regular hexagon."""
    return [
        (
            center[0] + radius * math.cos(math.radians(60 * i + angle_offset)),
            center[1] + radius * math.sin(math.radians(60 * i + angle_offset)),
        )
        for i in range(6)
    ]


# ---------------------------------------------------------------------------
# Glow helper
# ---------------------------------------------------------------------------


def draw_glow(
    surface: pygame.Surface,
    center: tuple[int, int],
    radius: int,
    color: tuple[int, int, int],
    intensity: float,
) -> None:
    """Draw a soft radial glow using an SRCALPHA surface."""
    size = radius * 4
    glow = pygame.Surface((size, size), pygame.SRCALPHA)
    cx, cy = size // 2, size // 2
    for r in range(size // 2, 0, -3):
        alpha = int(intensity * 80 * (1 - r / (size / 2)))
        alpha = max(0, min(255, alpha))
        pygame.draw.circle(glow, (*color, alpha), (cx, cy), r)
    surface.blit(glow, (center[0] - cx, center[1] - cy))


# ---------------------------------------------------------------------------
# Background
# ---------------------------------------------------------------------------


def draw_background(surface: pygame.Surface) -> None:
    """Dark background with a subtle dot grid."""
    surface.fill(BG_COLOR)
    dot_step, dot_color = 80, (28, 28, 42)
    for gx in range(0, SCREEN_W, dot_step):
        for gy in range(0, SCREEN_H, dot_step):
            pygame.draw.circle(surface, dot_color, (gx, gy), 2)


# ---------------------------------------------------------------------------
# Corridors
# ---------------------------------------------------------------------------


def draw_all_corridors(surface: pygame.Surface, flow_t: float) -> None:
    """Draw corridors as thick bordered paths with a moving flow dot."""
    for z1_name, z2_name in CONNECTIONS:
        p1 = world_to_screen(ZONES[z1_name]["x"], ZONES[z1_name]["y"])
        p2 = world_to_screen(ZONES[z2_name]["x"], ZONES[z2_name]["y"])

        pygame.draw.line(surface, (8, 8, 18),   p1, p2, CORRIDOR_W_OUT)
        pygame.draw.line(surface, (40, 45, 72), p1, p2, CORRIDOR_W_IN)

        dx, dy = p2[0] - p1[0], p2[1] - p1[1]
        length = math.hypot(dx, dy)
        if length > 0:
            half = CORRIDOR_W_IN // 2 - 3
            nx, ny = -dy / length * half, dx / length * half
            edge = (65, 70, 105)
            pygame.draw.line(surface, edge,
                             (int(p1[0] + nx), int(p1[1] + ny)),
                             (int(p2[0] + nx), int(p2[1] + ny)), 1)
            pygame.draw.line(surface, edge,
                             (int(p1[0] - nx), int(p1[1] - ny)),
                             (int(p2[0] - nx), int(p2[1] - ny)), 1)

        # Animated flow dot
        ft = flow_t % 1.0
        dot_x = int(lerp(p1[0], p2[0], ft))
        dot_y = int(lerp(p1[1], p2[1], ft))
        pygame.draw.circle(surface, (90, 110, 180), (dot_x, dot_y), 6)


# ---------------------------------------------------------------------------
# Hub drawing
# ---------------------------------------------------------------------------


def _hex_fill(
    surface: pygame.Surface,
    center: tuple[int, int],
    radius: int,
    fill: tuple[int, int, int],
    border: tuple[int, int, int],
    angle: float = 0.0,
) -> None:
    pts = hexagon_points(center, radius, angle)
    pygame.draw.polygon(surface, fill, pts)
    pygame.draw.polygon(surface, border, pts, 3)


def draw_hub_start(
    surface: pygame.Surface,
    center: tuple[int, int],
    t: float,
) -> None:
    """Animated green start hub: pulsing glow + rotating ring."""
    pulse = math.sin(t * math.pi * 2) * 0.2 + 0.8
    angle = t * 30

    draw_glow(surface, center, ZONE_RADIUS + 20, (50, 200, 80), pulse * 0.9)

    # Outer rotating hex outline
    pts_outer = hexagon_points(center, ZONE_RADIUS + 18, angle)
    pygame.draw.polygon(surface, (40, 120, 60), pts_outer, 3)

    fill   = (int(30 * pulse), int(140 * pulse), int(55 * pulse))
    border = (80, 255, 120)
    _hex_fill(surface, center, ZONE_RADIUS, fill, border)

    pygame.draw.circle(surface, (100, 255, 140), center, ZONE_RADIUS // 2)

    # Orbiting dots
    for i in range(3):
        a = math.radians(120 * i + angle * 3)
        ox = int(center[0] + (ZONE_RADIUS + 12) * math.cos(a))
        oy = int(center[1] + (ZONE_RADIUS + 12) * math.sin(a))
        pygame.draw.circle(surface, (150, 255, 170), (ox, oy), 7)


def draw_hub_end(
    surface: pygame.Surface,
    center: tuple[int, int],
    t: float,
) -> None:
    """Animated gold end hub: pulsing concentric rings."""
    pulse = math.sin(t * math.pi * 3) * 0.35 + 0.65

    draw_glow(surface, center, ZONE_RADIUS + 25, (220, 180, 30), pulse * 0.8)

    for ring in range(3, 0, -1):
        ring_r = ZONE_RADIUS + ring * 14 + int(pulse * 10)
        alpha_f = (4 - ring) / 3
        rc = (int(220 * alpha_f), int(180 * alpha_f), 0)
        pygame.draw.circle(surface, rc, center, ring_r, 2)

    fill   = (int(160 * pulse), int(130 * pulse), 0)
    border = (255, 220, 50)
    _hex_fill(surface, center, ZONE_RADIUS, fill, border, 30)
    pygame.draw.circle(surface, (255, 235, 60), center, ZONE_RADIUS // 2)


def draw_hub_normal(
    surface: pygame.Surface,
    center: tuple[int, int],
    color: tuple[int, int, int],
    t: float,
) -> None:
    """Gently pulsing normal hub."""
    pulse = math.sin(t * math.pi * 1.8) * 0.10 + 0.90
    r = int(ZONE_RADIUS * pulse)
    darker  = (int(color[0] * 0.4), int(color[1] * 0.4), int(color[2] * 0.4))
    brighter = (
        min(255, int(color[0] * 1.4)),
        min(255, int(color[1] * 1.4)),
        min(255, int(color[2] * 1.4)),
    )
    draw_glow(surface, center, r + 10, color, 0.35 * pulse)
    _hex_fill(surface, center, r, darker, brighter, 30)
    pygame.draw.circle(surface, color, center, r // 2)


def draw_all_hubs(
    surface: pygame.Surface,
    font: pygame.font.Font,
    t: float,
) -> None:
    """Draw every hub with its label."""
    for name, zone in ZONES.items():
        center = world_to_screen(zone["x"], zone["y"])
        ztype  = zone.get("type", "normal")

        if ztype == "start":
            draw_hub_start(surface, center, t)
        elif ztype == "end":
            draw_hub_end(surface, center, t)
        else:
            draw_hub_normal(surface, center, zone["color"], t)

        label = font.render(name, True, TEXT_COLOR)
        surface.blit(
            label,
            (center[0] - label.get_width() // 2, center[1] + ZONE_RADIUS + 8),
        )


# ---------------------------------------------------------------------------
# Drone drawing
# ---------------------------------------------------------------------------


def drone_screen_pos(
    drone_id: str,
    state: dict[str, str],
    prev_state: dict[str, str],
    trans_t: float,
    drone_idx: int,
    total_at_zone: int,
) -> tuple[int, int]:
    """Interpolate drone position between steps with stacking offset."""
    p1 = world_to_screen(ZONES[prev_state[drone_id]]["x"],
                         ZONES[prev_state[drone_id]]["y"])
    p2 = world_to_screen(ZONES[state[drone_id]]["x"],
                         ZONES[state[drone_id]]["y"])
    et = ease_in_out(trans_t)
    bx = int(lerp(p1[0], p2[0], et))
    by = int(lerp(p1[1], p2[1], et))
    offset = int((drone_idx - (total_at_zone - 1) / 2) * (DRONE_RADIUS * 2 + 12))
    return bx + offset, by


def draw_drone_shape(
    surface: pygame.Surface,
    pos: tuple[int, int],
    color: tuple[int, int, int],
    label: str,
    font: pygame.font.Font,
    rotor_angle: float,
) -> None:
    """Draw a stylised quadcopter (X frame) with animated rotors."""
    cx, cy = pos
    arm    = DRONE_RADIUS + 8
    arm_w  = 5
    rotor_r = 10

    # X-frame arms (45° diagonals)
    for angle_deg in (45, -45):
        rad = math.radians(angle_deg)
        dx, dy = int(arm * math.cos(rad)), int(arm * math.sin(rad))
        pygame.draw.line(surface, color, (cx - dx, cy - dy), (cx + dx, cy + dy), arm_w)

    # Rotors at four tips with spinning blades
    for tip_deg in (45, -45, 135, -135):
        rad = math.radians(tip_deg)
        rx, ry = int(cx + arm * math.cos(rad)), int(cy + arm * math.sin(rad))
        pygame.draw.circle(surface, color, (rx, ry), rotor_r, 2)
        for blade in range(2):
            ba  = math.radians(rotor_angle + blade * 90)
            bx2 = int(rx + (rotor_r - 2) * math.cos(ba))
            by2 = int(ry + (rotor_r - 2) * math.sin(ba))
            pygame.draw.line(surface, color, (rx, ry), (bx2, by2), 2)

    draw_glow(surface, pos, DRONE_RADIUS, color, 0.55)
    pygame.draw.circle(surface, color, pos, DRONE_RADIUS - 4)
    pygame.draw.circle(surface, (0, 0, 0), pos, DRONE_RADIUS - 4, 2)

    lbl = font.render(label, True, (0, 0, 0))
    surface.blit(lbl, (cx - lbl.get_width() // 2, cy - lbl.get_height() // 2))


def draw_all_drones(
    surface: pygame.Surface,
    font: pygame.font.Font,
    state: dict[str, str],
    prev_state: dict[str, str],
    trans_t: float,
    rotor_angle: float,
) -> None:
    """Draw all drones with interpolated positions."""
    per_zone: dict[str, list[str]] = {}
    for drone_id in state:
        per_zone.setdefault(state[drone_id], []).append(drone_id)

    for zone_drones in per_zone.values():
        total = len(zone_drones)
        for idx, drone_id in enumerate(zone_drones):
            num   = int(drone_id[1:]) - 1
            color = DRONE_COLORS[num % len(DRONE_COLORS)]
            pos   = drone_screen_pos(drone_id, state, prev_state,
                                     trans_t, idx, total)
            draw_drone_shape(surface, pos, color, drone_id, font, rotor_angle)


# ---------------------------------------------------------------------------
# HUD
# ---------------------------------------------------------------------------


def draw_hud(
    surface: pygame.Surface,
    font: pygame.font.Font,
    step: int,
    auto_play: bool,
) -> None:
    """Draw turn counter and auto status."""
    turn_label = "Initial state" if step == 0 else f"Turn {step} / {len(SIMULATION) - 1}"
    auto_label = "AUTO ON" if auto_play else "AUTO OFF"
    hud = font.render(f"{turn_label}   [{auto_label}]", True, TEXT_COLOR)
    surface.blit(hud, (10, 8))

    if step == len(SIMULATION) - 1:
        done_font = pygame.font.SysFont("monospace", 50, bold=True)
        done = done_font.render(
            f"All drones arrived in {step} turn(s)!",
            True,
            (60, 255, 120),
        )
        surface.blit(
            done,
            (SCREEN_W // 2 - done.get_width() // 2, BTN_MARGIN_Y + BTN_H + 10),
        )


# ---------------------------------------------------------------------------
# Button
# ---------------------------------------------------------------------------


@dataclass
class Button:
    """Clickable button with hover / pressed states."""

    label:   str
    rect:    pygame.Rect
    hover:   bool = field(default=False, init=False)
    pressed: bool = field(default=False, init=False)

    _C_NORMAL:  tuple[int, int, int] = field(default=(55, 55, 75),   init=False, repr=False)
    _C_HOVER:   tuple[int, int, int] = field(default=(85, 85, 115),  init=False, repr=False)
    _C_PRESSED: tuple[int, int, int] = field(default=(35, 35, 50),   init=False, repr=False)
    _C_ACTIVE:  tuple[int, int, int] = field(default=(40, 110, 65),  init=False, repr=False)

    def update(self, mouse_pos: tuple[int, int], mouse_down: bool) -> None:
        """Refresh hover / pressed flags."""
        self.hover   = self.rect.collidepoint(mouse_pos)
        self.pressed = self.hover and mouse_down

    def was_clicked(self, event: pygame.event.Event) -> bool:
        """True when a left-click release lands on this button."""
        return (
            event.type == pygame.MOUSEBUTTONUP
            and event.button == 1
            and self.rect.collidepoint(event.pos)
        )

    def draw(
        self,
        surface: pygame.Surface,
        font: pygame.font.Font,
        active: bool = False,
    ) -> None:
        """Render the button."""
        if active:
            bg = self._C_ACTIVE
        elif self.pressed:
            bg = self._C_PRESSED
        elif self.hover:
            bg = self._C_HOVER
        else:
            bg = self._C_NORMAL

        pygame.draw.rect(surface, bg, self.rect, border_radius=16)
        pygame.draw.rect(surface, TEXT_COLOR, self.rect, 2, border_radius=16)
        text = font.render(self.label, True, TEXT_COLOR)
        surface.blit(
            text,
            (
                self.rect.centerx - text.get_width() // 2,
                self.rect.centery - text.get_height() // 2,
            ),
        )


def make_buttons(screen_w: int, screen_h: int) -> dict[str, Button]:
    """Build the bottom button bar."""
    labels: list[tuple[str, str]] = [
        ("prev",    "\u25c0  Prev"),
        ("next",    "Next  \u25b6"),
        ("auto",    "\u23ef  Auto"),
        ("restart", "\u21ba  Restart"),
        ("quit",    "\u2715  Quit"),
    ]
    total_w  = len(labels) * BTN_W + (len(labels) - 1) * BTN_GAP
    start_x  = (screen_w - total_w) // 2
    y        = screen_h - BTN_H - BTN_MARGIN_Y
    return {
        key: Button(label=label,
                    rect=pygame.Rect(start_x + i * (BTN_W + BTN_GAP), y, BTN_W, BTN_H))
        for i, (key, label) in enumerate(labels)
    }


def draw_buttons(
    surface: pygame.Surface,
    font: pygame.font.Font,
    buttons: dict[str, Button],
    auto_play: bool,
) -> None:
    """Render the button bar."""
    for key, btn in buttons.items():
        btn.draw(surface, font, active=(key == "auto" and auto_play))


# ---------------------------------------------------------------------------
# Main
# ---------------------------------------------------------------------------


def main() -> None:
    """Run the pygame visualisation for easy_01."""
    pygame.init()
    screen   = pygame.display.set_mode((SCREEN_W, SCREEN_H))
    pygame.display.set_caption("Fly-in \u2014 easy_01 (linear path, 2 drones)")
    font     = pygame.font.SysFont("monospace", 30, bold=True)
    btn_font = pygame.font.SysFont("monospace", 28, bold=True)
    clock    = pygame.time.Clock()

    buttons = make_buttons(SCREEN_W, SCREEN_H)

    step:        int   = 0
    auto_play:   bool  = False
    auto_timer:  int   = 0
    prev_state: dict[str, str] = dict(SIMULATION[0])
    trans_t:    float = 1.0
    trans_timer: int  = 0
    rotor_angle: float = 0.0

    def advance(delta: int) -> None:
        nonlocal step, prev_state, trans_t, trans_timer, auto_play
        new_step = max(0, min(len(SIMULATION) - 1, step + delta))
        if new_step != step:
            prev_state  = dict(SIMULATION[step])
            step        = new_step
            trans_t     = 0.0
            trans_timer = 0
        if delta < 0:
            auto_play = False

    running: bool = True
    while running:
        dt: int    = clock.tick(60)
        t:  float  = pygame.time.get_ticks() / 1000.0
        rotor_angle = (rotor_angle + dt * 0.36) % 360

        mouse_pos  = pygame.mouse.get_pos()
        mouse_down = pygame.mouse.get_pressed()[0]
        for btn in buttons.values():
            btn.update(mouse_pos, mouse_down)

        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                running = False

            elif event.type == pygame.KEYDOWN:
                if event.key == pygame.K_ESCAPE:
                    running = False
                elif event.key == pygame.K_SPACE:
                    advance(1)
                elif event.key == pygame.K_LEFT:
                    advance(-1)
                elif event.key == pygame.K_a:
                    auto_play = not auto_play
                    auto_timer = 0

            elif event.type == pygame.MOUSEBUTTONUP:
                if buttons["prev"].was_clicked(event):
                    advance(-1)
                elif buttons["next"].was_clicked(event):
                    advance(1)
                elif buttons["auto"].was_clicked(event):
                    auto_play = not auto_play
                    auto_timer = 0
                elif buttons["restart"].was_clicked(event):
                    prev_state  = dict(SIMULATION[0])
                    step        = 0
                    trans_t     = 1.0
                    auto_play   = False
                elif buttons["quit"].was_clicked(event):
                    running = False

        # Auto-play (wait for current transition to finish first)
        if auto_play and trans_t >= 1.0:
            auto_timer += dt
            if auto_timer >= AUTO_DELAY:
                auto_timer = 0
                if step < len(SIMULATION) - 1:
                    advance(1)
                else:
                    auto_play = False

        # Advance transition
        if trans_t < 1.0:
            trans_timer += dt
            trans_t = min(1.0, trans_timer / TRANS_DURATION)

        # Draw
        draw_background(screen)
        draw_all_corridors(screen, t * 0.35)
        draw_all_hubs(screen, font, t)
        draw_all_drones(screen, font,
                        SIMULATION[step], prev_state,
                        trans_t, rotor_angle)
        draw_hud(screen, font, step, auto_play)
        draw_buttons(screen, btn_font, buttons, auto_play)
        pygame.display.flip()

    pygame.quit()
    sys.exit()


if __name__ == "__main__":
    main()
