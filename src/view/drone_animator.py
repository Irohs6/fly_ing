"""
Module d'animation des drones sur un graphe Pygame.

Ce module gère:
- L'animation des drones qui se déplacent entre les hubs avec interpolation
- Le contrôle de replay (play/pause, next/previous turn, restart, auto-replay)
- Le rendu des drones sur la surface pygame
"""

from enum import Enum
from typing import Dict, List, Optional, Tuple

try:
    import pygame
except ImportError:
    print("Pygame is not installed. Please install pygame to use drone_animator.")
    exit(1)


# ── Constants ─────────────────────────────────────────────────────────────────


DRONE_RADIUS: int = 8
ANIMATION_DURATION: float = 1.0  # seconds to animate one turn transition

# Couleurs pour les drones
DRONE_COLORS: Dict[str, Tuple[int, int, int]] = {
    "default": (100, 200, 255),  # Bleu ciel
    "moving": (150, 255, 100),   # Vert clair
    "idle": (150, 150, 255),     # Bleu pâle
}


class ReplayState(Enum):
    """État du contrôle de replay."""
    STOPPED = 0
    PLAYING = 1
    PAUSED = 2


# ── AnimatedDrone ────────────────────────────────────────────────────────────


class AnimatedDrone:
    """
    Représente un drone avec position interpolée pour l'animation.

    Attributes:
        drone_id: Identifiant unique du drone
        hub_positions: Dict{hub_name: (x, y)} pour la localisation spatiale
        start_hub: Hub de départ au tour courant
        end_hub: Hub de destination au tour courant
        position: Position interpolée (x, y) sur l'écran
        is_moving: True si le drone est en transition entre deux hubs
        animation_time: Temps écoulé depuis le début de l'animation [0, 1]
    """

    def __init__(
        self,
        drone_id: str,
        hub_positions: Dict[str, Tuple[float, float]],
        start_hub: str,
    ) -> None:
        self.drone_id = drone_id
        self.hub_positions = hub_positions
        self.start_hub = start_hub
        self.end_hub = start_hub
        self.position: Tuple[float, float] = hub_positions.get(start_hub, (0, 0))
        self.is_moving = False
        self.animation_time = 0.0

    def set_destination(self, hub_name: str) -> None:
        """Définit le hub de destination. Démarre l'animation si hub change."""
        if hub_name != self.end_hub:
            self.start_hub = self.end_hub
            self.end_hub = hub_name
            self.animation_time = 0.0
            self.is_moving = True
        else:
            self.is_moving = False
            self.animation_time = 0.0

    def update(self, dt: float) -> None:
        """
        Met à jour la position du drone avec interpolation.

        Args:
            dt: Temps écoulé depuis le dernier frame en secondes
        """
        if not self.is_moving:
            return

        self.animation_time = min(
            1.0, self.animation_time + dt / ANIMATION_DURATION
        )

        start_pos = self.hub_positions.get(self.start_hub, (0, 0))
        end_pos = self.hub_positions.get(self.end_hub, (0, 0))

        # Interpolation linéaire
        t = self.animation_time
        self.position = (
            start_pos[0] + (end_pos[0] - start_pos[0]) * t,
            start_pos[1] + (end_pos[1] - start_pos[1]) * t,
        )

        # Animation terminée
        if self.animation_time >= 1.0:
            self.is_moving = False
            self.position = end_pos

    def draw(
        self,
        surface: pygame.Surface,
        camera,
        screen_width: int,
        screen_height: int,
        zoom: float = 1.0,
    ) -> None:
        """
        Dessine le drone sur la surface pygame.
        
        Args:
            surface: Surface pygame où dessiner
            camera: Objet Camera pour la transformation de coordonnées
            screen_width: Largeur de l'écran
            screen_height: Hauteur de l'écran
            zoom: Facteur de zoom (par défaut 1.0)
        """
        # Convertir les coordonnées monde en coordonnées écran
        screen_x, screen_y = camera.to_screen(
            self.position[0],
            self.position[1],
            screen_width,
            screen_height,
        )

        # Choisir la couleur selon l'état
        color = DRONE_COLORS["moving"] if self.is_moving else DRONE_COLORS["idle"]
        radius = max(2, int(DRONE_RADIUS * zoom))

        # Dessiner le drone
        pygame.draw.circle(surface, color, (screen_x, screen_y), radius)

        # Bordure
        pygame.draw.circle(surface, (255, 255, 255), (screen_x, screen_y), radius, 1)

# ── ReplayController ─────────────────────────────────────────────────────────


class ReplayController:
    """
    Contrôle la lecture d'un historique de tours.
    
    Gère:
    - Play/Pause (SPACE)
    - Next turn (RIGHT)
    - Previous turn (LEFT)
    - Restart (R)
    - Auto-replay (avance automatiquement)
    
    Attributes:
        state: État actuel du replay (STOPPED, PLAYING, PAUSED)
        current_turn: Tour courant [0, NB_TURNS-1]
        total_turns: Nombre total de tours
        auto_replay_speed: Secondes entre chaque avance auto
        auto_replay_timer: Timer pour l'auto-replay
    """

    def __init__(self, total_turns: int, auto_replay_speed: float = 1.0) -> None:
        self.state = ReplayState.STOPPED
        self.current_turn = 0
        self.total_turns = max(1, total_turns)
        self.auto_replay_speed = auto_replay_speed
        self.auto_replay_timer = 0.0

    def handle_event(self, event) -> bool:
        """
        Traite les événements de clavier.
        
        Returns:
            True si un événement a été traité
        """
        if event.type != pygame.KEYDOWN:
            return False

        if event.key == pygame.K_SPACE:
            self.toggle_play_pause()
            return True
        elif event.key == pygame.K_RIGHT:
            self.next_turn()
            return True
        elif event.key == pygame.K_LEFT:
            self.previous_turn()
            return True
        elif event.key == pygame.K_r:
            self.restart()
            return True

        return False

    def toggle_play_pause(self) -> None:
        """Bascule entre PLAYING et PAUSED."""
        if self.state == ReplayState.PLAYING:
            self.state = ReplayState.PAUSED
        else:
            self.state = ReplayState.PLAYING
            self.auto_replay_timer = 0.0

    def next_turn(self) -> None:
        """Avance d'un tour."""
        self.current_turn = min(self.current_turn + 1, self.total_turns - 1)
        self.state = ReplayState.PAUSED
        self.auto_replay_timer = 0.0

    def previous_turn(self) -> None:
        """Recule d'un tour."""
        self.current_turn = max(self.current_turn - 1, 0)
        self.state = ReplayState.PAUSED
        self.auto_replay_timer = 0.0

    def restart(self) -> None:
        """Redémarre du tour 0."""
        self.current_turn = 0
        self.state = ReplayState.PLAYING
        self.auto_replay_timer = 0.0

    def update(self, dt: float) -> None:
        """
        Met à jour le timer d'auto-replay.
        
        Args:
            dt: Temps écoulé depuis le dernier frame
        """
        if self.state != ReplayState.PLAYING:
            self.auto_replay_timer = 0.0
            return

        self.auto_replay_timer += dt
        if self.auto_replay_timer >= self.auto_replay_speed:
            self.auto_replay_timer = 0.0
            if self.current_turn < self.total_turns - 1:
                self.current_turn += 1
            else:
                # Fin du replay: recommencer
                self.current_turn = 0

    def is_playing(self) -> bool:
        """Retourne True si le replay est en cours."""
        return self.state == ReplayState.PLAYING

    def is_paused(self) -> bool:
        """Retourne True si le replay est en pause."""
        return self.state == ReplayState.PAUSED

    def is_stopped(self) -> bool:
        """Retourne True si le replay est arrêté."""
        return self.state == ReplayState.STOPPED


# ── DroneAnimationLayer ──────────────────────────────────────────────────────


class DroneAnimationLayer:
    """
    Couche d'animation gérant l'ensemble des drones et leur rendu.
    Gère:
    - Création et suppression des drones
    - Mise à jour des positions selon l'historique des tours
    - Rendu de tous les drones
    - Contrôle de replay
    Attributes:
        drones: Dict de drones animés {drone_id: AnimatedDrone}
        hub_positions: Dict{hub_name: (x, y)} des positions des hubs
        tours: Liste des tours [ {drone_id: hub_name}, ... ]
        replay_controller: Contrôleur de replay
        last_tour_applied: Dernier tour appliqué aux drones
    """

    def __init__(
        self,
        hub_positions: Dict[str, Tuple[float, float]],
        tours: List[Dict[str, str]],
        auto_replay_speed: float = 1.0,
    ) -> None:
        """
        Initialise la couche d'animation.

        Args:
            hub_positions: Dict{hub_name: (x, y)} positions spatiales des hubs
            tours: Liste des tours [ {drone_id: hub_name}, ... ]
            auto_replay_speed: Temps en secondes avant d'avancer au tour suivant
        """
        self.hub_positions = hub_positions
        self.tours = tours
        self.drones: Dict[str, AnimatedDrone] = {}
        self.replay_controller = ReplayController(
            len(tours), auto_replay_speed
        )
        self.last_tour_applied = -1

        # Initialiser les drones depuis le premier tour
        self._initialize_drones()
        self._apply_turn(0)

    def _initialize_drones(self) -> None:
        """Crée les drones basés sur le premier tour."""
        if not self.tours:
            return

        first_turn = self.tours[0]
        for drone_id in first_turn.keys():
            hub_name = first_turn[drone_id]
            self.drones[drone_id] = AnimatedDrone(
                drone_id, self.hub_positions, hub_name
            )

    def _apply_turn(self, turn_index: int) -> None:
        """
        Applique un tour à tous les drones.

        Déplace les drones et lance les animations si nécessaire.

        Args:
            turn_index: Index du tour [0, len(tours)-1]
        """
        if turn_index < 0 or turn_index >= len(self.tours):
            return

        if turn_index == self.last_tour_applied:
            return

        turn_data = self.tours[turn_index]

        for drone_id, hub_name in turn_data.items():
            if drone_id not in self.drones:
                # Créer le drone s'il n'existe pas
                if self.last_tour_applied >= 0 and turn_index > 0:
                    prev_hub = self.tours[turn_index - 1].get(drone_id, hub_name)
                else:
                    prev_hub = hub_name
                self.drones[drone_id] = AnimatedDrone(
                    drone_id, self.hub_positions, prev_hub
                )

            # Appliquer la destination
            self.drones[drone_id].set_destination(hub_name)

        self.last_tour_applied = turn_index

    def update(self, dt: float) -> None:
        """
        Met à jour l'état de l'animation et l'historique.

        Args:
            dt: Temps écoulé depuis le dernier frame en secondes
        """
        # Mettre à jour le contrôleur de replay
        self.replay_controller.update(dt)

        # Appliquer le tour courant
        current_turn = self.replay_controller.current_turn
        self._apply_turn(current_turn)

        # Mettre à jour toutes les positions des drones
        for drone in self.drones.values():
            drone.update(dt)

    def handle_event(self, event) -> bool:
        """
        Traite les événements (clavier) pour le contrôle de replay.
        
        Returns:
            True si un événement a été traité
        """
        return self.replay_controller.handle_event(event)

    def draw(
        self,
        surface: pygame.Surface,
        camera,
        screen_width: int,
        screen_height: int,
        zoom: float = 1.0,
    ) -> None:
        """
        Dessine tous les drones.
        
        Args:
            surface: Surface pygame où dessiner
            camera: Objet Camera pour les transformations de coordonnées
            screen_width: Largeur de l'écran
            screen_height: Hauteur de l'écran
            zoom: Facteur de zoom (par défaut 1.0)
        """
        for drone in self.drones.values():
            drone.draw(surface, camera, screen_width, screen_height, zoom)

    def draw_overlay(
        self,
        surface: pygame.Surface,
        font: pygame.font.Font,
        screen_width: int,
        screen_height: int,
    ) -> None:
        """
        Dessine l'overlay d'information du replay.
        
        Affiche le tour courant, l'état (play/pause), les contrôles.
        
        Args:
            surface: Surface pygame où dessiner
            font: Police pygame pour le texte
            screen_width: Largeur de l'écran
            screen_height: Hauteur de l'écran
        """
        controller = self.replay_controller

        # État du replay
        state_str = "PLAYING" if controller.is_playing() else "PAUSED"
        turn_str = f"Turn {controller.current_turn + 1}/{controller.total_turns}"
        
        info = f"{turn_str} [{state_str}]"
        text_surface = font.render(info, True, (255, 255, 255))
        surface.blit(text_surface, (10, 10))

        # Contrôles
        controls = "SPACE:Play/Pause | RIGHT:Next | LEFT:Prev | R:Restart"
        controls_surface = font.render(controls, True, (180, 180, 180))
        surface.blit(controls_surface, (10, 35))

    def get_current_turn(self) -> int:
        """Retourne l'index du tour courant."""
        return self.replay_controller.current_turn

    def get_total_turns(self) -> int:
        """Retourne le nombre total de tours."""
        return self.replay_controller.total_turns

    def get_drone_at_turn(self, drone_id: str, turn_index: int) -> Optional[str]:
        """
        Retourne le hub où se trouve un drone à un tour donné.
        
        Args:
            drone_id: Identifiant du drone
            turn_index: Index du tour
            
        Returns:
            Nom du hub ou None
        """
        if turn_index < 0 or turn_index >= len(self.tours):
            return None
        return self.tours[turn_index].get(drone_id)

    def set_auto_replay_speed(self, speed: float) -> None:
        """Définit la vitesse d'auto-replay en secondes."""
        self.replay_controller.auto_replay_speed = max(0.1, speed)

    def get_stats(self) -> Dict[str, int]:
        """Retourne des statistiques sur l'animation."""
        return {
            "nb_drones": len(self.drones),
            "total_turns": self.replay_controller.total_turns,
            "current_turn": self.replay_controller.current_turn,
            "nb_moving": sum(1 for d in self.drones.values() if d.is_moving),
        }
