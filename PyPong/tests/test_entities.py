"""
Tests for core game entities: Paddle, Ball, PowerUp
"""
import pytest
from unittest.mock import MagicMock, patch
import sys
from pathlib import Path

# Add parent directory to path
current_dir = Path(__file__).parent.parent
if str(current_dir.parent) not in sys.path:
    sys.path.insert(0, str(current_dir.parent))


class TestPaddle:
    """Тесты для класса Paddle"""
    
    def test_paddle_creation(self, mock_pygame):
        """Создание ракетки"""
        import pygame
        from PyPong.core.entities import Paddle
        
        paddle = Paddle(player_number=1, is_ai=False)
        
        assert paddle.player_number == 1
        assert paddle.is_ai is False
        assert paddle.width > 0
        assert paddle.height > 0
    
    def test_paddle_ai_creation(self, mock_pygame):
        """Создание AI ракетки"""
        from PyPong.core.entities import Paddle
        
        paddle = Paddle(player_number=2, is_ai=True)
        
        assert paddle.is_ai is True
        assert paddle.speed > 0
    
    def test_paddle_reset_position(self, mock_pygame):
        """Сброс позиции ракетки"""
        from PyPong.core.entities import Paddle
        from PyPong.core.config import PADDLE_OFFSET, WINDOW_WIDTH, WINDOW_HEIGHT
        
        paddle = Paddle(player_number=1)
        paddle.reset_position()
        
        assert paddle.rect.centerx == PADDLE_OFFSET
        assert paddle.rect.centery == WINDOW_HEIGHT // 2
    
    def test_paddle_move_up(self, mock_pygame):
        """Движение ракетки вверх"""
        from PyPong.core.entities import Paddle
        
        paddle = Paddle(player_number=1)
        initial_y = paddle.rect.y
        
        paddle.move(up=True, down=False)
        
        assert paddle.rect.y < initial_y
    
    def test_paddle_move_down(self, mock_pygame):
        """Движение ракетки вниз"""
        from PyPong.core.entities import Paddle
        
        paddle = Paddle(player_number=1)
        initial_y = paddle.rect.y
        
        paddle.move(up=False, down=True)
        
        assert paddle.rect.y > initial_y
    
    def test_paddle_resize(self, mock_pygame):
        """Изменение размера ракетки"""
        from PyPong.core.entities import Paddle
        
        paddle = Paddle(player_number=1)
        original_height = paddle.height
        
        paddle.resize(150)
        
        assert paddle.height == 150
        assert paddle.height != original_height
    
    def test_paddle_reset_size(self, mock_pygame):
        """Сброс размера ракетки"""
        from PyPong.core.entities import Paddle
        
        paddle = Paddle(player_number=1)
        original_height = paddle.height
        
        paddle.resize(150)
        paddle.reset_size()
        
        assert paddle.height == original_height


class TestBall:
    """Тесты для класса Ball"""
    
    def test_ball_creation(self, mock_pygame):
        """Создание мяча"""
        from PyPong.core.entities import Ball
        
        ball = Ball()
        
        assert ball.speed > 0
        assert ball.velocity_x != 0 or ball.velocity_y != 0
    
    def test_ball_reset(self, mock_pygame):
        """Сброс мяча в центр"""
        import pygame
        from PyPong.core.entities import Ball
        from PyPong.core.config import WINDOW_WIDTH, WINDOW_HEIGHT
        
        ball = Ball()
        ball.reset_ball()
        
        assert ball.rect.centerx == WINDOW_WIDTH // 2
        assert ball.rect.centery == WINDOW_HEIGHT // 2
    
    def test_ball_move(self, mock_pygame):
        """Движение мяча"""
        from PyPong.core.entities import Ball
        
        ball = Ball()
        initial_x = ball.rect.x
        initial_y = ball.rect.y
        
        ball.move()
        
        # Мяч должен двигаться
        assert (ball.rect.x != initial_x) or (ball.rect.y != initial_y)
    
    def test_ball_bounce_wall(self, mock_pygame):
        """Отскок мяча от стены"""
        from PyPong.core.entities import Ball
        from PyPong.core.config import WINDOW_HEIGHT
        
        ball = Ball()
        ball.rect.top = 0
        initial_vy = ball.velocity_y
        
        ball.bounce_wall()
        
        assert ball.velocity_y == -initial_vy
    
    def test_ball_set_speed(self, mock_pygame):
        """Установка скорости мяча"""
        from PyPong.core.entities import Ball
        
        ball = Ball()
        initial_speed = ball.speed
        
        ball.set_speed(10)
        
        assert ball.speed == 10
        assert ball.speed != initial_speed
    
    def test_ball_is_out_left(self, mock_pygame):
        """Проверка выхода мяча слева"""
        from PyPong.core.entities import Ball
        
        ball = Ball()
        ball.rect.right = -10
        
        assert ball.is_out_left() is True
    
    def test_ball_is_out_right(self, mock_pygame):
        """Проверка выхода мяча справа"""
        from PyPong.core.entities import Ball
        from PyPong.core.config import WINDOW_WIDTH
        
        ball = Ball()
        ball.rect.left = WINDOW_WIDTH + 10
        
        assert ball.is_out_right() is True


class TestPowerUp:
    """Тесты для класса PowerUp"""
    
    def test_powerup_creation(self, mock_pygame):
        """Создание power-up"""
        from PyPong.core.entities import PowerUp
        
        powerup = PowerUp()
        
        assert powerup.type in PowerUp.TYPES
        assert powerup.active is False
    
    def test_powerup_activate(self, mock_pygame):
        """Активация power-up"""
        from PyPong.core.entities import PowerUp, Paddle
        
        powerup = PowerUp()
        paddle = Paddle(player_number=1)
        
        powerup.activate(paddle)
        
        assert powerup.active is True
        assert powerup.affected_paddle == paddle
    
    def test_powerup_deactivate(self, mock_pygame):
        """Деактивация power-up"""
        from PyPong.core.entities import PowerUp, Paddle
        
        powerup = PowerUp()
        paddle = Paddle(player_number=1)
        
        powerup.activate(paddle)
        powerup.deactivate()
        
        assert powerup.active is False
    
    def test_powerup_apply_to_ball_slow_ball(self, mock_pygame):
        """Применение эффекта замедления к мячу"""
        from PyPong.core.entities import PowerUp, Ball
        
        powerup = PowerUp()
        powerup.type = "slow_ball"
        
        ball = Ball()
        initial_speed = ball.speed
        
        powerup.apply_to_ball(ball)
        
        assert ball.speed < initial_speed or ball.speed == initial_speed


class TestPowerUpTypes:
    """Тесты для различных типов power-up"""
    
    def test_speed_boost_exists(self, mock_pygame):
        """Проверка существования speed_boost"""
        from PyPong.core.entities import PowerUp
        
        assert "speed_boost" in PowerUp.TYPES
    
    def test_large_paddle_exists(self, mock_pygame):
        """Проверка существования large_paddle"""
        from PyPong.core.entities import PowerUp
        
        assert "large_paddle" in PowerUp.TYPES
    
    def test_slow_ball_exists(self, mock_pygame):
        """Проверка существования slow_ball"""
        from PyPong.core.entities import PowerUp
        
        assert "slow_ball" in PowerUp.TYPES
    
    def test_multi_ball_exists(self, mock_pygame):
        """Проверка существования multi_ball"""
        from PyPong.core.entities import PowerUp
        
        assert "multi_ball" in PowerUp.TYPES
    
    def test_shrink_opponent_exists(self, mock_pygame):
        """Проверка существования shrink_opponent"""
        from PyPong.core.entities import PowerUp
        
        assert "shrink_opponent" in PowerUp.TYPES
