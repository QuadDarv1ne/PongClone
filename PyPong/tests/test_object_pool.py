"""
Tests for object pooling system
"""
import pytest

from PyPong.core.object_pool import ObjectPool, PoolManager, get_pool_manager, reset_pool_manager


class DummyObject:
    """Dummy object for testing"""

    def __init__(self):
        self.value = 0

    def reset(self):
        self.value = 0


class TestObjectPool:
    """Test suite for ObjectPool"""

    def test_pool_creation(self):
        """Test creating an object pool"""
        pool = ObjectPool(lambda: DummyObject(), initial_size=5, max_size=10)

        stats = pool.get_stats()
        assert stats["available"] == 5
        assert stats["active"] == 0
        assert stats["created"] == 5

    def test_acquire_from_pool(self):
        """Test acquiring objects from pool"""
        pool = ObjectPool(lambda: DummyObject(), initial_size=5)

        obj = pool.acquire()
        assert obj is not None
        assert isinstance(obj, DummyObject)

        stats = pool.get_stats()
        assert stats["available"] == 4
        assert stats["active"] == 1

    def test_release_to_pool(self):
        """Test releasing objects back to pool"""
        pool = ObjectPool(lambda: DummyObject(), initial_size=5)

        obj = pool.acquire()
        pool.release(obj)

        stats = pool.get_stats()
        assert stats["available"] == 5
        assert stats["active"] == 0

    def test_pool_reuse(self):
        """Test that objects are reused"""
        pool = ObjectPool(lambda: DummyObject(), initial_size=2)

        obj1 = pool.acquire()
        obj1.value = 42
        pool.release(obj1)

        obj2 = pool.acquire()
        # Should be the same object
        assert obj2 is obj1

        stats = pool.get_stats()
        # reused=2: first acquire from available (reused=1), second acquire after release (reused=2)
        assert stats["reused"] == 2

    def test_reset_function(self):
        """Test reset function is called on reuse"""

        def reset_func(obj):
            obj.reset()

        pool = ObjectPool(lambda: DummyObject(), initial_size=2, reset_func=reset_func)

        obj1 = pool.acquire()
        obj1.value = 42
        pool.release(obj1)

        obj2 = pool.acquire()
        # Value should be reset
        assert obj2.value == 0

    def test_pool_expansion(self):
        """Test pool creates new objects when empty"""
        pool = ObjectPool(lambda: DummyObject(), initial_size=1, max_size=10)

        obj1 = pool.acquire()
        obj2 = pool.acquire()  # Should create new object

        stats = pool.get_stats()
        assert stats["created"] == 2
        assert stats["active"] == 2

    def test_max_size_limit(self):
        """Test pool respects max size"""
        pool = ObjectPool(lambda: DummyObject(), initial_size=2, max_size=3)

        # Acquire and release more than max_size
        for _ in range(5):
            obj = pool.acquire()
            pool.release(obj)

        stats = pool.get_stats()
        # Pool should not exceed max_size
        assert stats["available"] <= 3

    def test_release_all(self):
        """Test releasing all active objects"""
        pool = ObjectPool(lambda: DummyObject(), initial_size=5)

        obj1 = pool.acquire()
        obj2 = pool.acquire()
        obj3 = pool.acquire()

        pool.release_all()

        stats = pool.get_stats()
        assert stats["active"] == 0

    def test_clear_pool(self):
        """Test clearing pool"""
        pool = ObjectPool(lambda: DummyObject(), initial_size=5)

        obj = pool.acquire()
        pool.clear()

        assert len(pool) == 0

    def test_pool_statistics(self):
        """Test pool statistics tracking"""
        pool = ObjectPool(lambda: DummyObject(), initial_size=2)

        obj1 = pool.acquire()
        obj2 = pool.acquire()
        pool.release(obj1)
        obj3 = pool.acquire()  # Should reuse obj1

        stats = pool.get_stats()
        assert stats["acquired"] == 3
        assert stats["released"] == 1
        # reused=3: obj1 from available (1), obj2 from available (2), obj3 reused from released obj1 (3)
        assert stats["reused"] == 3
        assert stats["reuse_rate"] > 0


class TestPoolManager:
    """Test suite for PoolManager"""

    def setup_method(self):
        """Setup for each test"""
        reset_pool_manager()

    def test_create_pool(self):
        """Test creating a pool through manager"""
        manager = get_pool_manager()

        pool = manager.create_pool("test_pool", lambda: DummyObject(), initial_size=5)

        assert pool is not None
        assert manager.get_pool("test_pool") is pool

    def test_get_pool(self):
        """Test getting pool by name"""
        manager = get_pool_manager()

        pool1 = manager.create_pool("test_pool", lambda: DummyObject())
        pool2 = manager.get_pool("test_pool")

        assert pool1 is pool2

    def test_remove_pool(self):
        """Test removing a pool"""
        manager = get_pool_manager()

        manager.create_pool("test_pool", lambda: DummyObject())
        manager.remove_pool("test_pool")

        assert manager.get_pool("test_pool") is None

    def test_multiple_pools(self):
        """Test managing multiple pools"""
        manager = get_pool_manager()

        pool1 = manager.create_pool("pool1", lambda: DummyObject())
        pool2 = manager.create_pool("pool2", lambda: DummyObject())

        assert pool1 is not pool2
        assert manager.get_pool("pool1") is pool1
        assert manager.get_pool("pool2") is pool2

    def test_get_all_stats(self):
        """Test getting statistics for all pools"""
        manager = get_pool_manager()

        manager.create_pool("pool1", lambda: DummyObject(), initial_size=5)
        manager.create_pool("pool2", lambda: DummyObject(), initial_size=3)

        all_stats = manager.get_all_stats()

        assert "pool1" in all_stats
        assert "pool2" in all_stats
        assert all_stats["pool1"]["available"] == 5
        assert all_stats["pool2"]["available"] == 3

    def test_clear_all(self):
        """Test clearing all pools"""
        manager = get_pool_manager()

        manager.create_pool("pool1", lambda: DummyObject())
        manager.create_pool("pool2", lambda: DummyObject())

        manager.clear_all()

        assert len(manager._pools) == 0


@pytest.mark.performance
class TestPoolPerformance:
    """Performance tests for object pooling"""

    def test_pool_vs_new_objects(self):
        """Compare pool performance vs creating new objects"""
        import time

        # Test with pool
        pool = ObjectPool(lambda: DummyObject(), initial_size=100)

        start = time.perf_counter()
        for _ in range(1000):
            obj = pool.acquire()
            pool.release(obj)
        pool_time = time.perf_counter() - start

        # Test without pool
        start = time.perf_counter()
        for _ in range(1000):
            obj = DummyObject()
            del obj
        new_time = time.perf_counter() - start

        # Pool should be comparable or faster (allow some variance)
        print(f"Pool time: {pool_time:.4f}s, New time: {new_time:.4f}s")
        # Just verify pool is not orders of magnitude slower
        assert pool_time < new_time * 10, f"Pool ({pool_time:.4f}s) too slow vs new ({new_time:.4f}s)"
