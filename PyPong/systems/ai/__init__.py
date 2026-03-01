"""
AI system for opponent paddles
"""
import random
from abc import ABC, abstractmethod
from typing import Optional, List, Dict, Type

import pygame

from PyPong.core.entities import Paddle, Ball


class AIBase(ABC):
    """Base class for AI controllers"""
    
    def __init__(self, paddle: Paddle, difficulty: str = "Medium") -> None:
        self.paddle: Paddle = paddle
        self.difficulty: str = difficulty
        self.reaction_delay: float = 0
        self.prediction_error: float = 0
        
    @abstractmethod
    def get_target_y(self, ball_x: float, ball_y: float,
                     ball_vx: float, ball_vy: float) -> float:
        """Get target Y position for paddle"""
        raise NotImplementedError

    def update(self, ball: Ball) -> Optional[bool]:
        """
        Update AI decision.
        Returns True if should move up, False if down, None if stay.
        """
        if not self.paddle.is_ai:
            return None
            
        target_y = self.get_target_y(
            ball.rect.centerx,
            ball.rect.centery,
            ball.velocity_x,
            ball.velocity_y
        )
        
        # Add prediction error based on difficulty
        error = self._get_error()
        target_y += random.uniform(-error, error)
        
        current_y = self.paddle.rect.centery
        diff = target_y - current_y
        
        # Dead zone to prevent jittering
        if abs(diff) < self.paddle.speed // 2:
            return None
            
        return diff > 0
    
    def _get_error(self) -> float:
        """Get prediction error based on difficulty"""
        errors: Dict[str, float] = {
            "Easy": 50,
            "Medium": 25,
            "Hard": 10,
            "Expert": 3,
            "Insane": 0,
        }
        return errors.get(self.difficulty, 20)


class SimpleAI(AIBase):
    """Simple AI that just follows ball Y position"""
    
    def get_target_y(self, ball_x: float, ball_y: float,
                     ball_vx: float, ball_vy: float) -> float:
        # Only track when ball is moving toward us
        if self.paddle.player_number == 1 and ball_vx < 0:
            return ball_y
        if self.paddle.player_number == 2 and ball_vx > 0:
            return ball_y
        return float(self.paddle.rect.centery)


class PredictiveAI(AIBase):
    """AI that predicts ball trajectory"""
    
    def get_target_y(self, ball_x: float, ball_y: float,
                     ball_vx: float, ball_vy: float) -> float:
        # Ball moving toward opponent
        moving_toward = (self.paddle.player_number == 1 and ball_vx < 0 or
                        self.paddle.player_number == 2 and ball_vx > 0)
        
        if not moving_toward:
            return self.paddle.rect.centery
        
        # Predict where ball will be at paddle
        target_x = 50 if self.paddle.player_number == 2 else 974
        
        # Calculate time to reach paddle
        if ball_vx == 0:
            return ball_y
            
        dx = target_x - ball_x
        time = dx / ball_vx
        
        # Predict Y position
        predicted_y = ball_y + ball_vy * time
        
        # Account for wall bounces
        from PyPong.core.config import WINDOW_HEIGHT, BALL_SIZE
        bounces = int(predicted_y // WINDOW_HEIGHT)
        if bounces % 2 == 1:
            predicted_y = WINDOW_HEIGHT - (predicted_y % WINDOW_HEIGHT)
        
        return max(BALL_SIZE, min(WINDOW_HEIGHT - BALL_SIZE, predicted_y))


class AdaptiveAI(PredictiveAI):
    """AI that learns from player behavior"""
    
    def __init__(self, paddle: Paddle, difficulty: str = "Medium") -> None:
        super().__init__(paddle, difficulty)
        self.player_weak_side: Optional[str] = None
        self.player_pattern: List[float] = []
        self.pattern_window: int = 5
        
    def get_target_y(self, ball_x: float, ball_y: float,
                     ball_vx: float, ball_vy: float) -> float:
        # Record player shot pattern
        if self.paddle.player_number == 1 and ball_vx > 0:
            self._record_pattern(ball_y)
        
        target_y = super().get_target_y(ball_x, ball_y, ball_vx, ball_vy)
        
        # Adjust based on learned pattern
        if self.player_pattern and len(self.player_pattern) >= 3:
            avg_y = sum(self.player_pattern) / len(self.player_pattern)
            # Blend prediction with learned behavior
            blend: Dict[str, float] = {"Easy": 0.8, "Medium": 0.5, "Hard": 0.2, "Expert": 0.1, "Insane": 0}
            factor = blend.get(self.difficulty, 0.3)
            target_y = target_y * (1 - factor) + avg_y * factor
        
        return target_y
    
    def _record_pattern(self, hit_y: float) -> None:
        """Record where player hits the ball"""
        self.player_pattern.append(hit_y)
        if len(self.player_pattern) > self.pattern_window:
            self.player_pattern.pop(0)


class AggressiveAI(PredictiveAI):
    """AI that tries to hit ball at optimal angles"""
    
    def __init__(self, paddle: Paddle, difficulty: str = "Medium") -> None:
        super().__init__(paddle, difficulty)
        self.preferred_angles: List[int] = [-30, 0, 30]  # Degrees
        
    def get_target_y(self, ball_x: float, ball_y: float,
                     ball_vx: float, ball_vy: float) -> float:
        target_y = super().get_target_y(ball_x, ball_y, ball_vx, ball_vy)
        
        # Adjust to aim for corners
        if self.difficulty in ("Hard", "Expert", "Insane"):
            # Add slight offset to aim for corners
            offset = random.choice([-30, 30])
            target_y += offset
        
        return target_y


class DefensiveAI(PredictiveAI):
    """AI focused on defense, rarely attacks"""
    
    def get_target_y(self, ball_x: float, ball_y: float,
                     ball_vx: float, ball_vy: float) -> float:
        target_y = super().get_target_y(ball_x, ball_y, ball_vx, ball_vy)
        
        # Stay closer to center when not needed
        from PyPong.core.config import WINDOW_HEIGHT
        center = WINDOW_HEIGHT // 2
        
        moving_toward = (self.paddle.player_number == 1 and ball_vx < 0 or
                        self.paddle.player_number == 2 and ball_vx > 0)
        
        if not moving_toward:
            # Return to defensive position
            return float(center)
        
        return target_y


# Factory function
def create_ai(paddle: Paddle, difficulty: str = "Medium", ai_type: str = "predictive") -> AIBase:
    """
    Create AI controller based on type and difficulty
    
    Args:
        paddle: Paddle sprite
        difficulty: "Easy", "Medium", "Hard", "Expert", "Insane"
        ai_type: "simple", "predictive", "adaptive", "aggressive", "defensive"
    
    Returns:
        AIBase instance
    """
    ai_classes: Dict[str, Type[AIBase]] = {
        "simple": SimpleAI,
        "predictive": PredictiveAI,
        "adaptive": AdaptiveAI,
        "aggressive": AggressiveAI,
        "defensive": DefensiveAI,
    }
    
    ai_class = ai_classes.get(ai_type, PredictiveAI)
    return ai_class(paddle, difficulty)
