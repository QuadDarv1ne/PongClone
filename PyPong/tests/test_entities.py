"""
Unit tests for core/entities.py
Paddle, Ball, PowerUp classes
"""
import sys
from pathlib import Path

# Add project root to path
root = Path(__file__).parent.parent.parent
if str(root) not in sys.path:
    sys.path.insert(0, str(root))

import pytest
import math


# Initialize pygame for tests (headless)
import pygame
pygame.init()
pygame.display.set_mode((1, 1))  # Minimal display for tests


class TestPaddle:
    """Tests for Paddle class"""
    
    def test_paddle_creation_player1(self):
        """Test creating player 1 paddle"""
        from PyPong.core.entities import Paddle
        from PyPong.core.config import PADDLE_OFFSET
        
        paddle = Paddle(player_number=1)
        
        assert paddle.player_number == 1
        assert paddle.is_ai is False
        assert paddle.rect.centerx == PADDLE_OFFSET
    
    def test_paddle_creation_player2(self):
        """Test creating player 2 paddle"""
        from PyPong.core.entities import Paddle
        from PyPong.core.config import WINDOW_WIDTH, PADDLE_OFFSET
        
        paddle = Paddle(player_number=2)
        
        assert paddle.player_number == 2
        assert paddle.rect.centerx == WINDOW_WIDTH - PADDLE_OFFSET
    
    def test_paddle_ai_flag(self):
        """Test AI flag is set correctly"""
        from PyPong.core.entities import Paddle
        
        human = Paddle(player_number=1, is_ai=False)
        ai = Paddle(player_number=1, is_ai=True)
        
        assert human.is_ai is False
        assert ai.is_ai is True
    
    def test_paddle_reset_position(self):
        """Test paddle resets to correct position"""
        from PyPong.core.entities import Paddle
        from PyPong.core.config import WINDOW_WIDTH, PADDLE_OFFSET, WINDOW_HEIGHT
        
        paddle = Paddle(player_number=1)
        
        # Move paddle
        paddle.rect.y = 500
        
        # Reset
        paddle.reset_position()
        
        assert paddle.rect.centerx == PADDLE_OFFSET
        assert paddle.rect.centery == WINDOW_HEIGHT // 2
    
    def test_paddle_move_up(self):
        """Test paddle moves up correctly"""
        from PyPong.core.entities import Paddle
        from PyPong.core.config import PADDLE_SPEED
        
        paddle = Paddle(player_number=1)
        initial_y = paddle.rect.y
        
        paddle.move(up=True, down=False)
        
        assert paddle.rect.y == initial_y - PADDLE_SPEED
    
    def test_paddle_move_down(self):
        """Test paddle moves down correctly"""
        from PyPong.core.entities import Paddle
        from PyPong.core.config import PADDLE_SPEED
        
        paddle = Paddle(player_number=1)
        initial_y = paddle.rect.y
        
        paddle.move(up=False, down=True)
        
        assert paddle.rect.y == initial_y + PADDLE_SPEED
    
    def test_paddle_ai_movement(self):
        """Test AI paddle follows ball position"""
        from PyPong.core.entities import Paddle
        
        paddle = Paddle(player_number=2, is_ai=True)
        initial_y = paddle.rect.centery
        
        # Ball below paddle
        paddle.move(up=False, down=False, ball_y=initial_y + 100)
        
        assert paddle.rect.centery > initial_y
    
    def test_paddle_resize(self):
        """Test paddle can be resized"""
        from PyPong.core.entities import Paddle
        
        paddle = Paddle(player_number=1)
        original_height = paddle.height
        
        paddle.resize(100)
        
        assert paddle.height == 100
        assert paddle.rect.height == 100
    
    def test_paddle_set_speed(self):
        """Test paddle speed can be changed"""
        from PyPong.core.entities import Paddle
        from PyPong.core.config import PADDLE_SPEED
        
        paddle = Paddle(player_number=1)
        assert paddle.speed == PADDLE_SPEED
        
        paddle.set_speed(15.0)
        assert paddle.speed == 15.0


class TestBall:
    """Tests for Ball class"""
    
    def test_ball_creation(self):
        """Test ball is created at center"""
        from PyPong.core.entities import Ball
        from PyPong.core.config import WINDOW_WIDTH, WINDOW_HEIGHT
        
        ball = Ball()
        
        assert ball.rect.centerx == WINDOW_WIDTH // 2
        assert ball.rect.centery == WINDOW_HEIGHT // 2
    
    def test_ball_reset(self):
        """Test ball reset returns to center"""
        from PyPong.core.entities import Ball
        from PyPong.core.config import WINDOW_WIDTH, WINDOW_HEIGHT
        
        ball = Ball()
        
        # Move ball
        ball.rect.x = 100
        ball.rect.y = 100
        
        # Reset
        ball.reset_ball()
        
        assert ball.rect.centerx == WINDOW_WIDTH // 2
        assert ball.rect.centery == WINDOW_HEIGHT // 2
    
    def test_ball_has_velocity(self):
        """Test ball has non-zero velocity after reset"""
        from PyPong.core.entities import Ball
        
        ball = Ball()
        
        assert ball.velocity_x != 0 or ball.velocity_y != 0
    
    def test_ball_move(self):
        """Test ball moves correctly"""
        from PyPong.core.entities import Ball
        
        ball = Ball()
        ball.velocity_x = 5.0
        ball.velocity_y = 3.0
        
        initial_x = ball.rect.x
        initial_y = ball.rect.y
        
        ball.move()
        
        assert ball.rect.x == initial_x + 5
        assert ball.rect.y == initial_y + 3
    
    def test_ball_bounce_wall_top(self):
        """Test ball bounces off top wall"""
        from PyPong.core.entities import Ball
        
        ball = Ball()
        ball.rect.y = 0
        ball.velocity_y = -5.0
        
        ball.bounce_wall()
        
        assert ball.velocity_y > 0
    
    def test_ball_bounce_wall_bottom(self):
        """Test ball bounces off bottom wall"""
        from PyPong.core.entities import Ball
        from PyPong.core.config import WINDOW_HEIGHT
        
        ball = Ball()
        ball.rect.bottom = WINDOW_HEIGHT
        ball.velocity_y = 5.0
        
        ball.bounce_wall()
        
        assert ball.velocity_y < 0
    
    def test_ball_set_speed(self):
        """Test ball speed can be changed"""
        from PyPong.core.entities import Ball
        from PyPong.core.config import BALL_INITIAL_SPEED
        
        ball = Ball()
        initial_speed = ball.speed
        
        ball.set_speed(15.0)
        
        assert ball.speed == 15.0
    
    def test_ball_is_out_left(self):
        """Test ball out of bounds left detection"""
        from PyPong.core.entities import Ball
        
        ball = Ball()
        ball.rect.right = -1
        
        assert ball.is_out_left() is True
    
    def test_ball_is_out_right(self):
        """Test ball out of bounds right detection"""
        from PyPong.core.entities import Ball
        from PyPong.core.config import WINDOW_WIDTH
        
        ball = Ball()
        ball.rect.left = WINDOW_WIDTH + 1
        
        assert ball.is_out_right() is True
    
    def test_ball_increase_speed(self):
        """Test ball speed increases on paddle hit"""
        from PyPong.core.entities import Ball
        from PyPong.core.config import BALL_INITIAL_SPEED, MAX_BALL_SPEED
        
        ball = Ball()
        initial_speed = ball.speed
        
        ball.increase_speed()
        
        assert ball.speed > initial_speed


class TestPowerUp:
    """Tests for PowerUp class"""
    
    def test_powerup_creation(self):
        """Test powerup is created with random type"""
        from PyPong.core.entities import PowerUp
        
        powerup = PowerUp()
        
        assert powerup.type in PowerUp.TYPES
        assert powerup.active is False
    
    def test_powerup_types(self):
        """Test all powerup types are defined"""
        from PyPong.core.entities import PowerUp
        
        expected_types = [
            "speed_boost",
            "large_paddle", 
            "slow_ball",
            "multi_ball",
            "shrink_opponent"
        ]
        
        assert set(expected_types) == set(PowerUp.TYPES.keys())
    
    def test_powerup_activate(self):
        """Test powerup activates on paddle"""
        from PyPong.core.entities import PowerUp, Paddle
        
        powerup = PowerUp()
        paddle = Paddle(player_number=1)
        
        powerup.activate(paddle)
        
        assert powerup.active is True
        assert powerup.affected_paddle == paddle
    
    def test_powerup_deactivate(self):
        """Test powerup deactivates properly"""
        from PyPong.core.entities import PowerUp, Paddle
        
        powerup = PowerUp()
        paddle = Paddle(player_number=1)
        
        powerup.activate(paddle)
        powerup.deactivate()
        
        assert powerup.active is False
    
    def test_powerup_speed_boost_effect(self):
        """Test speed_boost increases paddle speed"""
        from PyPong.core.entities import PowerUp, Paddle
        from PyPong.core.config import PADDLE_SPEED
        
        powerup = PowerUp()
        powerup.type = "speed_boost"
        
        paddle = Paddle(player_number=1)
        original_speed = paddle.speed
        
        powerup.activate(paddle)
        
        assert paddle.speed > original_speed


class TestBallPaddleCollision:
    """Tests for ball-paddle collision physics"""
    
    def test_bounce_paddle_center(self):
        """Test ball bounces correctly from center of paddle"""
        from PyPong.core.entities import Ball, Paddle
        from PyPong.core.config import WINDOW_WIDTH
        
        ball = Ball()
        paddle = Paddle(player_number=1)
        
        # Position ball at paddle
        ball.rect.right = paddle.rect.left + 5
        ball.rect.centery = paddle.rect.centery
        
        # Reset ball velocity toward paddle
        ball.velocity_x = -5
        ball.velocity_y = 0
        
        initial_vx = ball.velocity_x
        
        ball.bounce_paddle(paddle)
        
        # Should now move toward player 2 (positive x)
        assert ball.velocity_x > 0
    
    def test_bounce_paddle_angle(self):
        """Test ball angle changes based on paddle hit position"""
        from PyPong.core.entities import Ball, Paddle
        
        ball = Ball()
        paddle = Paddle(player_number=1)
        
        # Position ball at top of paddle
        ball.rect.right = paddle.rect.left + 5
        ball.rect.top = paddle.rect.top + 5
        
        ball.velocity_x = -5
        ball.velocity_y = 0
        
        ball.bounce_paddle(paddle)
        
        # Should have upward angle (negative y velocity)
        assert ball.velocity_y < 0


if __name__ == "__main__":
    pytest.main([__file__, "-v"])
