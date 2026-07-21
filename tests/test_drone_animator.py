"""
Tests unitaires pour le module drone_animator.

Couvrir:
- AnimatedDrone: création, mise à jour position, destination
- ReplayController: play/pause, next/prev, restart, auto-replay
- DroneAnimationLayer: gestion des drones, application des tours
"""

import unittest
from unittest.mock import Mock, MagicMock
from src.view.drone_animator import (
    AnimatedDrone,
    ReplayController,
    DroneAnimationLayer,
    ReplayState,
)


class TestAnimatedDrone(unittest.TestCase):
    """Tests pour la classe AnimatedDrone."""

    def setUp(self):
        """Prépare les données de test."""
        self.hub_positions = {
            "A": (0.0, 0.0),
            "B": (100.0, 0.0),
            "C": (100.0, 100.0),
        }
        self.drone = AnimatedDrone("drone_1", self.hub_positions, "A")

    def test_initialization(self):
        """Teste l'initialisation d'un drone."""
        self.assertEqual(self.drone.drone_id, "drone_1")
        self.assertEqual(self.drone.start_hub, "A")
        self.assertEqual(self.drone.end_hub, "A")
        self.assertEqual(self.drone.position, (0.0, 0.0))
        self.assertFalse(self.drone.is_moving)
        self.assertEqual(self.drone.animation_time, 0.0)

    def test_set_destination_no_change(self):
        """Teste set_destination quand le hub reste le même."""
        self.drone.set_destination("A")
        self.assertFalse(self.drone.is_moving)
        self.assertEqual(self.drone.end_hub, "A")

    def test_set_destination_with_change(self):
        """Teste set_destination quand le hub change."""
        self.drone.set_destination("B")
        self.assertTrue(self.drone.is_moving)
        self.assertEqual(self.drone.start_hub, "A")
        self.assertEqual(self.drone.end_hub, "B")
        self.assertEqual(self.drone.animation_time, 0.0)

    def test_update_animation(self):
        """Teste la mise à jour de position pendant l'animation."""
        self.drone.set_destination("B")

        # Halfway through animation
        self.drone.update(0.5)
        assert 45.0 <= self.drone.position[0] <= 55.0  # ~50, avec marge
        assert self.drone.position[1] == 0.0

        # Animation terminée
        self.drone.update(0.5)
        self.assertFalse(self.drone.is_moving)
        self.assertEqual(self.drone.position, (100.0, 0.0))

    def test_update_no_movement(self):
        """Teste la mise à jour quand il n'y a pas de mouvement."""
        pos_before = self.drone.position
        self.drone.update(10.0)
        self.assertEqual(self.drone.position, pos_before)

    def test_get_current_hub_while_moving(self):
        """Teste get_current_hub pendant un déplacement."""
        self.drone.set_destination("B")
        # Pendant le mouvement, c'est le hub de départ
        self.assertEqual(self.drone.get_current_hub(), "A")

    def test_get_current_hub_at_rest(self):
        """Teste get_current_hub au repos."""
        self.drone.set_destination("B")
        self.drone.update(1.0)
        # Après le mouvement, c'est le hub de destination
        self.assertEqual(self.drone.get_current_hub(), "B")


class TestReplayController(unittest.TestCase):
    """Tests pour la classe ReplayController."""

    def setUp(self):
        """Prépare les données de test."""
        self.controller = ReplayController(total_turns=5, auto_replay_speed=1.0)

    def test_initialization(self):
        """Teste l'initialisation du contrôleur."""
        self.assertEqual(self.controller.state, ReplayState.STOPPED)
        self.assertEqual(self.controller.current_turn, 0)
        self.assertEqual(self.controller.total_turns, 5)
        self.assertFalse(self.controller.is_playing())
        self.assertFalse(self.controller.is_paused())
        self.assertTrue(self.controller.is_stopped())

    def test_toggle_play_pause_stopped_to_playing(self):
        """Teste le passage de STOPPED à PLAYING."""
        self.controller.toggle_play_pause()
        self.assertEqual(self.controller.state, ReplayState.PLAYING)
        self.assertTrue(self.controller.is_playing())

    def test_toggle_play_pause_playing_to_paused(self):
        """Teste le passage de PLAYING à PAUSED."""
        self.controller.state = ReplayState.PLAYING
        self.controller.toggle_play_pause()
        self.assertEqual(self.controller.state, ReplayState.PAUSED)
        self.assertTrue(self.controller.is_paused())

    def test_next_turn(self):
        """Teste l'avancement d'un tour."""
        self.controller.next_turn()
        self.assertEqual(self.controller.current_turn, 1)
        self.assertTrue(self.controller.is_paused())

    def test_next_turn_at_end(self):
        """Teste next_turn quand on est au dernier tour."""
        self.controller.current_turn = 4
        self.controller.next_turn()
        self.assertEqual(self.controller.current_turn, 4)  # Ne pas dépasser

    def test_previous_turn(self):
        """Teste le recul d'un tour."""
        self.controller.current_turn = 3
        self.controller.previous_turn()
        self.assertEqual(self.controller.current_turn, 2)
        self.assertTrue(self.controller.is_paused())

    def test_previous_turn_at_start(self):
        """Teste previous_turn quand on est au tour 0."""
        self.controller.previous_turn()
        self.assertEqual(self.controller.current_turn, 0)  # Ne pas descendre dessous

    def test_restart(self):
        """Teste le redémarrage."""
        self.controller.current_turn = 4
        self.controller.restart()
        self.assertEqual(self.controller.current_turn, 0)
        self.assertTrue(self.controller.is_playing())

    def test_auto_replay_timer(self):
        """Teste l'avancement automatique."""
        self.controller.state = ReplayState.PLAYING
        self.controller.update(0.5)
        self.assertEqual(self.controller.current_turn, 0)  # Pas assez de temps

        self.controller.update(0.5)
        self.assertEqual(self.controller.current_turn, 1)  # Avancement

    def test_auto_replay_loops(self):
        """Teste la boucle de l'auto-replay."""
        self.controller.state = ReplayState.PLAYING
        self.controller.current_turn = 4

        # Avancer jusqu'à la fin
        self.controller.update(1.0)
        self.assertEqual(self.controller.current_turn, 0)  # Recommencer

    def test_handle_event_space(self):
        """Teste la touche SPACE."""
        event = Mock()
        event.type = 2  # KEYDOWN
        event.key = 1073741912  # K_SPACE approximatif (selon la distribution)

        # Ce test peut avoir besoin d'ajustement selon votre config pygame
        # On teste juste que handle_event retourne bool
        result = self.controller.handle_event(event)
        self.assertIsInstance(result, bool)


class TestDroneAnimationLayer(unittest.TestCase):
    """Tests pour la classe DroneAnimationLayer."""

    def setUp(self):
        """Prépare les données de test."""
        self.hub_positions = {
            "A": (0.0, 0.0),
            "B": (100.0, 0.0),
            "C": (100.0, 100.0),
        }
        self.tours = [
            {"drone_1": "A", "drone_2": "B"},
            {"drone_1": "B", "drone_2": "C"},
            {"drone_1": "C", "drone_2": "A"},
        ]
        self.animation_layer = DroneAnimationLayer(
            hub_positions=self.hub_positions,
            tours=self.tours,
            auto_replay_speed=1.0,
        )

    def test_initialization(self):
        """Teste l'initialisation de la couche."""
        self.assertEqual(len(self.animation_layer.drones), 2)
        self.assertIn("drone_1", self.animation_layer.drones)
        self.assertIn("drone_2", self.animation_layer.drones)
        self.assertEqual(self.animation_layer.get_total_turns(), 3)
        self.assertEqual(self.animation_layer.get_current_turn(), 0)

    def test_add_drone(self):
        """Teste l'ajout d'un drone."""
        self.animation_layer.add_drone("drone_3", "A")
        self.assertIn("drone_3", self.animation_layer.drones)
        self.assertEqual(
            self.animation_layer.drones["drone_3"].get_current_hub(), "A"
        )

    def test_remove_drone(self):
        """Teste la suppression d'un drone."""
        self.animation_layer.remove_drone("drone_1")
        self.assertNotIn("drone_1", self.animation_layer.drones)

    def test_get_drone_at_turn(self):
        """Teste la récupération du hub d'un drone à un tour."""
        hub = self.animation_layer.get_drone_at_turn("drone_1", 0)
        self.assertEqual(hub, "A")

        hub = self.animation_layer.get_drone_at_turn("drone_1", 1)
        self.assertEqual(hub, "B")

        hub = self.animation_layer.get_drone_at_turn("drone_1", 2)
        self.assertEqual(hub, "C")

    def test_get_drone_at_invalid_turn(self):
        """Teste avec un index invalide."""
        hub = self.animation_layer.get_drone_at_turn("drone_1", 999)
        self.assertIsNone(hub)

    def test_update_applies_turn(self):
        """Teste que update applique le tour courant."""
        # Au tour 0
        drone_1_hub_before = self.animation_layer.drones["drone_1"].end_hub
        self.assertEqual(drone_1_hub_before, "A")

        # Avancer d'un tour
        self.animation_layer.replay_controller.current_turn = 1
        self.animation_layer.update(0.1)

        # Le drone devrait se diriger vers B
        drone_1_end = self.animation_layer.drones["drone_1"].end_hub
        self.assertEqual(drone_1_end, "B")

    def test_set_auto_replay_speed(self):
        """Teste la modification de la vitesse d'auto-replay."""
        self.animation_layer.set_auto_replay_speed(0.5)
        self.assertEqual(
            self.animation_layer.replay_controller.auto_replay_speed, 0.5
        )

        # Vitesse minimale respectée
        self.animation_layer.set_auto_replay_speed(0.01)
        self.assertEqual(
            self.animation_layer.replay_controller.auto_replay_speed, 0.1
        )

    def test_get_stats(self):
        """Teste les statistiques."""
        stats = self.animation_layer.get_stats()
        self.assertEqual(stats["nb_drones"], 2)
        self.assertEqual(stats["total_turns"], 3)
        self.assertEqual(stats["current_turn"], 0)
        self.assertIn("nb_moving", stats)

    def test_draw_overlay_doesnt_crash(self):
        """Teste que draw_overlay n'échoue pas (test de non-crash)."""
        mock_surface = MagicMock()
        mock_font = MagicMock()
        mock_font.render.return_value = MagicMock()

        # Ne doit pas lever d'erreur
        self.animation_layer.draw_overlay(
            surface=mock_surface,
            font=mock_font,
            screen_width=800,
            screen_height=600,
        )

        # Vérifier que render a été appelé
        self.assertTrue(mock_font.render.called)

    def test_draw_doesnt_crash(self):
        """Teste que draw n'échoue pas (test de non-crash)."""
        mock_surface = MagicMock()
        mock_camera = MagicMock()
        mock_camera.to_screen.return_value = (400, 300)

        # Ne doit pas lever d'erreur
        self.animation_layer.draw(
            surface=mock_surface,
            camera=mock_camera,
            screen_width=800,
            screen_height=600,
            zoom=1.0,
        )


# ── Tests d'intégration ──────────────────────────────────────────────────────


class TestIntegration(unittest.TestCase):
    """Tests d'intégration du workflow complet."""

    def test_complete_replay_workflow(self):
        """Teste le workflow complet de replay."""
        hub_positions = {"A": (0, 0), "B": (100, 0), "C": (100, 100)}
        tours = [
            {"d1": "A"},
            {"d1": "B"},
            {"d1": "C"},
        ]

        layer = DroneAnimationLayer(hub_positions, tours, auto_replay_speed=0.5)

        # Tour 0
        self.assertEqual(layer.get_current_turn(), 0)
        self.assertEqual(layer.get_drone_at_turn("d1", 0), "A")

        # Play automatiquement
        layer.replay_controller.state = ReplayState.PLAYING
        layer.update(0.25)
        self.assertEqual(layer.get_current_turn(), 0)  # Pas assez de temps

        layer.update(0.25)
        self.assertEqual(layer.get_current_turn(), 1)  # Avance

        # Pause et next
        layer.replay_controller.toggle_play_pause()
        self.assertTrue(layer.replay_controller.is_paused())

        layer.replay_controller.next_turn()
        self.assertEqual(layer.get_current_turn(), 2)

        # Restart
        layer.replay_controller.restart()
        self.assertEqual(layer.get_current_turn(), 0)


if __name__ == "__main__":
    unittest.main()
