"""Tests for CollisionManager"""
import unittest
from unittest.mock import MagicMock, PropertyMock

import pygame

from PyPong.core.collision_manager import CollisionManager
from PyPong.core.entities import Ball, Paddle, PowerUp


class TestCollisionManager(unittest.TestCase):
    """Test collision manager functionality"""

    def setUp(self) -> None:
        """Set up test fixtures"""
        pygame.init()
        self.collision_manager = CollisionManager()
        self.paddle1 = Paddle(1, is_ai=False)
        self.paddle2 = Paddle(2, is_ai=True)
        self.ball = Ball()

    def tearDown(self) -> None:
        """Clean up"""
        pygame.quit()

    def test_check_paddle_collision_no_collision(self) -> None:
        """Test when ball and paddle don't collide"""
        # Place ball far from paddle
        self.ball.rect.center = (500, 300)
        self.paddle1.rect.center = (50, 360)

        result = self.collision_manager.check_paddle_collision(self.ball, self.paddle1)
        self.assertFalse(result)

    def test_check_paddle_collision_wrong_direction(self) -> None:
        """Test when ball is moving away from paddle"""
        # Place ball near paddle1 but moving right (away)
        self.ball.rect.center = (100, 360)
        self.ball.velocity_x = 5  # Moving right
        self.paddle1.rect.center = (50, 360)

        result = self.collision_manager.check_paddle_collision(self.ball, self.paddle1)
        self.assertFalse(result)

    def test_check_paddle_collision_valid(self) -> None:
        """Test valid collision"""
        # Place ball colliding with paddle1 and moving left
        self.ball.rect.center = (55, 360)
        self.ball.velocity_x = -5  # Moving left
        self.paddle1.rect.center = (50, 360)

        result = self.collision_manager.check_paddle_collision(self.ball, self.paddle1)
        self.assertTrue(result)

    def test_handle_paddle_collision_returns_correct_values(self) -> None:
        """Test handle_paddle_collision returns correct values"""
        original_vx = self.ball.velocity_x
        result = self.collision_manager.handle_paddle_collision(self.ball, self.paddle1)

        self.assertTrue(result[0])  # Should play sound
        self.assertEqual(result[1], 1)  # Paddle number
        self.assertNotEqual(self.ball.velocity_x, original_vx)  # Ball should bounce

    def test_check_powerup_collision_not_active(self) -> None:
        """Test powerup collision when not active"""
        powerup = PowerUp()
        powerup.active = False
        powerup.affected_paddle = None
        powerup.rect.center = (50, 360)
        self.paddle1.rect.center = (50, 360)

        result = self.collision_manager.check_powerup_collision(powerup, self.paddle1)
        self.assertTrue(result)

    def test_check_powerup_collision_active(self) -> None:
        """Test powerup collision when active"""
        powerup = PowerUp()
        powerup.active = True
        powerup.affected_paddle = self.paddle1

        result = self.collision_manager.check_powerup_collision(powerup, self.paddle1)
        self.assertFalse(result)

    def test_check_ball_powerup_collision_slow_ball(self) -> None:
        """Test ball-powerup collision for slow_ball"""
        powerup = PowerUp()
        powerup.active = True
        powerup.type = "slow_ball"
        powerup.rect.center = (500, 360)
        self.ball.rect.center = (500, 360)

        result = self.collision_manager.check_ball_powerup_collision(powerup, self.ball)
        self.assertTrue(result)

    def test_check_ball_powerup_collision_wrong_type(self) -> None:
        """Test ball-powerup collision for non slow_ball powerup"""
        powerup = PowerUp()
        powerup.active = True
        powerup.type = "speed_boost"
        powerup.rect.center = (500, 360)
        self.ball.rect.center = (500, 360)

        result = self.collision_manager.check_ball_powerup_collision(powerup, self.ball)
        self.assertFalse(result)

    def test_check_score_goal_player1(self) -> None:
        """Test goal scored by player 1"""
        # Ball out on left side (player 2 scores)
        self.ball.rect.centerx = -20
        result = self.collision_manager.check_score(self.ball, 1024)
        self.assertEqual(result, 2)

    def test_check_score_goal_player2(self) -> None:
        """Test goal scored by player 2"""
        # Ball out on right side (player 1 scores)
        self.ball.rect.centerx = 1100
        result = self.collision_manager.check_score(self.ball, 1024)
        self.assertEqual(result, 1)

    def test_check_score_no_goal(self) -> None:
        """Test no goal scored"""
        self.ball.rect.centerx = 500
        result = self.collision_manager.check_score(self.ball, 1024)
        self.assertIsNone(result)

    def test_get_shake_intensity_goal(self) -> None:
        """Test shake intensity for goal"""
        intensity = self.collision_manager.get_shake_intensity(is_goal=True)
        self.assertEqual(intensity, (15, 15))

    def test_get_shake_intensity_normal(self) -> None:
        """Test shake intensity for normal hit"""
        intensity = self.collision_manager.get_shake_intensity(is_goal=False)
        self.assertEqual(intensity, (5, 5))

    def test_check_multi_ball_collisions(self) -> None:
        """Test multiple ball collisions"""
        ball1 = Ball()
        ball2 = Ball()
        ball1.rect.center = (55, 360)
        ball1.velocity_x = -5
        ball2.rect.center = (500, 360)
        balls = [ball1, ball2]

        collisions = self.collision_manager.check_multi_ball_collisions(balls, self.paddle1)

        self.assertEqual(len(collisions), 2)
        # First ball should collide, second should not
        self.assertTrue(collisions[0][1])
        self.assertFalse(collisions[1][1])


if __name__ == "__main__":
    unittest.main()
