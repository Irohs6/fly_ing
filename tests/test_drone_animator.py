"""Tests for drone animation logic (src/view/drone_animator.py).

Only the pure-logic classes are tested here (no Pygame display required).
Classes that call pygame.draw.* are excluded from unit tests.
"""

from src.view.drone_animator import (
    AnimatedDrone,
    ReplayController,
    ReplayState,
    DroneAnimationLayer,
)

# ---------------------------------------------------------------------------
# Fixtures
# ---------------------------------------------------------------------------

HUB_POSITIONS = {
    "hub_a": (0.0, 0.0),
    "hub_b": (100.0, 0.0),
    "hub_c": (200.0, 0.0),
}

TOURS = [
    {"D1": "hub_a", "D2": "hub_a"},
    {"D1": "hub_b", "D2": "hub_a"},
    {"D1": "hub_c", "D2": "hub_b"},
    {"D1": "hub_c", "D2": "hub_c"},
]


# ---------------------------------------------------------------------------
# AnimatedDrone
# ---------------------------------------------------------------------------


class TestAnimatedDrone:
    def test_initial_position_is_start_hub(self) -> None:
        d = AnimatedDrone("D1", HUB_POSITIONS, "hub_a")
        assert d.pos == HUB_POSITIONS["hub_a"]
        assert d.moving is False

    def test_set_destination_triggers_movement(self) -> None:
        d = AnimatedDrone("D1", HUB_POSITIONS, "hub_a")
        d.set_destination("hub_b")
        assert d.moving is True
        assert d.end == "hub_b"
        assert d.start == "hub_a"

    def test_set_same_destination_does_not_move(self) -> None:
        d = AnimatedDrone("D1", HUB_POSITIONS, "hub_a")
        d.set_destination("hub_a")
        assert d.moving is False

    def test_update_advances_interpolation(self) -> None:
        d = AnimatedDrone("D1", HUB_POSITIONS, "hub_a")
        d.set_destination("hub_b")
        d.update(0.5)  # half of ANIM_DURATION (1.0)
        # Should be halfway between hub_a (0,0) and hub_b (100,0)
        assert 40.0 < d.pos[0] < 60.0

    def test_update_completes_at_destination(self) -> None:
        d = AnimatedDrone("D1", HUB_POSITIONS, "hub_a")
        d.set_destination("hub_b")
        d.update(2.0)  # more than ANIM_DURATION
        assert d.moving is False
        assert d.pos == HUB_POSITIONS["hub_b"]

    def test_chained_destinations(self) -> None:
        d = AnimatedDrone("D1", HUB_POSITIONS, "hub_a")
        d.set_destination("hub_b")
        d.update(2.0)
        d.set_destination("hub_c")
        assert d.moving is True
        assert d.start == "hub_b"
        assert d.end == "hub_c"

    def test_no_movement_when_not_moving(self) -> None:
        d = AnimatedDrone("D1", HUB_POSITIONS, "hub_a")
        initial_pos = d.pos
        d.update(1.0)
        assert d.pos == initial_pos


# ---------------------------------------------------------------------------
# ReplayController
# ---------------------------------------------------------------------------


class TestReplayController:
    def test_initial_state_is_stopped(self) -> None:
        rc = ReplayController(total_turns=5, speed=1.0)
        assert rc.state == ReplayState.STOPPED
        assert rc.turn == 0

    def test_space_starts_playback(self) -> None:
        import pygame

        pygame.init()
        rc = ReplayController(total_turns=5, speed=1.0)
        event = pygame.event.Event(pygame.KEYDOWN, key=pygame.K_SPACE)
        rc.handle_event(event)
        assert rc.state == ReplayState.PLAYING
        pygame.quit()

    def test_space_toggles_pause(self) -> None:
        import pygame

        pygame.init()
        rc = ReplayController(total_turns=5, speed=1.0)
        event = pygame.event.Event(pygame.KEYDOWN, key=pygame.K_SPACE)
        rc.handle_event(event)  # play
        rc.handle_event(event)  # pause
        assert rc.state == ReplayState.PAUSED
        pygame.quit()

    def test_right_arrow_advances_turn(self) -> None:
        import pygame

        pygame.init()
        rc = ReplayController(total_turns=5, speed=1.0)
        event = pygame.event.Event(pygame.KEYDOWN, key=pygame.K_RIGHT)
        rc.handle_event(event)
        assert rc.turn == 1
        assert rc.state == ReplayState.PAUSED
        pygame.quit()

    def test_left_arrow_does_not_go_below_zero(self) -> None:
        import pygame

        pygame.init()
        rc = ReplayController(total_turns=5, speed=1.0)
        event = pygame.event.Event(pygame.KEYDOWN, key=pygame.K_LEFT)
        rc.handle_event(event)
        assert rc.turn == 0
        pygame.quit()

    def test_right_arrow_does_not_exceed_total(self) -> None:
        import pygame

        pygame.init()
        rc = ReplayController(total_turns=3, speed=1.0)
        event = pygame.event.Event(pygame.KEYDOWN, key=pygame.K_RIGHT)
        for _ in range(10):
            rc.handle_event(event)
        assert rc.turn == rc.total - 1
        pygame.quit()

    def test_r_key_restarts(self) -> None:
        import pygame

        pygame.init()
        rc = ReplayController(total_turns=5, speed=1.0)
        rc.turn = 3
        event = pygame.event.Event(pygame.KEYDOWN, key=pygame.K_r)
        rc.handle_event(event)
        assert rc.turn == 0
        assert rc.state == ReplayState.PLAYING
        pygame.quit()

    def test_update_advances_turn_while_playing(self) -> None:
        rc = ReplayController(total_turns=5, speed=0.5)
        rc.state = ReplayState.PLAYING
        rc.update(0.6)  # > speed (0.5) → should advance
        assert rc.turn == 1

    def test_update_does_not_advance_when_paused(self) -> None:
        rc = ReplayController(total_turns=5, speed=0.5)
        rc.state = ReplayState.PAUSED
        rc.update(2.0)
        assert rc.turn == 0

    def test_non_keydown_event_ignored(self) -> None:
        import pygame

        pygame.init()
        rc = ReplayController(total_turns=5, speed=1.0)
        event = pygame.event.Event(pygame.MOUSEMOTION)
        result = rc.handle_event(event)
        assert result is False
        pygame.quit()


# ---------------------------------------------------------------------------
# DroneAnimationLayer
# ---------------------------------------------------------------------------


class TestDroneAnimationLayer:
    def test_drones_initialized_from_first_tour(self) -> None:
        layer = DroneAnimationLayer(
            HUB_POSITIONS, TOURS, auto_replay_speed=1.0
        )
        assert "D1" in layer.drones
        assert "D2" in layer.drones

    def test_initial_drone_position_correct(self) -> None:
        layer = DroneAnimationLayer(
            HUB_POSITIONS, TOURS, auto_replay_speed=1.0
        )
        assert layer.drones["D1"].end == "hub_a"
        assert layer.drones["D2"].end == "hub_a"

    def test_apply_turn_updates_destinations(self) -> None:
        layer = DroneAnimationLayer(
            HUB_POSITIONS, TOURS, auto_replay_speed=1.0
        )
        layer._apply_turn(1)
        assert layer.drones["D1"].end == "hub_b"
        assert layer.drones["D2"].end == "hub_a"

    def test_apply_turn_out_of_bounds_is_safe(self) -> None:
        layer = DroneAnimationLayer(
            HUB_POSITIONS, TOURS, auto_replay_speed=1.0
        )
        # Should not raise
        layer._apply_turn(-1)
        layer._apply_turn(999)

    def test_total_tours_set_correctly(self) -> None:
        layer = DroneAnimationLayer(
            HUB_POSITIONS, TOURS, auto_replay_speed=1.0
        )
        assert layer.controller.total == len(TOURS)

    def test_update_advances_animation(self) -> None:
        layer = DroneAnimationLayer(
            HUB_POSITIONS, TOURS, auto_replay_speed=0.1
        )
        layer.controller.state = ReplayState.PLAYING
        layer.update(0.2)  # enough to advance one turn at speed=0.1
        # Turn counter should have moved
        assert layer.controller.turn >= 1

    def test_empty_tours_does_not_crash(self) -> None:
        layer = DroneAnimationLayer(HUB_POSITIONS, [], auto_replay_speed=1.0)
        assert layer.drones == {}

    def test_new_drone_in_later_tour_added(self) -> None:
        tours = [
            {"D1": "hub_a"},
            {"D1": "hub_b", "D2": "hub_a"},  # D2 appears at turn 1
        ]
        layer = DroneAnimationLayer(
            HUB_POSITIONS, tours, auto_replay_speed=1.0
        )
        layer._apply_turn(1)
        assert "D2" in layer.drones
