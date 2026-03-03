"""Mini-games and variations of Pong"""
import math
from random import choice, randint
from typing import Any, List, Optional

import pygame

from PyPong.core.config import (
    FONT_NAME,
    GREEN,
    LIGHT_BLUE,
    RED,
    WHITE,
    WINDOW_HEIGHT,
    WINDOW_WIDTH,
    YELLOW,
)
from PyPong.core.entities import Ball, Paddle


class MiniGame:
    """Base class for mini-games"""

    def __init__(self, name: str, description: str) -> None:
        self.name = name
        self.description = description
        self.active = False
        self.score = 0
        self.time_limit: Optional[int] = None
        self.start_time: Optional[int] = None

    def start(self) -> None:
        """Start the mini-game"""
        self.active = True
        self.score = 0
        self.start_time = pygame.time.get_ticks()

    def update(self, *args):
        """Update mini-game state"""
        raise NotImplementedError

    def draw(self, screen):
        """Draw mini-game specific elements"""
        raise NotImplementedError

    def is_complete(self):
        """Check if mini-game is complete"""
        if self.time_limit and self.start_time:
            elapsed = (pygame.time.get_ticks() - self.start_time) / 1000
            return elapsed >= self.time_limit
        return False

    def get_remaining_time(self):
        """Get remaining time in seconds"""
        if self.time_limit and self.start_time:
            elapsed = (pygame.time.get_ticks() - self.start_time) / 1000
            return max(0, self.time_limit - elapsed)
        return 0


class TargetPractice(MiniGame):
    """Hit targets that appear on screen"""

    def __init__(self) -> None:
        super().__init__("Target Practice", "Hit as many targets as possible")
        self.targets: List[dict] = []
        self.time_limit = 60  # 60 seconds
        self.target_spawn_interval = 2000
        self.last_spawn = 0

    def start(self) -> None:
        super().start()
        self.targets = []
        self.spawn_target()

    def spawn_target(self):
        """Spawn a new target"""
        target = {
            "rect": pygame.Rect(randint(100, WINDOW_WIDTH - 100), randint(100, WINDOW_HEIGHT - 100), 30, 30),
            "color": choice([RED, GREEN, YELLOW, LIGHT_BLUE]),
            "points": randint(1, 5),
        }
        self.targets.append(target)

    def update(self, ball):
        """Update targets and check collisions"""
        current_time = pygame.time.get_ticks()

        # Spawn new targets
        if current_time - self.last_spawn > self.target_spawn_interval:
            self.spawn_target()
            self.last_spawn = current_time

        # Check collisions
        for target in self.targets[:]:
            if ball.rect.colliderect(target["rect"]):
                self.score += target["points"]
                self.targets.remove(target)
                ball.velocity_x *= -1
                ball.velocity_y *= -1

    def draw(self, screen):
        """Draw targets"""
        for target in self.targets:
            pygame.draw.rect(screen, target["color"], target["rect"])
            pygame.draw.rect(screen, WHITE, target["rect"], 2)


class BreakoutMode(MiniGame):
    """Breakout-style game with bricks"""

    def __init__(self) -> None:
        super().__init__("Breakout", "Break all the bricks")
        self.bricks: List[dict] = []
        self.rows = 5
        self.cols = 10
        self.brick_width = 80
        self.brick_height = 30

    def start(self) -> None:
        super().start()
        self.create_bricks()

    def create_bricks(self):
        """Create brick layout"""
        self.bricks = []
        colors = [RED, (255, 165, 0), YELLOW, GREEN, LIGHT_BLUE]

        offset_x = (WINDOW_WIDTH - (self.cols * self.brick_width)) // 2
        offset_y = 50

        for row in range(self.rows):
            for col in range(self.cols):
                brick = {
                    "rect": pygame.Rect(
                        offset_x + col * self.brick_width,
                        offset_y + row * self.brick_height,
                        self.brick_width - 2,
                        self.brick_height - 2,
                    ),
                    "color": colors[row % len(colors)],
                    "hits": 1,
                }
                self.bricks.append(brick)

    def update(self, ball):
        """Update bricks and check collisions"""
        for brick in self.bricks[:]:
            if ball.rect.colliderect(brick["rect"]):
                brick["hits"] -= 1
                if brick["hits"] <= 0:
                    self.bricks.remove(brick)
                    self.score += 10

                # Bounce ball
                ball.velocity_y *= -1

    def draw(self, screen):
        """Draw bricks"""
        for brick in self.bricks:
            pygame.draw.rect(screen, brick["color"], brick["rect"])
            pygame.draw.rect(screen, WHITE, brick["rect"], 1)

    def is_complete(self):
        """Complete when all bricks are destroyed"""
        return len(self.bricks) == 0


class SurvivalMode(MiniGame):
    """Survive as long as possible with increasing difficulty"""

    def __init__(self) -> None:
        super().__init__("Survival", "Survive as long as possible")
        self.difficulty_increase_interval = 10000  # Every 10 seconds
        self.last_increase = 0
        self.current_speed_multiplier = 1.0

    def start(self) -> None:
        super().start()
        self.current_speed_multiplier = 1.0
        self.last_increase = pygame.time.get_ticks()

    def update(self, ball):
        """Increase difficulty over time"""
        current_time = pygame.time.get_ticks()

        if current_time - self.last_increase > self.difficulty_increase_interval:
            self.current_speed_multiplier += 0.1
            ball.speed *= 1.1
            self.last_increase = current_time
            self.score += 100

    def draw(self, screen):
        """Draw difficulty indicator"""
        font = pygame.font.SysFont(FONT_NAME, 24)
        text = font.render(f"Speed: {self.current_speed_multiplier:.1f}x", True, WHITE)
        screen.blit(text, (WINDOW_WIDTH - 150, 50))


class KeepUpMode(MiniGame):
    """Keep the ball in the air without letting it touch the bottom"""

    def __init__(self) -> None:
        super().__init__("Keep Up", "Don't let the ball touch the bottom")
        self.time_limit = 60
        self.touches = 0

    def start(self) -> None:
        super().start()
        self.touches = 0

    def update(self, ball, paddle):
        """Count paddle touches"""
        if ball.rect.colliderect(paddle.rect):
            self.touches += 1
            self.score = self.touches

    def check_fail(self, ball):
        """Check if ball touched bottom"""
        return ball.rect.bottom >= WINDOW_HEIGHT

    def draw(self, screen):
        """Draw touch counter"""
        font = pygame.font.SysFont(FONT_NAME, 36)
        text = font.render(f"Touches: {self.touches}", True, WHITE)
        screen.blit(text, (WINDOW_WIDTH // 2 - 80, 50))


class PrecisionMode(MiniGame):
    """Hit specific zones on the paddle for bonus points"""

    def __init__(self) -> None:
        super().__init__("Precision", "Hit the sweet spot for bonus points")
        self.time_limit = 60
        self.perfect_hits = 0
        self.good_hits = 0
        self.normal_hits = 0

    def start(self) -> None:
        super().start()
        self.perfect_hits = 0
        self.good_hits = 0
        self.normal_hits = 0

    def check_hit_quality(self, ball, paddle):
        """Check hit quality based on position"""
        hit_pos = abs(ball.rect.centery - paddle.rect.centery)
        paddle_height = paddle.height

        if hit_pos < paddle_height * 0.15:  # Center 30%
            self.perfect_hits += 1
            self.score += 10
            return "PERFECT!"
        elif hit_pos < paddle_height * 0.35:  # Middle 70%
            self.good_hits += 1
            self.score += 5
            return "GOOD"
        else:
            self.normal_hits += 1
            self.score += 1
            return "OK"

    def draw(self, screen):
        """Draw hit statistics"""
        font = pygame.font.SysFont(FONT_NAME, 24)
        y = 50

        stats = [f"Perfect: {self.perfect_hits}", f"Good: {self.good_hits}", f"Normal: {self.normal_hits}"]

        for stat in stats:
            text = font.render(stat, True, WHITE)
            screen.blit(text, (20, y))
            y += 30


class MiniGameManager:
    """Manages mini-games"""

    def __init__(self) -> None:
        self.minigames = {
            "target_practice": TargetPractice(),
            "breakout": BreakoutMode(),
            "survival": SurvivalMode(),
            "keep_up": KeepUpMode(),
            "precision": PrecisionMode(),
        }
        self.current_minigame: Optional[MiniGame] = None

    def start_minigame(self, name: str) -> bool:
        """Start a specific mini-game"""
        if name in self.minigames:
            self.current_minigame = self.minigames[name]
            self.current_minigame.start()
            return True
        return False

    def stop_minigame(self):
        """Stop current mini-game"""
        if self.current_minigame:
            score = self.current_minigame.score
            self.current_minigame.active = False
            self.current_minigame = None
            return score
        return 0

    def update(self, *args):
        """Update current mini-game"""
        if self.current_minigame and self.current_minigame.active:
            self.current_minigame.update(*args)

    def draw(self, screen):
        """Draw current mini-game"""
        if self.current_minigame and self.current_minigame.active:
            self.current_minigame.draw(screen)

    def is_active(self):
        """Check if a mini-game is active"""
        return self.current_minigame is not None and self.current_minigame.active

    def get_current_minigame(self):
        """Get current mini-game"""
        return self.current_minigame
