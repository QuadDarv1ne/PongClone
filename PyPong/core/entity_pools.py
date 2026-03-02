"""
Specialized object pools for game entities (Ball, PowerUp)
"""
from typing import Optional
from PyPong.core.object_pool import ObjectPool
from PyPong.core.entities import Ball, PowerUp
from PyPong.core.logger import logger


class BallPool:
    """
    Specialized object pool for Ball entities.
    Manages ball creation, reuse, and cleanup.
    """
    
    def __init__(self, initial_size: int = 5, max_size: int = 20):
        """
        Initialize ball pool
        
        Args:
            initial_size: Number of balls to pre-create
            max_size: Maximum number of balls in pool
        """
        self._pool = ObjectPool(
            factory=Ball,
            initial_size=initial_size,
            max_size=max_size,
            reset_func=self._reset_ball,
        )
        logger.info(f"BallPool initialized: initial={initial_size}, max={max_size}")
    
    @staticmethod
    def _reset_ball(ball: Ball) -> None:
        """Reset ball to initial state"""
        ball.reset_ball()
        # Ensure ball is visible and active
        if hasattr(ball, 'kill'):
            # Remove from any sprite groups
            ball.kill()
    
    def acquire(self) -> Ball:
        """
        Get a ball from the pool
        
        Returns:
            Ball instance ready to use
        """
        ball = self._pool.acquire()
        logger.debug(f"Ball acquired from pool. Pool stats: {self._pool.get_stats()}")
        return ball
    
    def release(self, ball: Ball) -> None:
        """
        Return a ball to the pool
        
        Args:
            ball: Ball to return to pool
        """
        # Remove from sprite groups before returning to pool
        ball.kill()
        self._pool.release(ball)
        logger.debug(f"Ball released to pool. Pool stats: {self._pool.get_stats()}")
    
    def release_all(self) -> None:
        """Release all active balls back to pool"""
        self._pool.release_all()
    
    def get_stats(self):
        """Get pool statistics"""
        return self._pool.get_stats()
    
    def print_stats(self) -> None:
        """Print pool statistics"""
        stats = self.get_stats()
        logger.info(
            f"BallPool: available={stats['available']}, "
            f"active={stats['active']}, "
            f"reuse_rate={stats['reuse_rate']:.1f}%"
        )


class PowerUpPool:
    """
    Specialized object pool for PowerUp entities.
    Manages power-up creation, reuse, and cleanup.
    """
    
    def __init__(self, initial_size: int = 10, max_size: int = 30):
        """
        Initialize power-up pool
        
        Args:
            initial_size: Number of power-ups to pre-create
            max_size: Maximum number of power-ups in pool
        """
        self._pool = ObjectPool(
            factory=PowerUp,
            initial_size=initial_size,
            max_size=max_size,
            reset_func=self._reset_powerup,
        )
        logger.info(f"PowerUpPool initialized: initial={initial_size}, max={max_size}")
    
    @staticmethod
    def _reset_powerup(powerup: PowerUp) -> None:
        """Reset power-up to initial state"""
        # Reset power-up state
        powerup.active = False
        powerup.start_time = 0
        powerup.affected_paddle = None
        
        # Randomize type and position (will be set by game logic)
        from random import choice, randint
        from PyPong.core.config import WINDOW_WIDTH, WINDOW_HEIGHT
        
        powerup.type = choice(list(PowerUp.TYPES.keys()))
        powerup.image.fill(PowerUp.TYPES[powerup.type]["color"])
        powerup.rect.center = (
            randint(WINDOW_WIDTH // 4, 3 * WINDOW_WIDTH // 4),
            randint(50, WINDOW_HEIGHT - 50)
        )
        
        # Remove from sprite groups
        if hasattr(powerup, 'kill'):
            powerup.kill()
    
    def acquire(self) -> PowerUp:
        """
        Get a power-up from the pool
        
        Returns:
            PowerUp instance ready to use
        """
        powerup = self._pool.acquire()
        logger.debug(f"PowerUp acquired from pool. Pool stats: {self._pool.get_stats()}")
        return powerup
    
    def release(self, powerup: PowerUp) -> None:
        """
        Return a power-up to the pool
        
        Args:
            powerup: PowerUp to return to pool
        """
        # Deactivate and remove from sprite groups
        if powerup.active:
            powerup.deactivate()
        else:
            powerup.kill()
        
        self._pool.release(powerup)
        logger.debug(f"PowerUp released to pool. Pool stats: {self._pool.get_stats()}")
    
    def release_all(self) -> None:
        """Release all active power-ups back to pool"""
        self._pool.release_all()
    
    def get_stats(self):
        """Get pool statistics"""
        return self._pool.get_stats()
    
    def print_stats(self) -> None:
        """Print pool statistics"""
        stats = self.get_stats()
        logger.info(
            f"PowerUpPool: available={stats['available']}, "
            f"active={stats['active']}, "
            f"reuse_rate={stats['reuse_rate']:.1f}%"
        )


# Global pool instances
_ball_pool: Optional[BallPool] = None
_powerup_pool: Optional[PowerUpPool] = None


def get_ball_pool() -> BallPool:
    """Get global ball pool instance"""
    global _ball_pool
    if _ball_pool is None:
        _ball_pool = BallPool()
    return _ball_pool


def get_powerup_pool() -> PowerUpPool:
    """Get global power-up pool instance"""
    global _powerup_pool
    if _powerup_pool is None:
        _powerup_pool = PowerUpPool()
    return _powerup_pool


def reset_entity_pools() -> None:
    """Reset all entity pools (useful for testing)"""
    global _ball_pool, _powerup_pool
    
    if _ball_pool:
        _ball_pool.release_all()
    if _powerup_pool:
        _powerup_pool.release_all()
    
    _ball_pool = BallPool()
    _powerup_pool = PowerUpPool()
    
    logger.info("Entity pools reset")


def print_all_pool_stats() -> None:
    """Print statistics for all entity pools"""
    logger.info("=== Entity Pool Statistics ===")
    if _ball_pool:
        _ball_pool.print_stats()
    if _powerup_pool:
        _powerup_pool.print_stats()
