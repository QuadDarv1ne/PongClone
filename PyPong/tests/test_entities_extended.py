"""
Extended tests for game entities (Paddle, Ball, PowerUp)
"""
import pytest
import pygame
from PyPong.core.entities import Paddle, Ball, PowerUp
from PyPong.core.config import (
    WINDOW_WIDTH, WINDOW_HEIGHT, PADDLE_WIDTH, PADDLE_HEIGHT,
    BALL_SIZE, BALL_INITIAL_SPEED, MAX_BALL_SPEED, WHITE
)


@pytest.fixture
def init_pygame():
    """Initialize pygame for tests"""
    pygame.init()
    yield
    pygame.quit()


class TestPaddle:
    """Test suite for Paddle class"""
    
    def test_paddle_initialization(self, init_pygame):
        """Test paddle is initialized correctly"""
        paddle = Paddle(player_number=1, is_ai=False, color=WHITE)
        
        assert paddle.player_number == 1
        assert paddle.is_ai is False
        assert paddle.width == PADDLE_WIDTH
        assert paddle.height == PADDLE_HEIGHT
        assert paddle.color == WHITE
        assert paddle.rect.centerx == 50  # PADDLE_OFFSET
        assert paddle.rect.centery == WINDOW_HEIGHT // 2
    
    def test_paddle_reset_position(self, init_pygame):
        """Test paddle reset to initial position"""
        paddle = Paddle(player_number=2)
        
        # Move paddle
        paddle.rect.y = 100
        
        # Reset
        paddle.reset_position()
        
        assert paddle.rect.centerx == WINDOW_WIDTH - 50
        assert paddle.rect.centery == WINDOW_HEIGHT // 2
    
    def test_paddle_move_up(self, init_pygame):
        """Test paddle moves up"""
        paddle = Paddle(player_number=1)
        initial_y = paddle.rect.y
        
        paddle.move(up=True, down=False)
        
        assert paddle.rect.y < initial_y
    
    def test_paddle_move_down(self, init_pygame):
        """Test paddle moves down"""
        paddle = Paddle(player_number=1)
        initial_y = paddle.rect.y
        
        paddle.move(up=False, down=True)
        
        assert paddle.rect.y > initial_y
    
    def test_paddle_boundary_top(self, init_pygame):
        """Test paddle cannot move above screen"""
        paddle = Paddle(player_number=1)
        paddle.rect.y = 0
        
        # Try to move up
        for _ in range(10):
            paddle.move(up=True, down=False)
        
        assert paddle.rect.top >= 0
    
    def test_paddle_boundary_bottom(self, init_pygame):
        """Test paddle cannot move below screen"""
        paddle = Paddle(player_number=1)
        paddle.rect.y = WINDOW_HEIGHT - paddle.height
        
        # Try to move down
        for _ in range(10):
            paddle.move(up=False, down=True)
        
        assert paddle.rect.bottom <= WINDOW_HEIGHT
    
    def test_paddle_ai_movement(self, init_pygame):
        """Test AI paddle follows ball"""
        paddle = Paddle(player_number=2, is_ai=True)
        paddle.rect.centery = WINDOW_HEIGHT // 2
        
        # Ball above paddle
        ball_y = WINDOW_HEIGHT // 4
        paddle.move(up=False, down=False, ball_y=ball_y)
        
        # Paddle should move up towards ball
        assert paddle.rect.centery < WINDOW_HEIGHT // 2
    
    def test_paddle_resize(self, init_pygame):
        """Test paddle can be resized"""
        paddle = Paddle(player_number=1)
        original_height = paddle.height
        
        paddle.resize(150)
        
        assert paddle.height == 150
        assert paddle.height != original_height
    
    def test_paddle_reset_size(self, init_pygame):
        """Test paddle size can be reset"""
        paddle = Paddle(player_number=1)
        original_height = paddle.height
        
        paddle.resize(150)
        paddle.reset_size()
        
        assert paddle.height == original_height
    
    def test_paddle_set_speed(self, init_pygame):
        """Test paddle speed can be changed"""
        paddle = Paddle(player_number=1)
        original_speed = paddle.speed
        
        paddle.set_speed(15)
        
        assert paddle.speed == 15
        assert paddle.speed != original_speed
    
    def test_predict_ball_position_basic(self, init_pygame):
        """Test ball position prediction"""
        paddle = Paddle(player_number=2, is_ai=True)
        
        # Ball moving towards paddle
        ball_x = WINDOW_WIDTH // 2
        ball_y = WINDOW_HEIGHT // 2
        ball_vx = 5
        ball_vy = 3
        
        predicted_y = paddle.predict_ball_position(ball_x, ball_y, ball_vx, ball_vy)
        
        # Predicted position should be within screen bounds
        assert 0 <= predicted_y <= WINDOW_HEIGHT
    
    def test_predict_ball_position_away(self, init_pygame):
        """Test prediction when ball moves away"""
        paddle = Paddle(player_number=2, is_ai=True)
        
        # Ball moving away from paddle
        ball_x = WINDOW_WIDTH // 2
        ball_y = WINDOW_HEIGHT // 2
        ball_vx = -5  # Moving left (away from right paddle)
        ball_vy = 3
        
        predicted_y = paddle.predict_ball_position(ball_x, ball_y, ball_vx, ball_vy)
        
        # Should return current position
        assert predicted_y == ball_y
    
    def test_predict_ball_position_no_infinite_loop(self, init_pygame):
        """Test prediction doesn't cause infinite loop"""
        paddle = Paddle(player_number=2, is_ai=True)
        
        # Edge case: very slow ball
        ball_x = WINDOW_WIDTH // 2
        ball_y = WINDOW_HEIGHT // 2
        ball_vx = 0.01
        ball_vy = 0.01
        
        # Should complete without hanging
        predicted_y = paddle.predict_ball_position(ball_x, ball_y, ball_vx, ball_vy)
        
        assert isinstance(predicted_y, (int, float))


class TestBall:
    """Test suite for Ball class"""
    
    def test_ball_initialization(self, init_pygame):
        """Test ball is initialized correctly"""
        ball = Ball()
        
        assert ball.rect.width == BALL_SIZE
        assert ball.rect.height == BALL_SIZE
        assert ball.speed == BALL_INITIAL_SPEED
        assert ball.velocity_x != 0
        assert ball.velocity_y != 0
    
    def test_ball_reset(self, init_pygame):
        """Test ball reset to center"""
        ball = Ball()
        
        # Move ball
        ball.rect.x = 100
        ball.rect.y = 100
        ball.speed = 10
        
        # Reset
        ball.reset_ball()
        
        assert ball.rect.centerx == WINDOW_WIDTH // 2
        assert ball.rect.centery == WINDOW_HEIGHT // 2
        assert ball.speed == BALL_INITIAL_SPEED
    
    def test_ball_move(self, init_pygame):
        """Test ball moves according to velocity"""
        ball = Ball()
        initial_x = ball.rect.x
        initial_y = ball.rect.y
        
        ball.move()
        
        # Ball should have moved
        assert ball.rect.x != initial_x or ball.rect.y != initial_y
    
    def test_ball_bounce_wall_top(self, init_pygame):
        """Test ball bounces off top wall"""
        ball = Ball()
        ball.rect.y = -5
        ball.velocity_y = -5
        
        ball.bounce_wall()
        
        assert ball.velocity_y > 0  # Should reverse direction
    
    def test_ball_bounce_wall_bottom(self, init_pygame):
        """Test ball bounces off bottom wall"""
        ball = Ball()
        ball.rect.y = WINDOW_HEIGHT + 5
        ball.velocity_y = 5
        
        ball.bounce_wall()
        
        assert ball.velocity_y < 0  # Should reverse direction
    
    def test_ball_increase_speed(self, init_pygame):
        """Test ball speed increases"""
        ball = Ball()
        initial_speed = ball.speed
        
        ball.increase_speed()
        
        assert ball.speed > initial_speed
    
    def test_ball_max_speed(self, init_pygame):
        """Test ball speed doesn't exceed maximum"""
        ball = Ball()
        
        # Increase speed many times
        for _ in range(100):
            ball.increase_speed()
        
        assert ball.speed <= MAX_BALL_SPEED
    
    def test_ball_set_speed(self, init_pygame):
        """Test ball speed can be set while maintaining direction"""
        ball = Ball()
        ball.velocity_x = 5
        ball.velocity_y = 3
        
        # Calculate initial angle
        import math
        initial_angle = math.atan2(ball.velocity_y, ball.velocity_x)
        
        ball.set_speed(10)
        
        # Check speed changed
        assert ball.speed == 10
        
        # Check angle maintained
        new_angle = math.atan2(ball.velocity_y, ball.velocity_x)
        assert abs(initial_angle - new_angle) < 0.01
    
    def test_ball_is_out_left(self, init_pygame):
        """Test ball detection when out of left boundary"""
        ball = Ball()
        ball.rect.x = -20
        
        assert ball.is_out_left() is True
    
    def test_ball_is_out_right(self, init_pygame):
        """Test ball detection when out of right boundary"""
        ball = Ball()
        ball.rect.x = WINDOW_WIDTH + 20
        
        assert ball.is_out_right() is True
    
    def test_ball_bounce_paddle(self, init_pygame):
        """Test ball bounces off paddle"""
        ball = Ball()
        paddle = Paddle(player_number=1)
        
        ball.velocity_x = -5
        initial_speed = ball.speed
        
        ball.bounce_paddle(paddle)
        
        # Ball should reverse horizontal direction
        assert ball.velocity_x > 0
        # Speed should increase
        assert ball.speed > initial_speed


class TestPowerUp:
    """Test suite for PowerUp class"""
    
    def test_powerup_initialization(self, init_pygame):
        """Test power-up is initialized correctly"""
        powerup = PowerUp()
        
        assert powerup.type in PowerUp.TYPES
        assert powerup.active is False
        assert powerup.start_time == 0
        assert powerup.affected_paddle is None
    
    def test_powerup_activate(self, init_pygame):
        """Test power-up activation"""
        powerup = PowerUp()
        paddle = Paddle(player_number=1)
        
        powerup.activate(paddle)
        
        assert powerup.active is True
        assert powerup.start_time > 0
        assert powerup.affected_paddle == paddle
    
    def test_powerup_speed_boost(self, init_pygame):
        """Test speed boost power-up"""
        powerup = PowerUp()
        powerup.type = "speed_boost"
        paddle = Paddle(player_number=1)
        original_speed = paddle.speed
        
        powerup.activate(paddle)
        
        assert paddle.speed > original_speed
    
    def test_powerup_large_paddle(self, init_pygame):
        """Test large paddle power-up"""
        powerup = PowerUp()
        powerup.type = "large_paddle"
        paddle = Paddle(player_number=1)
        original_height = paddle.height
        
        powerup.activate(paddle)
        
        assert paddle.height > original_height
    
    def test_powerup_deactivate(self, init_pygame):
        """Test power-up deactivation"""
        powerup = PowerUp()
        powerup.type = "speed_boost"
        paddle = Paddle(player_number=1)
        
        powerup.activate(paddle)
        powerup.deactivate()
        
        assert powerup.active is False
    
    def test_powerup_slow_ball(self, init_pygame):
        """Test slow ball power-up"""
        powerup = PowerUp()
        powerup.type = "slow_ball"
        ball = Ball()
        ball.speed = 10
        
        powerup.apply_to_ball(ball)
        
        assert ball.speed < 10
    
    def test_powerup_duration(self, init_pygame):
        """Test power-up expires after duration"""
        powerup = PowerUp()
        powerup.type = "speed_boost"
        paddle = Paddle(player_number=1)
        
        powerup.activate(paddle)
        
        # Simulate time passing
        powerup.start_time = pygame.time.get_ticks() - PowerUp.TYPES["speed_boost"]["duration"] - 100
        
        powerup.update()
        
        assert powerup.active is False


@pytest.mark.integration
class TestEntityInteractions:
    """Integration tests for entity interactions"""
    
    def test_ball_paddle_collision(self, init_pygame):
        """Test ball-paddle collision handling"""
        ball = Ball()
        paddle = Paddle(player_number=1)
        
        # Position ball at paddle
        ball.rect.centerx = paddle.rect.centerx
        ball.rect.centery = paddle.rect.centery
        ball.velocity_x = -5
        
        ball.bounce_paddle(paddle)
        
        # Ball should bounce away from paddle
        assert ball.velocity_x > 0
    
    def test_powerup_paddle_interaction(self, init_pygame):
        """Test power-up affects paddle correctly"""
        powerup = PowerUp()
        powerup.type = "large_paddle"
        paddle = Paddle(player_number=1)
        original_height = paddle.height
        
        # Activate power-up
        powerup.activate(paddle)
        assert paddle.height > original_height
        
        # Deactivate power-up
        powerup.deactivate()
        assert paddle.height == original_height
    
    def test_ai_paddle_tracks_ball(self, init_pygame):
        """Test AI paddle follows ball movement"""
        paddle = Paddle(player_number=2, is_ai=True)
        ball = Ball()
        
        # Position ball above paddle
        ball.rect.centery = WINDOW_HEIGHT // 4
        initial_y = paddle.rect.centery
        
        # AI should move towards ball
        for _ in range(10):
            paddle.move(up=False, down=False, ball_y=ball.rect.centery)
        
        assert paddle.rect.centery < initial_y


if __name__ == "__main__":
    pytest.main([__file__, "-v"])
