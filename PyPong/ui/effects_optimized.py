"""
Optimized visual effects using object pooling
"""
import math
from random import randint, uniform
from typing import List, Tuple

import pygame

from PyPong.core.config import MAX_PARTICLES, PARTICLES_PER_HIT, WHITE
from PyPong.core.logger import logger
from PyPong.core.object_pool import ObjectPool, get_pool_manager

# Surface cache for particles
_particle_surfaces: dict = {}


def _get_particle_surface(size: int, color: tuple) -> pygame.Surface:
    """Get cached particle surface"""
    key = (size, color)
    if key not in _particle_surfaces:
        surf = pygame.Surface([size, size])
        surf.fill(color)
        surf.set_colorkey((0, 0, 0))  # Transparency
        _particle_surfaces[key] = surf
    return _particle_surfaces[key]


class OptimizedParticle:
    """Lightweight particle for pooling"""

    def __init__(self):
        self.x = 0.0
        self.y = 0.0
        self.velocity_x = 0.0
        self.velocity_y = 0.0
        self.size = 3
        self.color = WHITE
        self.lifetime = 30
        self.age = 0
        self.active = False

    def activate(self, x: float, y: float, color: Tuple[int, int, int]) -> None:
        """Activate particle with new parameters"""
        self.x = x
        self.y = y
        self.color = color
        self.size = randint(2, 5)
        self.lifetime = randint(20, 40)
        self.age = 0
        self.active = True

        # Random velocity
        angle = uniform(0, 360)
        speed = uniform(1, 4)
        rad = math.radians(angle)
        self.velocity_x = speed * math.cos(rad)
        self.velocity_y = speed * math.sin(rad)

    def deactivate(self) -> None:
        """Deactivate particle"""
        self.active = False

    def update(self) -> None:
        """Update particle position and lifetime"""
        if not self.active:
            return

        self.x += self.velocity_x
        self.y += self.velocity_y
        self.velocity_y += 0.2  # Gravity
        self.age += 1

        if self.age >= self.lifetime:
            self.deactivate()

    def draw(self, surface: pygame.Surface) -> None:
        """Draw particle"""
        if not self.active:
            return

        # Fade out based on age
        alpha = int(255 * (1 - self.age / self.lifetime))
        color = tuple(min(255, max(0, c * alpha // 255)) for c in self.color)

        surf = _get_particle_surface(self.size, color)
        surface.blit(surf, (int(self.x), int(self.y)))


class OptimizedParticlePool:
    """
    Optimized particle pool using generic ObjectPool.
    Much more efficient than creating/destroying particles.
    """

    def __init__(self, max_size: int = MAX_PARTICLES):
        self.max_size = max_size

        # Create object pool
        pool_manager = get_pool_manager()
        self.pool = pool_manager.create_pool(
            name="particles",
            factory=lambda: OptimizedParticle(),
            initial_size=max_size // 2,
            max_size=max_size,
            reset_func=lambda p: p.deactivate(),
        )

        self.active_particles: List[OptimizedParticle] = []
        logger.debug(f"OptimizedParticlePool initialized with max_size={max_size}")

    def emit(
        self,
        x: float,
        y: float,
        color: Tuple[int, int, int],
        count: int = PARTICLES_PER_HIT,
    ) -> None:
        """Emit particles at position"""
        for _ in range(count):
            if len(self.active_particles) >= self.max_size:
                # Pool is full, remove oldest particle
                oldest = self.active_particles.pop(0)
                self.pool.release(oldest)

            particle = self.pool.acquire()
            particle.activate(x, y, color)
            self.active_particles.append(particle)

    def update(self) -> None:
        """Update all active particles"""
        # Update and remove dead particles
        alive = []
        for particle in self.active_particles:
            particle.update()
            if particle.active:
                alive.append(particle)
            else:
                self.pool.release(particle)

        self.active_particles = alive

    def draw(self, surface: pygame.Surface) -> None:
        """Draw all active particles"""
        for particle in self.active_particles:
            particle.draw(surface)

    def clear(self) -> None:
        """Clear all particles"""
        for particle in self.active_particles:
            self.pool.release(particle)
        self.active_particles.clear()

    def get_stats(self) -> dict:
        """Get particle pool statistics"""
        return {
            "active": len(self.active_particles),
            "pool_stats": self.pool.get_stats(),
        }


class OptimizedTrail(pygame.sprite.Sprite):
    """Optimized trail effect"""

    def __init__(self, x: int, y: int, color: Tuple[int, int, int], size: int = 5):
        super().__init__()
        self.lifetime = 10
        self.age = 0
        self.color = color
        self.size = size

        self.image = pygame.Surface([size, size])
        self.image.fill(color)
        self.rect = self.image.get_rect(center=(x, y))

    def update(self) -> None:
        """Update trail"""
        self.age += 1
        if self.age >= self.lifetime:
            self.kill()
        else:
            # Fade out
            alpha = int(255 * (1 - self.age / self.lifetime))
            self.image.set_alpha(alpha)


class TrailPool:
    """Pool for trail effects"""

    def __init__(self, max_size: int = 20):
        self.max_size = max_size
        self.trails = pygame.sprite.Group()

    def add_trail(self, x: int, y: int, color: Tuple[int, int, int], size: int = 5) -> None:
        """Add a trail at position"""
        if len(self.trails) >= self.max_size:
            # Remove oldest trail
            oldest = min(self.trails.sprites(), key=lambda t: t.age)
            oldest.kill()

        trail = OptimizedTrail(x, y, color, size)
        self.trails.add(trail)

    def update(self) -> None:
        """Update all trails"""
        self.trails.update()

    def draw(self, surface: pygame.Surface) -> None:
        """Draw all trails"""
        self.trails.draw(surface)

    def clear(self) -> None:
        """Clear all trails"""
        self.trails.empty()

    def sprites(self) -> List[pygame.sprite.Sprite]:
        """Get list of trail sprites (for compatibility)"""
        return self.trails.sprites()


class BatchRenderer:
    """
    Batch renderer for drawing multiple similar objects efficiently.
    Groups draw calls to reduce overhead.
    """

    def __init__(self):
        self._batches: dict = {}

    def add_to_batch(self, key: str, surface: pygame.Surface, pos: Tuple[int, int]) -> None:
        """Add a draw call to a batch"""
        if key not in self._batches:
            self._batches[key] = []
        self._batches[key].append((surface, pos))

    def render_batches(self, target: pygame.Surface) -> None:
        """Render all batches"""
        for batch in self._batches.values():
            for surface, pos in batch:
                target.blit(surface, pos)
        self._batches.clear()

    def clear(self) -> None:
        """Clear all batches"""
        self._batches.clear()
