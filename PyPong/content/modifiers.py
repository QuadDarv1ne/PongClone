"""Game modifiers that change physics and gameplay"""
import math
from random import choice, uniform
from typing import Any, Dict, List, Optional, Tuple

import pygame

from PyPong.core.entities import Ball, Paddle


class GameModifier:
    """Base class for game modifiers"""

    def __init__(self, name: str, description: str) -> None:
        self.name = name
        self.description = description
        self.active = True

    def apply_to_ball(self, ball: Ball) -> None:
        """Apply modifier effect to ball"""
        raise NotImplementedError

    def apply_to_paddle(self, paddle: Paddle) -> None:
        """Apply modifier effect to paddle"""
        raise NotImplementedError

    def update(self) -> None:
        """Update modifier state"""
        pass


class GravityModifier(GameModifier):
    """Adds gravity effect to ball"""

    def __init__(self, strength: float = 0.2) -> None:
        super().__init__("Gravity", f"Ball affected by gravity (strength: {strength})")
        self.strength = strength

    def apply_to_ball(self, ball: Ball) -> None:
        if self.active:
            ball.velocity_y += self.strength


class WindModifier(GameModifier):
    """Adds wind effect that pushes ball horizontally"""

    def __init__(self, strength: float = 0.15, variable: bool = True) -> None:
        super().__init__("Wind", "Wind pushes the ball")
        self.base_strength = strength
        self.strength = strength
        self.variable = variable
        self.direction = 1
        self.change_timer = 0
        self.change_interval = 3000

    def apply_to_ball(self, ball: Ball) -> None:
        if self.active:
            ball.velocity_x += self.strength * self.direction

    def update(self) -> None:
        if self.variable:
            self.change_timer += 16
            if self.change_timer >= self.change_interval:
                self.direction *= -1
                self.change_timer = 0


class LowGravityModifier(GameModifier):
    """Reduces gravity effect"""

    def __init__(self) -> None:
        super().__init__("Low Gravity", "Ball falls slower")

    def apply_to_ball(self, ball: Ball) -> None:
        if self.active:
            ball.velocity_y *= 0.95


class SpeedBoostModifier(GameModifier):
    """Increases ball speed over time"""

    def __init__(self, boost_rate: float = 0.01) -> None:
        super().__init__("Speed Boost", "Ball gradually speeds up")
        self.boost_rate = boost_rate

    def apply_to_ball(self, ball: Ball) -> None:
        if self.active:
            current_speed = math.sqrt(ball.velocity_x**2 + ball.velocity_y**2)
            if current_speed < 20:
                ball.velocity_x *= 1 + self.boost_rate
                ball.velocity_y *= 1 + self.boost_rate


class ReverseControlsModifier(GameModifier):
    """Reverses player controls"""

    def __init__(self) -> None:
        super().__init__("Reverse Controls", "Controls are inverted")
        self.affected_paddle: Optional[Paddle] = None

    def apply_to_paddle(self, paddle: Paddle) -> None:
        self.affected_paddle = paddle

    def is_reversed(self, paddle: Paddle) -> bool:
        return self.active and self.affected_paddle == paddle


class ModifierManager:
    """Manages active game modifiers"""

    def __init__(self) -> None:
        self.modifiers: List[GameModifier] = []
        self.active_modifiers: Dict[str, GameModifier] = {}

    def add_modifier(self, modifier: GameModifier) -> None:
        """Add a modifier"""
        self.modifiers.append(modifier)
        self.active_modifiers[modifier.name] = modifier

    def remove_modifier(self, name: str) -> bool:
        """Remove a modifier by name"""
        if name in self.active_modifiers:
            del self.active_modifiers[name]
            self.modifiers = [m for m in self.modifiers if m.name != name]
            return True
        return False

    def apply_to_ball(self, ball: Ball) -> None:
        """Apply all active modifiers to ball"""
        for modifier in self.active_modifiers.values():
            if modifier.active:
                modifier.apply_to_ball(ball)

    def apply_to_paddle(self, paddle: Paddle) -> None:
        """Apply all active modifiers to paddle"""
        for modifier in self.active_modifiers.values():
            if modifier.active:
                modifier.apply_to_paddle(paddle)

    def update(self) -> None:
        """Update all active modifiers"""
        for modifier in self.active_modifiers.values():
            modifier.update()

    def get_active_modifiers(self) -> List[str]:
        """Get list of active modifier names"""
        return [m.name for m in self.active_modifiers.values() if m.active]

    def clear(self) -> None:
        """Clear all modifiers"""
        self.modifiers = []
        self.active_modifiers = {}
