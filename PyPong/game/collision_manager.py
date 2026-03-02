"""
Collision manager for game physics
"""
from typing import Optional, Tuple
import pygame

from PyPong.core.entities import Paddle, Ball, PowerUp
from PyPong.core.config import SHAKE_INTENSITY_NORMAL, SHAKE_INTENSITY_GOAL


class CollisionManager:
    """
    Управляет коллизиями между игровыми объектами.
    """
    
    def __init__(self) -> None:
        self.last_collision_time = 0
    
    def check_paddle_collision(
        self, 
        ball: Ball, 
        paddle: Paddle
    ) -> bool:
        """
        Проверить коллизию мяча с ракеткой.
        
        Returns:
            bool: True если была коллизия
        """
        if not pygame.sprite.collide_rect(ball, paddle):
            return False
        
        # Проверка направления удара
        if paddle.player_number == 1 and ball.velocity_x > 0:
            return False
        if paddle.player_number == 2 and ball.velocity_x < 0:
            return False
        
        return True
    
    def handle_paddle_collision(
        self, 
        ball: Ball, 
        paddle: Paddle
    ) -> Tuple[bool, int]:
        """
        Обработать коллизию мяча с ракеткой.
        
        Args:
            ball: Мяч
            paddle: Ракетка
            
        Returns:
            tuple: (should_play_sound, player_number)
        """
        ball.bounce_paddle(paddle)
        return (True, paddle.player_number)
    
    def check_powerup_collision(
        self,
        powerup: PowerUp,
        paddle: Paddle
    ) -> bool:
        """
        Проверить коллизию power-up с ракеткой.

        Returns:
            bool: True если была коллизия
        """
        # Power-up активен только если ещё не подобран
        if powerup.active or powerup.affected_paddle is not None:
            return False
        return pygame.sprite.collide_rect(powerup, paddle)
    
    def check_ball_powerup_collision(
        self, 
        powerup: PowerUp, 
        ball: Ball
    ) -> bool:
        """
        Проверить коллизию power-up с мячом (для slow_ball).
        
        Returns:
            bool: True если была коллизия
        """
        if powerup.active and powerup.type == "slow_ball":
            return pygame.sprite.collide_rect(powerup, ball)
        return False
    
    def check_score(
        self, 
        ball: Ball, 
        window_width: int
    ) -> Optional[int]:
        """
        Проверить забитый гол.
        
        Args:
            ball: Мяч
            window_width: Ширина окна
            
        Returns:
            int или None: Номер игрока, получившего очко, или None
        """
        if ball.is_out_left():
            return 2  # Игрок 2 забил
        elif ball.is_out_right():
            return 1  # Игрок 1 забил
        return None
    
    def get_shake_intensity(self, is_goal: bool) -> Tuple[int, int]:
        """
        Получить интенсивность тряски экрана.
        
        Args:
            is_goal: True если это гол
            
        Returns:
            tuple: (intensity_x, intensity_y)
        """
        if is_goal:
            return SHAKE_INTENSITY_GOAL
        return SHAKE_INTENSITY_NORMAL
