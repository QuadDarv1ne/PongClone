"""
Visual effects: Particles, Trails, Screen Shake
"""
import math
import pygame
from random import randint, uniform
from typing import Optional, List, Tuple
from PyPong.core.config import (
    WHITE, WINDOW_WIDTH, WINDOW_HEIGHT, FONT_NAME,
    MAX_PARTICLES, PARTICLES_PER_HIT,
)

# Кэш поверхностей для частиц (оптимизация)
_particle_surfaces: dict = {}

def _get_particle_surface(size: int, color: tuple) -> pygame.Surface:
    """Получить закэшированную поверхность для частицы"""
    key = (size, color)
    if key not in _particle_surfaces:
        surf = pygame.Surface([size, size])
        surf.fill(color)
        _particle_surfaces[key] = surf
    return _particle_surfaces[key]


class ParticlePool:
    """
    Пул объектов для частиц.
    Предотвращает постоянное создание/удаление объектов.
    """
    
    def __init__(self, max_size: int = MAX_PARTICLES):
        self.max_size = max_size
        self.pool: List[Particle] = []
        self.active: List[Particle] = []
        
        # Предварительно создаём частицы
        for _ in range(max_size):
            particle = Particle(0, 0, WHITE, inactive=True)
            self.pool.append(particle)
    
    def emit(
        self, 
        x: int, 
        y: int, 
        color: Tuple[int, int, int], 
        count: int = PARTICLES_PER_HIT
    ) -> None:
        """Создать частицы в указанной позиции"""
        emitted = 0
        for particle in self.pool:
            if emitted >= count:
                break
            if not particle.active:
                particle.activate(x, y, color)
                self.active.append(particle)
                emitted += 1
    
    def update(self) -> None:
        """Обновить все активные частицы"""
        new_active: List[Particle] = []
        for particle in self.active:
            particle.update()
            if particle.active:
                new_active.append(particle)
        self.active = new_active
    
    def draw(self, surface: pygame.Surface) -> None:
        """Отрисовать все активные частицы"""
        for particle in self.active:
            surface.blit(particle.image, particle.rect)
    
    def clear(self) -> None:
        """Очистить все активные частицы"""
        for particle in self.active:
            particle.deactivate()
        self.active = []


class Particle(pygame.sprite.Sprite):
    """Частица для визуальных эффектов"""
    
    def __init__(
        self, 
        x: int = 0, 
        y: int = 0, 
        color: Tuple[int, int, int] = WHITE,
        inactive: bool = False
    ):
        super().__init__()
        self.active = not inactive
        self.size = randint(2, 5)
        self.image = _get_particle_surface(self.size, color)
        self.rect = self.image.get_rect(center=(x, y))
        
        angle = uniform(0, 360)
        speed = uniform(1, 4)
        rad = math.radians(angle)
        self.velocity_x = speed * math.cos(rad)
        self.velocity_y = speed * math.sin(rad)
        
        self.lifetime = randint(20, 40)
        self.age = 0
    
    def activate(self, x: int, y: int, color: Tuple[int, int, int]) -> None:
        """Активировать частицу"""
        self.active = True
        self.rect.center = (x, y)
        self.image.fill(color)
        
        angle = uniform(0, 360)
        speed = uniform(1, 4)
        rad = math.radians(angle)
        self.velocity_x = speed * math.cos(rad)
        self.velocity_y = speed * math.sin(rad)
        
        self.age = 0
        self.lifetime = randint(20, 40)
    
    def deactivate(self) -> None:
        """Деактивировать частицу"""
        self.active = False
        self.kill()

    def update(self):
        self.rect.x += self.velocity_x
        self.rect.y += self.velocity_y
        self.velocity_y += 0.2  # Gravity
        self.age += 1

        if self.age >= self.lifetime:
            self.kill()


# Кэш для trail
_trail_surface: Optional[pygame.Surface] = None

def _get_trail_surface(size: int) -> pygame.Surface:
    """Получить закэшированную поверхность для trail"""
    global _trail_surface
    if _trail_surface is None or _trail_surface.get_width() != size:
        _trail_surface = pygame.Surface([size, size])
        _trail_surface.fill(WHITE)
        _trail_surface.set_alpha(150)
    return _trail_surface


class Trail(pygame.sprite.Sprite):
    """Эффект шлейфа для мяча"""
    
    def __init__(self, x: int, y: int, size: int = 8):
        super().__init__()
        self.image = _get_trail_surface(size)
        self.rect = self.image.get_rect(center=(x, y))
        self.lifetime = 10
        self.age = 0

    def update(self):
        self.age += 1
        alpha = int(150 * (1 - self.age / self.lifetime))
        self.image.set_alpha(max(0, alpha))

        if self.age >= self.lifetime:
            self.kill()

class ScreenShake:
    """Эффект тряски экрана"""

    def __init__(self) -> None:
        self.offset_x = 0
        self.offset_y = 0
        self.intensity = 0
        self.duration = 0

    def start(self, intensity: int = 10, duration: int = 10) -> None:
        self.intensity = intensity
        self.duration = duration
    
    def update(self) -> None:
        if self.duration > 0:
            self.offset_x = randint(-self.intensity, self.intensity)
            self.offset_y = randint(-self.intensity, self.intensity)
            self.duration -= 1
            self.intensity = max(0, self.intensity - 1)
        else:
            self.offset_x = 0
            self.offset_y = 0
    
    def apply(self, surface: pygame.Surface, screen: pygame.Surface) -> None:
        screen.blit(surface, (self.offset_x, self.offset_y))


class GoalAnimation:
    """Анимация гола"""

    def __init__(self) -> None:
        self.active = False
        self.timer = 0
        self.duration = 60
        self.player: Optional[int] = None
        self.font = pygame.font.SysFont(FONT_NAME, 80)

    def start(self, player: int) -> None:
        self.active = True
        self.timer = 0
        self.player = player

    def update(self):
        if self.active:
            self.timer += 1
            if self.timer >= self.duration:
                self.active = False

    def draw(self, screen):
        if self.active:
            alpha = int(255 * (1 - self.timer / self.duration))
            text = self.font.render(f"GOAL! Player {self.player}", True, YELLOW)
            text.set_alpha(max(0, alpha))
            
            y_offset = -self.timer * 2
            rect = text.get_rect(center=(WINDOW_WIDTH // 2, WINDOW_HEIGHT // 2 + y_offset))
            screen.blit(text, rect)
