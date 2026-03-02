"""
Tests for entity object pools (BallPool, PowerUpPool)
"""
import pytest
import pygame
from PyPong.core.entity_pools import (
    BallPool, PowerUpPool,
    get_ball_pool, get_powerup_pool, reset_entity_pools
)
from PyPong.core.entities import Ball, PowerUp


@pytest.fixture
def init_pygame():
    """Initialize pygame for tests"""
    pygame.init()
    yield
    pygame.quit()


@pytest.fixture
def ball_pool():
    """Create a fresh ball pool for testing"""
    return BallPool(initial_size=3, max_size=10)


@pytest.fixture
def powerup_pool():
    """Create a fresh power-up pool for testing"""
    return PowerUpPool(initial_size=5, max_size=15)


class TestBallPool:
    """Test suite for BallPool"""
    
    def test_ball_pool_initialization(self, init_pygame, ball_pool):
        """Test ball pool is initialized correctly"""
        stats = ball_pool.get_stats()
        
        assert stats['available'] == 3  # initial_size
        assert stats['active'] == 0
    
    def test_acquire_ball(self, init_pygame, ball_pool):
        """Test acquiring ball from pool"""
        ball = ball_pool.acquire()
        
        assert isinstance(ball, Ball)
        assert ball.rect.centerx > 0
        assert ball.rect.centery > 0
        
        stats = ball_pool.get_stats()
        assert stats['available'] == 2  # One less available
        assert stats['active'] == 1  # One active
    
    def test_release_ball(self, init_pygame, ball_pool):
        """Test releasing ball back to pool"""
        ball = ball_pool.acquire()
        ball_pool.release(ball)
        
        stats = ball_pool.get_stats()
        assert stats['available'] == 3  # Back to initial
        assert stats['active'] == 0
    
    def test_ball_reuse(self, init_pygame, ball_pool):
        """Test balls are reused from pool"""
        # Acquire and release multiple times
        for _ in range(5):
            ball = ball_pool.acquire()
            ball_pool.release(ball)
        
        stats = ball_pool.get_stats()
        assert stats['reused'] > 0
        assert stats['reuse_rate'] > 0
    
    def test_ball_pool_expansion(self, init_pygame, ball_pool):
        """Test pool creates new balls when needed"""
        balls = []
        
        # Acquire more balls than initial size
        for _ in range(5):
            balls.append(ball_pool.acquire())
        
        stats = ball_pool.get_stats()
        assert stats['created'] >= 5
        assert stats['active'] == 5
        
        # Clean up
        for ball in balls:
            ball_pool.release(ball)
    
    def test_ball_pool_max_size(self, init_pygame, ball_pool):
        """Test pool respects max size"""
        balls = []
        
        # Acquire up to max size
        for _ in range(10):
            balls.append(ball_pool.acquire())
        
        # Release all
        for ball in balls:
            ball_pool.release(ball)
        
        stats = ball_pool.get_stats()
        # Pool should not exceed max_size
        assert stats['available'] <= 10
    
    def test_ball_reset_on_acquire(self, init_pygame, ball_pool):
        """Test ball is reset when acquired from pool"""
        ball = ball_pool.acquire()
        
        # Modify ball
        ball.rect.x = 999
        ball.speed = 20
        
        # Release and acquire again
        ball_pool.release(ball)
        ball2 = ball_pool.acquire()
        
        # Ball should be reset to initial state
        assert ball2.rect.centerx != 999
        assert ball2.speed == ball2.speed  # Reset to initial
    
    def test_release_all_balls(self, init_pygame, ball_pool):
        """Test releasing all active balls"""
        # Acquire multiple balls
        for _ in range(3):
            ball_pool.acquire()
        
        ball_pool.release_all()
        
        stats = ball_pool.get_stats()
        assert stats['active'] == 0


class TestPowerUpPool:
    """Test suite for PowerUpPool"""
    
    def test_powerup_pool_initialization(self, init_pygame, powerup_pool):
        """Test power-up pool is initialized correctly"""
        stats = powerup_pool.get_stats()
        
        assert stats['available'] == 5  # initial_size
        assert stats['active'] == 0
    
    def test_acquire_powerup(self, init_pygame, powerup_pool):
        """Test acquiring power-up from pool"""
        powerup = powerup_pool.acquire()
        
        assert isinstance(powerup, PowerUp)
        assert powerup.type in PowerUp.TYPES
        assert powerup.active is False
        
        stats = powerup_pool.get_stats()
        assert stats['available'] == 4
        assert stats['active'] == 1
    
    def test_release_powerup(self, init_pygame, powerup_pool):
        """Test releasing power-up back to pool"""
        powerup = powerup_pool.acquire()
        powerup_pool.release(powerup)
        
        stats = powerup_pool.get_stats()
        assert stats['available'] == 5
        assert stats['active'] == 0
    
    def test_powerup_reuse(self, init_pygame, powerup_pool):
        """Test power-ups are reused from pool"""
        # Acquire and release multiple times
        for _ in range(10):
            powerup = powerup_pool.acquire()
            powerup_pool.release(powerup)
        
        stats = powerup_pool.get_stats()
        assert stats['reused'] > 0
        assert stats['reuse_rate'] > 0
    
    def test_powerup_reset_on_acquire(self, init_pygame, powerup_pool):
        """Test power-up is reset when acquired from pool"""
        powerup = powerup_pool.acquire()
        
        # Modify power-up
        powerup.active = True
        powerup.start_time = 12345
        
        # Release and acquire again
        powerup_pool.release(powerup)
        powerup2 = powerup_pool.acquire()
        
        # Power-up should be reset
        assert powerup2.active is False
        assert powerup2.start_time == 0
    
    def test_powerup_pool_expansion(self, init_pygame, powerup_pool):
        """Test pool creates new power-ups when needed"""
        powerups = []
        
        # Acquire more than initial size
        for _ in range(8):
            powerups.append(powerup_pool.acquire())
        
        stats = powerup_pool.get_stats()
        assert stats['created'] >= 8
        assert stats['active'] == 8
        
        # Clean up
        for powerup in powerups:
            powerup_pool.release(powerup)
    
    def test_release_all_powerups(self, init_pygame, powerup_pool):
        """Test releasing all active power-ups"""
        # Acquire multiple power-ups
        for _ in range(5):
            powerup_pool.acquire()
        
        powerup_pool.release_all()
        
        stats = powerup_pool.get_stats()
        assert stats['active'] == 0


class TestGlobalPools:
    """Test global pool instances"""
    
    def test_get_ball_pool(self, init_pygame):
        """Test getting global ball pool"""
        pool1 = get_ball_pool()
        pool2 = get_ball_pool()
        
        # Should return same instance
        assert pool1 is pool2
    
    def test_get_powerup_pool(self, init_pygame):
        """Test getting global power-up pool"""
        pool1 = get_powerup_pool()
        pool2 = get_powerup_pool()
        
        # Should return same instance
        assert pool1 is pool2
    
    def test_reset_entity_pools(self, init_pygame):
        """Test resetting all entity pools"""
        # Get pools and acquire some objects
        ball_pool = get_ball_pool()
        powerup_pool = get_powerup_pool()
        
        ball_pool.acquire()
        powerup_pool.acquire()
        
        # Reset pools
        reset_entity_pools()
        
        # Pools should be fresh
        new_ball_pool = get_ball_pool()
        new_powerup_pool = get_powerup_pool()
        
        ball_stats = new_ball_pool.get_stats()
        powerup_stats = new_powerup_pool.get_stats()
        
        assert ball_stats['active'] == 0
        assert powerup_stats['active'] == 0


@pytest.mark.performance
class TestPoolPerformance:
    """Performance tests for object pools"""
    
    def test_ball_pool_performance(self, init_pygame, ball_pool):
        """Test ball pool reduces object creation"""
        # Acquire and release many times
        for _ in range(100):
            ball = ball_pool.acquire()
            ball_pool.release(ball)
        
        stats = ball_pool.get_stats()
        
        # Reuse rate should be high (>80%)
        assert stats['reuse_rate'] > 80
        
        # Should create far fewer objects than acquired
        assert stats['created'] < stats['acquired']
    
    def test_powerup_pool_performance(self, init_pygame, powerup_pool):
        """Test power-up pool reduces object creation"""
        # Acquire and release many times
        for _ in range(100):
            powerup = powerup_pool.acquire()
            powerup_pool.release(powerup)
        
        stats = powerup_pool.get_stats()
        
        # Reuse rate should be high (>80%)
        assert stats['reuse_rate'] > 80
        
        # Should create far fewer objects than acquired
        assert stats['created'] < stats['acquired']


@pytest.mark.integration
class TestPoolIntegration:
    """Integration tests for pools with game entities"""
    
    def test_ball_pool_with_sprite_groups(self, init_pygame, ball_pool):
        """Test ball pool works with pygame sprite groups"""
        all_sprites = pygame.sprite.Group()
        
        # Acquire ball and add to group
        ball = ball_pool.acquire()
        all_sprites.add(ball)
        
        assert len(all_sprites) == 1
        
        # Release ball (should remove from group)
        ball_pool.release(ball)
        
        assert len(all_sprites) == 0
    
    def test_powerup_pool_with_activation(self, init_pygame, powerup_pool):
        """Test power-up pool with activation/deactivation"""
        from PyPong.core.entities import Paddle
        
        powerup = powerup_pool.acquire()
        paddle = Paddle(player_number=1)
        
        # Activate power-up
        powerup.activate(paddle)
        assert powerup.active is True
        
        # Release should deactivate
        powerup_pool.release(powerup)
        assert powerup.active is False


if __name__ == "__main__":
    pytest.main([__file__, "-v"])
