"""
Animation des drones + contrôle de replay (version simplifiée).
"""

import pygame
from enum import Enum
from typing import Dict, List, Tuple


# ───────────────────────────────────────────────
# Constantes
# ───────────────────────────────────────────────

DRONE_RADIUS = 8
ANIM_DURATION = 1.0

DRONE_COLORS = {
    "moving": (150, 255, 100),
    "idle": (150, 150, 255),
}


class ReplayState(Enum):
    STOPPED = 0
    PLAYING = 1
    PAUSED = 2


# ───────────────────────────────────────────────
# Drone animé (interpolation + dessin)
# ───────────────────────────────────────────────

class AnimatedDrone:
    def __init__(self, drone_id: str, hub_positions: Dict[str, Tuple[float, float]], start_hub: str):
        self.id = drone_id
        self.hub_positions = hub_positions
        self.start = start_hub
        self.end = start_hub
        self.pos = hub_positions[start_hub]
        self.t = 0.0
        self.moving = False

    def set_destination(self, hub: str):
        if hub != self.end:
            self.start = self.end
            self.end = hub
            self.t = 0.0
            self.moving = True

    def update(self, dt: float):
        if not self.moving:
            return

        self.t = min(1.0, self.t + dt / ANIM_DURATION)
        sx, sy = self.hub_positions[self.start]
        ex, ey = self.hub_positions[self.end]

        self.pos = (sx + (ex - sx) * self.t, sy + (ey - sy) * self.t)

        if self.t >= 1.0:
            self.moving = False
            self.pos = self.hub_positions[self.end]

    def draw(self, surf, camera, sw, sh, zoom):
        x, y = camera.world_to_screen(self.pos[0], self.pos[1], sw, sh)
        color = DRONE_COLORS["moving"] if self.moving else DRONE_COLORS["idle"]
        r = max(2, int(DRONE_RADIUS * zoom))

        pygame.draw.circle(surf, color, (x, y), r)
        pygame.draw.circle(surf, (255, 255, 255), (x, y), r, 1)


# ───────────────────────────────────────────────
# Contrôleur de replay (play/pause/next/prev)
# ───────────────────────────────────────────────

class ReplayController:
    def __init__(self, total_turns: int, speed: float):
        self.state = ReplayState.STOPPED
        self.turn = 0
        self.total = max(1, total_turns)
        self.speed = speed
        self.timer = 0.0

    def handle_event(self, event):
        if event.type != pygame.KEYDOWN:
            return False

        if event.key == pygame.K_SPACE:
            self.state = ReplayState.PAUSED if self.state == ReplayState.PLAYING else ReplayState.PLAYING
            self.timer = 0.0
            return True

        if event.key == pygame.K_RIGHT:
            self.turn = min(self.turn + 1, self.total - 1)
            self.state = ReplayState.PAUSED
            return True

        if event.key == pygame.K_LEFT:
            self.turn = max(self.turn - 1, 0)
            self.state = ReplayState.PAUSED
            return True

        if event.key == pygame.K_r:
            self.turn = 0
            self.state = ReplayState.PLAYING
            self.timer = 0.0
            return True

        return False

    def update(self, dt):
        if self.state != ReplayState.PLAYING:
            self.timer = 0.0
            return

        self.timer += dt
        if self.timer >= self.speed:
            self.timer = 0.0
            self.turn = (self.turn + 1) % self.total


# ───────────────────────────────────────────────
# Couche d’animation (mise à jour + dessin)
# ───────────────────────────────────────────────

class DroneAnimationLayer:
    def __init__(self, hub_positions: Dict[str, Tuple[float, float]], tours: List[Dict[str, str]], auto_replay_speed=1.0):
        self.hub_positions = hub_positions
        self.tours = tours
        self.drones: Dict[str, AnimatedDrone] = {}
        self.controller = ReplayController(len(tours), auto_replay_speed)
        self.last_turn = -1

        self._init_drones()
        self._apply_turn(0)

    def _init_drones(self):
        if not self.tours:
            return
        for drone_id, hub in self.tours[0].items():
            self.drones[drone_id] = AnimatedDrone(drone_id, self.hub_positions, hub)

    def _apply_turn(self, idx: int):
        if idx == self.last_turn or idx < 0 or idx >= len(self.tours):
            return

        for drone_id, hub in self.tours[idx].items():
            if drone_id not in self.drones:
                prev = self.tours[idx - 1].get(drone_id, hub) if idx > 0 else hub
                self.drones[drone_id] = AnimatedDrone(drone_id, self.hub_positions, prev)

            self.drones[drone_id].set_destination(hub)

        self.last_turn = idx

    def update(self, dt: float):
        self.controller.update(dt)
        self._apply_turn(self.controller.turn)

        for d in self.drones.values():
            d.update(dt)

    def handle_event(self, event):
        return self.controller.handle_event(event)

    def draw(self, surf, camera, sw, sh, zoom):
        for d in self.drones.values():
            d.draw(surf, camera, sw, sh, zoom)

    def draw_overlay(self, surf, font, sw, sh):
        turn = self.controller.turn + 1
        total = self.controller.total
        state = "PLAYING" if self.controller.state == ReplayState.PLAYING else "PAUSED"

        info = font.render(f"Turn {turn}/{total} [{state}]", True, (255, 255, 255))
        surf.blit(info, (10, 10))

        controls = font.render("SPACE Play/Pause | ← Prev | → Next | R Restart", True, (180, 180, 180))
        surf.blit(controls, (10, 35))
