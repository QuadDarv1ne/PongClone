"""Collision manager for game physics"""
from typing import List, Optional, Tuple

import pygame

from PyPong.core.config import SHAKE_INTENSITY_GOAL, SHAKE_INTENSITY_NORMAL
from PyPong.core.entities import Ball, Paddle, PowerUp


class CollisionManager:
    """Управляет коллизиями между игровыми объектами."""

    def __init__(self) -> None:
        self.last_collision_time: float = 0

    def check_paddle_collision(self, ball: Ball, paddle: Paddle) -> bool:
        """Проверить коллизию мяча с ракеткой."""
        if not pygame.sprite.collide_rect(ball, paddle):
            return False
        if paddle.player_number == 1 and ball.velocity_x > 0:
            return False
        if paddle.player_number == 2 and ball.velocity_x < 0:
            return False
        return True

    def handle_paddle_collision(self, ball: Ball, paddle: Paddle) -> Tuple[bool, int]:
        """Обработать коллизию мяча с ракеткой."""
        ball.bounce_paddle(paddle)
        return True, paddle.player_number

    def check_powerup_collision(self, powerup: PowerUp, paddle: Paddle) -> bool:
        """Проверить коллизию power-up с ракеткой."""
        return not (powerup.active or powerup.affected_paddle is not None) and pygame.sprite.collide_rect(
            powerup, paddle
        )

    def check_ball_powerup_collision(self, powerup: PowerUp, ball: Ball) -> bool:
        """Проверить коллизию power-up с мячом (для slow_ball)."""
        return powerup.active and powerup.type == "slow_ball" and pygame.sprite.collide_rect(powerup, ball)

    def check_score(self, ball: Ball, window_width: int) -> Optional[int]:
        """Проверить забитый гол."""
        if ball.is_out_left():
            return 2
        elif ball.is_out_right():
            return 1
        return None

    def get_shake_intensity(self, is_goal: bool) -> Tuple[int, int]:
        """Получить интенсивность тряски экрана."""
        return SHAKE_INTENSITY_GOAL if is_goal else SHAKE_INTENSITY_NORMAL

    def check_multi_ball_collisions(
        self, balls: List[Ball], paddle: Paddle
    ) -> List[Tuple[Ball, bool]]:
        """Проверить коллизии нескольких мячей с ракеткой."""
        collisions = []
        for ball in balls:
            is_collision = self.check_paddle_collision(ball, paddle)
            collisions.append((ball, is_collision))
        return collisions
