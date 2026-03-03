"""
Optimized entities with caching and performance improvements
"""
import math
from functools import lru_cache
from random import choice, randint
from typing import Any, Dict, Optional, Tuple

import pygame

from PyPong.core.config import (
    BALL_INITIAL_SPEED,
    BALL_SIZE,
    BALL_SPEED_INCREASE,
    DIFFICULTY_LEVELS,
    GREEN,
    LIGHT_BLUE,
    MAX_BALL_SPEED,
    PADDLE_HEIGHT,
    PADDLE_OFFSET,
    PADDLE_SPEED,
    PADDLE_WIDTH,
    POWERUP_DURATION,
    RED,
    WHITE,
    WINDOW_HEIGHT,
    WINDOW_WIDTH,
    YELLOW,
)

# Pre-create commonly used surfaces for better performance
_PADDLE_SURFACES: Dict[Tuple[int, Tuple[int, int, int]], pygame.Surface] = {}
_BALL_SURFACE: Optional[pygame.Surface] = None


def _get_paddle_surface(width: int, height: int, color: Tuple[int, int, int]) -> pygame.Surface:
    """Get cached paddle surface or create new one"""
    key = (height, color)
    if key not in _PADDLE_SURFACES:
        surf = pygame.Surface((width, height))
        surf.fill(color)
        _PADDLE_SURFACES[key] = surf
    return _PADDLE_SURFACES[key]


def _get_ball_surface() -> pygame.Surface:
    """Get cached ball surface"""
    global _BALL_SURFACE
    if _BALL_SURFACE is None:
        _BALL_SURFACE = pygame.Surface((BALL_SIZE, BALL_SIZE))
        _BALL_SURFACE.fill(WHITE)
    return _BALL_SURFACE


class Paddle(pygame.sprite.Sprite):
    """Optimized Paddle class with caching"""

    __slots__ = ("player_number", "is_ai", "color", "width", "height", "speed", "image", "rect", "original_height")

    def __init__(self, player_number: int, is_ai: bool = False, color: Tuple[int, int, int] = WHITE):
        super().__init__()
        self.player_number = player_number
        self.is_ai = is_ai
        self.color = color
        self.width = PADDLE_WIDTH
        self.height = PADDLE_HEIGHT
        self.speed = PADDLE_SPEED if not is_ai else DIFFICULTY_LEVELS["Medium"]["ai_speed"]

        # Use cached surface
        self.image = _get_paddle_surface(self.width, self.height, color)
        self.rect = self.image.get_rect()
        self.reset_position()
        self.original_height = PADDLE_HEIGHT

    def reset_position(self) -> None:
        if self.player_number == 1:
            self.rect.centerx = PADDLE_OFFSET
        else:
            self.rect.centerx = WINDOW_WIDTH - PADDLE_OFFSET
        self.rect.centery = WINDOW_HEIGHT // 2

    def move(self, up: bool, down: bool, ball_y: Optional[float] = None) -> None:
        if self.is_ai and ball_y is not None:
            diff = self.rect.centery - ball_y
            if abs(diff) > 5:
                if diff > 0:
                    self.rect.y -= self.speed
                else:
                    self.rect.y += self.speed
        else:
            if up and self.rect.top > 5:
                self.rect.y -= self.speed
            elif down and self.rect.bottom < WINDOW_HEIGHT - 5:
                self.rect.y += self.speed

        self.rect.clamp_ip(pygame.Rect(0, 0, WINDOW_WIDTH, WINDOW_HEIGHT))

    @lru_cache(maxsize=128)
    def predict_ball_position(
        self, ball_x: float, ball_y: float, ball_velocity_x: float, ball_velocity_y: float
    ) -> float:
        """Predict ball Y position when it reaches paddle (cached)"""
        if self.player_number == 1 and ball_velocity_x < 0:
            return ball_y
        if self.player_number == 2 and ball_velocity_x > 0:
            return ball_y

        sim_x, sim_y = ball_x, ball_y
        sim_vy = ball_velocity_y
        target_x = self.rect.centerx

        # Optimized simulation (fewer iterations)
        step = abs(ball_velocity_x)
        while True:
            if (self.player_number == 2 and sim_x >= target_x) or (self.player_number == 1 and sim_x <= target_x):
                return sim_y

            sim_x += ball_velocity_x
            sim_y += sim_vy

            if sim_y <= 0 or sim_y >= WINDOW_HEIGHT:
                sim_vy = -sim_vy
                sim_y = max(0, min(WINDOW_HEIGHT, sim_y))

            if abs(sim_x - target_x) < step:
                break

        return sim_y

    def resize(self, new_height: int) -> None:
        center = self.rect.center
        self.height = new_height
        self.image = _get_paddle_surface(self.width, new_height, self.color)
        self.rect = self.image.get_rect(center=center)

    def reset_size(self) -> None:
        self.resize(self.original_height)

    def set_speed(self, speed: float) -> None:
        self.speed = speed


class Ball(pygame.sprite.Sprite):
    """Optimized Ball class with caching"""

    __slots__ = ("image", "rect", "velocity_x", "velocity_y", "speed")

    def __init__(self) -> None:
        super().__init__()
        self.image = _get_ball_surface()
        self.rect = self.image.get_rect()
        self.velocity_x = 0.0
        self.velocity_y = 0.0
        self.speed = BALL_INITIAL_SPEED
        self.reset_ball()

    def reset_ball(self) -> None:
        self.rect.center = (WINDOW_WIDTH // 2, WINDOW_HEIGHT // 2)
        self.speed = BALL_INITIAL_SPEED

        angle = choice([45, 135, 225, 315])
        rad = math.radians(angle)
        self.velocity_x = self.speed * math.cos(rad)
        self.velocity_y = self.speed * math.sin(rad)

    def set_speed(self, speed: float) -> None:
        current_angle = math.atan2(self.velocity_y, self.velocity_x)
        self.speed = speed
        self.velocity_x = self.speed * math.cos(current_angle)
        self.velocity_y = self.speed * math.sin(current_angle)

    def move(self) -> None:
        self.rect.x += int(self.velocity_x)
        self.rect.y += int(self.velocity_y)

    def bounce_wall(self) -> None:
        if self.rect.top <= 0 or self.rect.bottom >= WINDOW_HEIGHT:
            self.velocity_y *= -1
            self.rect.clamp_ip(pygame.Rect(0, 0, WINDOW_WIDTH, WINDOW_HEIGHT))

    def bounce_paddle(self, paddle: Paddle) -> None:
        hit_pos = (self.rect.centery - paddle.rect.centery) / (paddle.height / 2)
        hit_pos = max(-1, min(1, hit_pos))

        max_angle = 60
        angle = hit_pos * max_angle
        direction = 1 if paddle.player_number == 1 else -1

        rad = math.radians(angle)
        self.velocity_x = direction * self.speed * math.cos(rad)
        self.velocity_y = self.speed * math.sin(rad)
        self.increase_speed()

    def increase_speed(self) -> None:
        if self.speed < MAX_BALL_SPEED:
            self.speed = min(self.speed * BALL_SPEED_INCREASE, MAX_BALL_SPEED)
            current_angle = math.atan2(self.velocity_y, self.velocity_x)
            self.velocity_x = self.speed * math.cos(current_angle)
            self.velocity_y = self.speed * math.sin(current_angle)

    def is_out_left(self) -> bool:
        return self.rect.right < 0

    def is_out_right(self) -> bool:
        return self.rect.left > WINDOW_WIDTH


class PowerUp(pygame.sprite.Sprite):
    """Optimized PowerUp with cached surfaces"""

    TYPES: Dict[str, Dict[str, Any]] = {
        "speed_boost": {"color": GREEN, "duration": POWERUP_DURATION},
        "large_paddle": {"color": YELLOW, "duration": POWERUP_DURATION},
        "slow_ball": {"color": LIGHT_BLUE, "duration": POWERUP_DURATION},
        "multi_ball": {"color": RED, "duration": 0},
        "shrink_opponent": {"color": (255, 165, 0), "duration": POWERUP_DURATION},
    }

    # Cache surfaces by type
    _SURFACES: Dict[str, pygame.Surface] = {}

    @classmethod
    def _get_surface(cls, ptype: str) -> pygame.Surface:
        if ptype not in cls._SURFACES:
            surf = pygame.Surface((20, 20))
            surf.fill(cls.TYPES[ptype]["color"])
            cls._SURFACES[ptype] = surf
        return cls._SURFACES[ptype]

    def __init__(self) -> None:
        super().__init__()
        self.type = choice(list(self.TYPES.keys()))
        self.image = self._get_surface(self.type)
        self.rect = self.image.get_rect()
        self.rect.center = (randint(WINDOW_WIDTH // 4, 3 * WINDOW_WIDTH // 4), randint(50, WINDOW_HEIGHT - 50))
        self.active = False
        self.start_time = 0
        self.affected_paddle: Optional[Paddle] = None

    def activate(self, paddle: Paddle) -> None:
        self.active = True
        self.start_time = pygame.time.get_ticks()
        self.affected_paddle = paddle

        if self.type == "speed_boost":
            paddle.set_speed(paddle.speed * 1.5)
        elif self.type == "large_paddle":
            paddle.resize(150)

    def deactivate(self) -> None:
        self.active = False
        if self.affected_paddle:
            if self.type == "speed_boost":
                self.affected_paddle.set_speed(PADDLE_SPEED)
            elif self.type == "large_paddle":
                self.affected_paddle.reset_size()
        self.kill()

    def update(self) -> None:
        if self.active:
            elapsed = pygame.time.get_ticks() - self.start_time
            if elapsed > self.TYPES[self.type]["duration"]:
                self.deactivate()

    def apply_to_ball(self, ball: Ball) -> None:
        if self.type == "slow_ball":
            new_speed = max(BALL_INITIAL_SPEED, ball.speed * 0.5)
            ball.set_speed(new_speed)
