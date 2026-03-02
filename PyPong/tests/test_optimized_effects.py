"""
Tests for optimized effects system
"""
import pytest
import pygame
from PyPong.ui.effects_optimized import (
    OptimizedParticle,
    OptimizedParticlePool,
    TrailPool,
    BatchRenderer,
)
from PyPong.core.object_pool import reset_pool_manager


class TestOptimizedParticle:
    """Test suite for OptimizedParticle"""
    
    def test_particle_creation(self):
        """Test creating a particle"""
        particle = OptimizedParticle()
        assert not particle.active
    
    def test_particle_activation(self):
        """Test activating a particle"""
        particle = OptimizedParticle()
        particle.activate(100, 100, (255, 0, 0))
        
        assert particle.active
        assert particle.x == 100
        assert particle.y == 100
        assert particle.color == (255, 0, 0)
    
    def test_particle_deactivation(self):
        """Test deactivating a particle"""
        particle = OptimizedParticle()
        particle.activate(100, 100, (255, 0, 0))
        particle.deactivate()
        
        assert not particle.active
    
    def test_particle_update(self):
        """Test particle update"""
        particle = OptimizedParticle()
        particle.activate(100, 100, (255, 0, 0))
        
        initial_x = particle.x
        initial_y = particle.y
        
        particle.update()
        
        # Position should change
        assert particle.x != initial_x or particle.y != initial_y
        assert particle.age == 1
    
    def test_particle_lifetime(self):
        """Test particle dies after lifetime"""
        particle = OptimizedParticle()
        particle.activate(100, 100, (255, 0, 0))
        particle.lifetime = 5
        
        # Update past lifetime
        for _ in range(10):
            particle.update()
        
        assert not particle.active


class TestOptimizedParticlePool:
    """Test suite for OptimizedParticlePool"""
    
    def setup_method(self):
        """Setup for each test"""
        reset_pool_manager()
        pygame.init()
    
    def teardown_method(self):
        """Cleanup after each test"""
        pygame.quit()
    
    def test_pool_creation(self):
        """Test creating particle pool"""
        pool = OptimizedParticlePool(max_size=50)
        assert pool.max_size == 50
        assert len(pool.active_particles) == 0
    
    def test_emit_particles(self):
        """Test emitting particles"""
        pool = OptimizedParticlePool(max_size=50)
        pool.emit(100, 100, (255, 0, 0), count=5)
        
        assert len(pool.active_particles) == 5
    
    def test_update_particles(self):
        """Test updating particles"""
        pool = OptimizedParticlePool(max_size=50)
        pool.emit(100, 100, (255, 0, 0), count=3)
        
        pool.update()
        
        # Particles should still be active after one update
        assert len(pool.active_particles) > 0
    
    def test_particle_cleanup(self):
        """Test dead particles are removed"""
        pool = OptimizedParticlePool(max_size=50)
        pool.emit(100, 100, (255, 0, 0), count=3)
        
        # Set short lifetime
        for particle in pool.active_particles:
            particle.lifetime = 1
        
        # Update past lifetime
        for _ in range(5):
            pool.update()
        
        # All particles should be dead
        assert len(pool.active_particles) == 0
    
    def test_max_particles(self):
        """Test pool respects max size"""
        pool = OptimizedParticlePool(max_size=10)
        
        # Emit more than max
        pool.emit(100, 100, (255, 0, 0), count=20)
        
        # Should not exceed max
        assert len(pool.active_particles) <= 10
    
    def test_clear_particles(self):
        """Test clearing all particles"""
        pool = OptimizedParticlePool(max_size=50)
        pool.emit(100, 100, (255, 0, 0), count=10)
        
        pool.clear()
        
        assert len(pool.active_particles) == 0
    
    def test_pool_statistics(self):
        """Test getting pool statistics"""
        pool = OptimizedParticlePool(max_size=50)
        pool.emit(100, 100, (255, 0, 0), count=5)
        
        stats = pool.get_stats()
        
        assert 'active' in stats
        assert 'pool_stats' in stats
        assert stats['active'] == 5


class TestTrailPool:
    """Test suite for TrailPool"""
    
    def setup_method(self):
        """Setup for each test"""
        pygame.init()
    
    def teardown_method(self):
        """Cleanup after each test"""
        pygame.quit()
    
    def test_trail_creation(self):
        """Test creating trail pool"""
        pool = TrailPool(max_size=20)
        assert pool.max_size == 20
    
    def test_add_trail(self):
        """Test adding trails"""
        pool = TrailPool(max_size=20)
        pool.add_trail(100, 100, (255, 255, 255))
        
        assert len(pool.trails) == 1
    
    def test_max_trails(self):
        """Test pool respects max trails"""
        pool = TrailPool(max_size=5)
        
        # Add more than max
        for i in range(10):
            pool.add_trail(i * 10, 100, (255, 255, 255))
        
        # Should not exceed max
        assert len(pool.trails) <= 5
    
    def test_trail_update(self):
        """Test updating trails"""
        pool = TrailPool(max_size=20)
        pool.add_trail(100, 100, (255, 255, 255))
        
        pool.update()
        
        # Trail should still exist after one update
        assert len(pool.trails) > 0
    
    def test_trail_lifetime(self):
        """Test trails die after lifetime"""
        pool = TrailPool(max_size=20)
        pool.add_trail(100, 100, (255, 255, 255))
        
        # Update past lifetime
        for _ in range(20):
            pool.update()
        
        # Trail should be gone
        assert len(pool.trails) == 0
    
    def test_clear_trails(self):
        """Test clearing all trails"""
        pool = TrailPool(max_size=20)
        pool.add_trail(100, 100, (255, 255, 255))
        pool.add_trail(200, 200, (255, 255, 255))
        
        pool.clear()
        
        assert len(pool.trails) == 0


class TestBatchRenderer:
    """Test suite for BatchRenderer"""
    
    def setup_method(self):
        """Setup for each test"""
        pygame.init()
        self.renderer = BatchRenderer()
    
    def teardown_method(self):
        """Cleanup after each test"""
        pygame.quit()
    
    def test_add_to_batch(self):
        """Test adding items to batch"""
        surface = pygame.Surface((10, 10))
        
        self.renderer.add_to_batch('test', surface, (0, 0))
        
        assert 'test' in self.renderer._batches
        assert len(self.renderer._batches['test']) == 1
    
    def test_multiple_batches(self):
        """Test multiple batches"""
        surface = pygame.Surface((10, 10))
        
        self.renderer.add_to_batch('batch1', surface, (0, 0))
        self.renderer.add_to_batch('batch2', surface, (10, 10))
        
        assert len(self.renderer._batches) == 2
    
    def test_clear_batches(self):
        """Test clearing batches"""
        surface = pygame.Surface((10, 10))
        
        self.renderer.add_to_batch('test', surface, (0, 0))
        self.renderer.clear()
        
        assert len(self.renderer._batches) == 0
