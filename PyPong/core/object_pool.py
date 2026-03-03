"""
Generic object pooling system for performance optimization
"""
from typing import Any, Callable, Dict, Generic, List, Optional, TypeVar

from PyPong.core.logger import logger

T = TypeVar("T")


class ObjectPool(Generic[T]):
    """
    Generic object pool for reusing objects instead of creating/destroying.
    Reduces garbage collection overhead and improves performance.

    Usage:
        # Create pool with factory function
        ball_pool = ObjectPool(lambda: Ball(), initial_size=10, max_size=50)

        # Get object from pool
        ball = ball_pool.acquire()

        # Return object to pool when done
        ball_pool.release(ball)
    """

    def __init__(
        self,
        factory: Callable[[], T],
        initial_size: int = 10,
        max_size: int = 100,
        reset_func: Optional[Callable[[T], None]] = None,
    ):
        """
        Initialize object pool

        Args:
            factory: Function to create new objects
            initial_size: Number of objects to pre-create
            max_size: Maximum pool size
            reset_func: Optional function to reset object state before reuse
        """
        self._factory = factory
        self._max_size = max_size
        self._reset_func = reset_func

        # Available objects
        self._available: List[T] = []

        # Active objects (for tracking)
        self._active: List[T] = []

        # Statistics
        self._created_count = 0
        self._acquired_count = 0
        self._released_count = 0
        self._reused_count = 0

        # Pre-create initial objects
        self._preallocate(initial_size)

        logger.debug(f"ObjectPool initialized: initial={initial_size}, max={max_size}")

    def _preallocate(self, count: int) -> None:
        """Pre-create objects for the pool"""
        for _ in range(count):
            obj = self._factory()
            self._available.append(obj)
            self._created_count += 1

    def acquire(self) -> T:
        """
        Get an object from the pool.
        Creates new object if pool is empty.

        Returns:
            Object from pool or newly created
        """
        self._acquired_count += 1

        if self._available:
            # Reuse existing object
            obj = self._available.pop()
            self._reused_count += 1

            # Reset object state if reset function provided
            if self._reset_func:
                self._reset_func(obj)
        else:
            # Create new object
            obj = self._factory()
            self._created_count += 1

        self._active.append(obj)
        return obj

    def release(self, obj: T) -> None:
        """
        Return an object to the pool for reuse.

        Args:
            obj: Object to return to pool
        """
        if obj not in self._active:
            logger.warning("Attempting to release object not from this pool")
            return

        self._released_count += 1
        self._active.remove(obj)

        # Only keep object if pool not at max size
        if len(self._available) < self._max_size:
            self._available.append(obj)
        else:
            # Pool is full, let object be garbage collected
            logger.debug("Pool at max size, discarding object")

    def release_all(self) -> None:
        """Release all active objects back to pool"""
        while self._active:
            obj = self._active.pop()
            if len(self._available) < self._max_size:
                self._available.append(obj)

        self._released_count += len(self._active)

    def clear(self) -> None:
        """Clear all objects from pool"""
        self._available.clear()
        self._active.clear()

    def get_stats(self) -> Dict[str, int]:
        """Get pool statistics"""
        return {
            "available": len(self._available),
            "active": len(self._active),
            "created": self._created_count,
            "acquired": self._acquired_count,
            "released": self._released_count,
            "reused": self._reused_count,
            "reuse_rate": (self._reused_count / self._acquired_count * 100 if self._acquired_count > 0 else 0),
        }

    def __len__(self) -> int:
        """Total objects in pool (available + active)"""
        return len(self._available) + len(self._active)

    def __repr__(self) -> str:
        stats = self.get_stats()
        return (
            f"ObjectPool(available={stats['available']}, "
            f"active={stats['active']}, "
            f"reuse_rate={stats['reuse_rate']:.1f}%)"
        )


class PoolManager:
    """
    Manages multiple object pools.
    Provides centralized access to all pools.
    """

    def __init__(self):
        self._pools: Dict[str, ObjectPool] = {}

    def create_pool(
        self,
        name: str,
        factory: Callable[[], Any],
        initial_size: int = 10,
        max_size: int = 100,
        reset_func: Optional[Callable[[Any], None]] = None,
    ) -> ObjectPool:
        """
        Create a new object pool

        Args:
            name: Pool identifier
            factory: Function to create objects
            initial_size: Initial pool size
            max_size: Maximum pool size
            reset_func: Optional reset function

        Returns:
            Created object pool
        """
        if name in self._pools:
            logger.warning(f"Pool '{name}' already exists, returning existing pool")
            return self._pools[name]

        pool = ObjectPool(factory, initial_size, max_size, reset_func)
        self._pools[name] = pool
        logger.info(f"Created pool '{name}'")

        return pool

    def get_pool(self, name: str) -> Optional[ObjectPool]:
        """Get pool by name"""
        return self._pools.get(name)

    def remove_pool(self, name: str) -> None:
        """Remove and clear a pool"""
        if name in self._pools:
            self._pools[name].clear()
            del self._pools[name]
            logger.info(f"Removed pool '{name}'")

    def clear_all(self) -> None:
        """Clear all pools"""
        for pool in self._pools.values():
            pool.clear()
        self._pools.clear()

    def get_all_stats(self) -> Dict[str, Dict[str, int]]:
        """Get statistics for all pools"""
        return {name: pool.get_stats() for name, pool in self._pools.items()}

    def print_stats(self) -> None:
        """Print statistics for all pools"""
        logger.info("=== Object Pool Statistics ===")
        for name, stats in self.get_all_stats().items():
            logger.info(
                f"{name}: available={stats['available']}, "
                f"active={stats['active']}, "
                f"reuse_rate={stats['reuse_rate']:.1f}%"
            )


# Global pool manager
_pool_manager: Optional[PoolManager] = None


def get_pool_manager() -> PoolManager:
    """Get global pool manager instance"""
    global _pool_manager
    if _pool_manager is None:
        _pool_manager = PoolManager()
    return _pool_manager


def reset_pool_manager() -> None:
    """Reset global pool manager (useful for testing)"""
    global _pool_manager
    if _pool_manager:
        _pool_manager.clear_all()
    _pool_manager = PoolManager()
