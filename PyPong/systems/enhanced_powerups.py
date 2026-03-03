"""
Enhanced power-up system with new types
"""
from dataclasses import dataclass
from random import choice, randint
from typing import Dict, List, Optional, Tuple

import pygame

from PyPong.core.constants import Balance, Colors, PowerUpType
from PyPong.core.logger import logger


@dataclass
class PowerUpConfig:
    """Power-up configuration"""

    type: PowerUpType
    color: Tuple[int, int, int]
    duration: int
    name: str
    description: str
    icon: str


class PowerUpRegistry:
    """Registry of all power-up types"""

    CONFIGS: Dict[PowerUpType, PowerUpConfig] = {
        PowerUpType.SPEED_BOOST: PowerUpConfig(
            PowerUpType.SPEED_BOOST,
            Colors.GREEN.to_tuple(),
            Balance.POWERUP_DURATIONS[PowerUpType.SPEED_BOOST],
            "Speed Boost",
            "Increase paddle speed",
            "⚡",
        ),
        PowerUpType.LARGE_PADDLE: PowerUpConfig(
            PowerUpType.LARGE_PADDLE,
            Colors.YELLOW.to_tuple(),
            Balance.POWERUP_DURATIONS[PowerUpType.LARGE_PADDLE],
            "Large Paddle",
            "Increase paddle size",
            "📏",
        ),
        PowerUpType.SLOW_BALL: PowerUpConfig(
            PowerUpType.SLOW_BALL,
            Colors.LIGHT_BLUE.to_tuple(),
            Balance.POWERUP_DURATIONS[PowerUpType.SLOW_BALL],
            "Slow Ball",
            "Slow down the ball",
            "🐌",
        ),
        PowerUpType.MULTI_BALL: PowerUpConfig(
            PowerUpType.MULTI_BALL, Colors.RED.to_tuple(), 0, "Multi Ball", "Spawn multiple balls", "🎱"
        ),
        PowerUpType.SHRINK_OPPONENT: PowerUpConfig(
            PowerUpType.SHRINK_OPPONENT,
            Colors.ORANGE.to_tuple(),
            Balance.POWERUP_DURATIONS[PowerUpType.LARGE_PADDLE],
            "Shrink Opponent",
            "Shrink opponent's paddle",
            "📉",
        ),
        PowerUpType.INVISIBLE_BALL: PowerUpConfig(
            PowerUpType.INVISIBLE_BALL,
            Colors.PURPLE.to_tuple(),
            5000,
            "Invisible Ball",
            "Make ball invisible to opponent",
            "👻",
        ),
        PowerUpType.REVERSE_CONTROLS: PowerUpConfig(
            PowerUpType.REVERSE_CONTROLS,
            Colors.CYAN.to_tuple(),
            5000,
            "Reverse Controls",
            "Reverse opponent's controls",
            "🔄",
        ),
        PowerUpType.SHIELD: PowerUpConfig(
            PowerUpType.SHIELD,
            (100, 200, 255),
            Balance.POWERUP_DURATIONS[PowerUpType.SHIELD],
            "Shield",
            "Protect from one miss",
            "🛡️",
        ),
        PowerUpType.FREEZE: PowerUpConfig(
            PowerUpType.FREEZE,
            (150, 200, 255),
            Balance.POWERUP_DURATIONS[PowerUpType.FREEZE],
            "Freeze",
            "Freeze opponent's paddle",
            "❄️",
        ),
        PowerUpType.MAGNET: PowerUpConfig(
            PowerUpType.MAGNET,
            (255, 100, 200),
            Balance.POWERUP_DURATIONS[PowerUpType.MAGNET],
            "Magnet",
            "Ball attracted to paddle",
            "🧲",
        ),
    }

    @classmethod
    def get_config(cls, powerup_type: PowerUpType) -> PowerUpConfig:
        """Get power-up configuration"""
        return cls.CONFIGS.get(powerup_type)

    @classmethod
    def get_random_type(cls) -> PowerUpType:
        """Get random power-up type"""
        return choice(list(cls.CONFIGS.keys()))


class EnhancedPowerUp(pygame.sprite.Sprite):
    """Enhanced power-up with new types"""

    def __init__(self, powerup_type: Optional[PowerUpType] = None):
        super().__init__()

        # Select type
        self.type = powerup_type or PowerUpRegistry.get_random_type()
        self.config = PowerUpRegistry.get_config(self.type)

        # Visual
        self.image = pygame.Surface([25, 25])
        self.image.fill(self.config.color)
        self.rect = self.image.get_rect()

        # Position
        self.rect.center = (randint(200, 824), randint(100, 620))  # WINDOW_WIDTH - 200  # WINDOW_HEIGHT - 100

        # State
        self.active = False
        self.start_time = 0
        self.affected_paddle = None
        self.affected_opponent = None

        # Animation
        self.pulse_timer = 0
        self.original_size = 25

        logger.debug(f"PowerUp spawned: {self.config.name} at {self.rect.center}")

    def update(self) -> None:
        """Update power-up state"""
        if not self.active:
            # Pulse animation
            self.pulse_timer += 0.1
            size = int(self.original_size + 3 * abs(pygame.math.Vector2(0, 1).rotate(self.pulse_timer * 10).y))
            self.image = pygame.Surface([size, size])
            self.image.fill(self.config.color)
            center = self.rect.center
            self.rect = self.image.get_rect(center=center)
        else:
            # Check expiration
            if self.config.duration > 0:
                elapsed = pygame.time.get_ticks() - self.start_time
                if elapsed > self.config.duration:
                    self.deactivate()

    def activate(self, paddle, opponent=None) -> None:
        """Activate power-up"""
        self.active = True
        self.start_time = pygame.time.get_ticks()
        self.affected_paddle = paddle
        self.affected_opponent = opponent

        logger.info(f"PowerUp activated: {self.config.name}")

        # Apply immediate effects
        if self.type == PowerUpType.SPEED_BOOST:
            paddle.speed *= 1.5

        elif self.type == PowerUpType.LARGE_PADDLE:
            paddle.resize(int(paddle.height * 1.5))

        elif self.type == PowerUpType.SHRINK_OPPONENT and opponent:
            opponent.resize(int(opponent.height * 0.6))

        elif self.type == PowerUpType.FREEZE and opponent:
            opponent.frozen = True

        elif self.type == PowerUpType.SHIELD:
            paddle.has_shield = True

    def deactivate(self) -> None:
        """Deactivate power-up"""
        if not self.active:
            return

        logger.debug(f"PowerUp deactivated: {self.config.name}")

        # Revert effects
        if self.affected_paddle:
            if self.type == PowerUpType.SPEED_BOOST:
                self.affected_paddle.speed /= 1.5

            elif self.type == PowerUpType.LARGE_PADDLE:
                self.affected_paddle.reset_size()

            elif self.type == PowerUpType.SHIELD:
                self.affected_paddle.has_shield = False

        if self.affected_opponent:
            if self.type == PowerUpType.SHRINK_OPPONENT:
                self.affected_opponent.reset_size()

            elif self.type == PowerUpType.FREEZE:
                self.affected_opponent.frozen = False

        self.kill()

    def get_remaining_time(self) -> float:
        """Get remaining time in seconds"""
        if not self.active or self.config.duration == 0:
            return 0

        elapsed = pygame.time.get_ticks() - self.start_time
        remaining = max(0, self.config.duration - elapsed)
        return remaining / 1000


class ComboSystem:
    """Tracks combos and multipliers"""

    def __init__(self) -> None:
        self.combo_count = 0
        self.last_hit_time = 0
        self.combo_timeout = Balance.COMBO_TIMEOUT_MS
        self.multiplier = 1.0
        self.max_combo = 0

        logger.debug("Combo system initialized")

    def register_hit(self) -> Tuple[int, float]:
        """Register a paddle hit"""
        current_time = pygame.time.get_ticks()

        # Check if combo continues
        if current_time - self.last_hit_time < self.combo_timeout:
            self.combo_count += 1
        else:
            self.combo_count = 1

        self.last_hit_time = current_time

        # Update multiplier
        self.multiplier = 1.0 + (self.combo_count - 1) * 0.1
        self.multiplier = min(self.multiplier, 3.0)  # Max 3x

        # Track max combo
        if self.combo_count > self.max_combo:
            self.max_combo = self.combo_count
            logger.info(f"New max combo: {self.max_combo}")

        return self.combo_count, self.multiplier

    def reset(self) -> None:
        """Reset combo"""
        if self.combo_count > 0:
            logger.debug(f"Combo broken at {self.combo_count}")
        self.combo_count = 0
        self.multiplier = 1.0

    def get_bonus_points(self, base_points: int) -> int:
        """Calculate bonus points from combo"""
        return int(base_points * self.multiplier)

    def is_active(self) -> bool:
        """Check if combo is active"""
        if self.combo_count == 0:
            return False

        current_time = pygame.time.get_ticks()
        return current_time - self.last_hit_time < self.combo_timeout

    def get_remaining_time(self) -> float:
        """Get remaining combo time in seconds"""
        if not self.is_active():
            return 0

        current_time = pygame.time.get_ticks()
        elapsed = current_time - self.last_hit_time
        remaining = max(0, self.combo_timeout - elapsed)
        return remaining / 1000
