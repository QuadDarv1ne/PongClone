"""
Enhanced AI with trajectory prediction
"""
import pygame
import math
from typing import Optional, Tuple, List
from PyPong.core.constants import Difficulty, Balance
from PyPong.core.logger import logger


class TrajectoryPredictor:
    """Predicts ball trajectory"""
    
    def __init__(self, window_width: int = 1024, window_height: int = 720):
        self.window_width = window_width
        self.window_height = window_height
    
    def predict_impact_point(
        self,
        ball_pos: Tuple[float, float],
        ball_velocity: Tuple[float, float],
        paddle_x: float,
        max_bounces: int = 3
    ) -> Optional[float]:
        """
        Predict where ball will hit paddle's x position
        Returns predicted y coordinate or None
        """
        x, y = ball_pos
        vx, vy = ball_velocity
        
        # If ball moving away, return None
        if (paddle_x < self.window_width // 2 and vx > 0) or \
           (paddle_x > self.window_width // 2 and vx < 0):
            return None
        
        bounces = 0
        
        while bounces < max_bounces:
            # Calculate time to reach paddle x
            if vx == 0:
                return None
            
            t = (paddle_x - x) / vx
            
            if t < 0:
                return None
            
            # Calculate y position at that time
            predicted_y = y + vy * t
            
            # Check for wall bounces
            if predicted_y < 0:
                # Bounce off top
                y = 0
                vy = abs(vy)
                bounces += 1
            elif predicted_y > self.window_height:
                # Bounce off bottom
                y = self.window_height
                vy = -abs(vy)
                bounces += 1
            else:
                # No bounce needed
                return max(0, min(self.window_height, predicted_y))
        
        return None
    
    def get_trajectory_points(
        self,
        ball_pos: Tuple[float, float],
        ball_velocity: Tuple[float, float],
        steps: int = 50
    ) -> List[Tuple[int, int]]:
        """Get list of points along trajectory for visualization"""
        points = []
        x, y = ball_pos
        vx, vy = ball_velocity
        
        for _ in range(steps):
            points.append((int(x), int(y)))
            
            x += vx
            y += vy
            
            # Bounce off walls
            if y < 0 or y > self.window_height:
                vy *= -1
                y = max(0, min(self.window_height, y))
            
            # Stop if ball goes off screen horizontally
            if x < 0 or x > self.window_width:
                break
        
        return points


class EnhancedAI:
    """Enhanced AI with difficulty levels and prediction"""
    
    def __init__(
        self,
        difficulty: Difficulty = Difficulty.MEDIUM,
        window_width: int = 1024,
        window_height: int = 720
    ):
        self.difficulty = difficulty
        self.predictor = TrajectoryPredictor(window_width, window_height)
        self.reaction_delay = Balance.AI_REACTION_DELAYS[difficulty]
        self.last_decision_time = 0
        self.target_y: Optional[float] = None
        self.error_margin = self._get_error_margin()
        
        logger.info(f"Enhanced AI initialized: {difficulty.value}")
    
    def _get_error_margin(self) -> float:
        """Get error margin based on difficulty"""
        margins = {
            Difficulty.EASY: 50,
            Difficulty.MEDIUM: 30,
            Difficulty.HARD: 15,
            Difficulty.EXPERT: 5,
            Difficulty.INSANE: 0,
        }
        return margins.get(self.difficulty, 30)
    
    def _add_human_error(self, target: float) -> float:
        """Add human-like error to target"""
        if self.error_margin == 0:
            return target
        
        import random
        error = random.uniform(-self.error_margin, self.error_margin)
        return target + error
    
    def decide_move(
        self,
        paddle,
        ball,
        current_time: int
    ) -> Tuple[bool, bool]:
        """
        Decide paddle movement
        Returns (move_up, move_down)
        """
        # Check reaction delay
        if current_time - self.last_decision_time < self.reaction_delay:
            # Continue previous decision
            if self.target_y is not None:
                return self._move_to_target(paddle)
            return (False, False)
        
        self.last_decision_time = current_time
        
        # Predict ball trajectory
        predicted_y = self.predictor.predict_impact_point(
            (ball.rect.centerx, ball.rect.centery),
            (ball.velocity_x, ball.velocity_y),
            paddle.rect.centerx
        )
        
        if predicted_y is not None:
            # Add human-like error
            self.target_y = self._add_human_error(predicted_y)
        else:
            # Fallback: move to ball's current y
            self.target_y = ball.rect.centery
        
        return self._move_to_target(paddle)
    
    def _move_to_target(self, paddle) -> Tuple[bool, bool]:
        """Move paddle towards target"""
        if self.target_y is None:
            return (False, False)
        
        diff = self.target_y - paddle.rect.centery
        threshold = 5  # Dead zone
        
        if abs(diff) < threshold:
            return (False, False)
        
        if diff < 0:
            return (True, False)  # Move up
        else:
            return (False, True)  # Move down
    
    def set_difficulty(self, difficulty: Difficulty) -> None:
        """Change AI difficulty"""
        self.difficulty = difficulty
        self.reaction_delay = Balance.AI_REACTION_DELAYS[difficulty]
        self.error_margin = self._get_error_margin()
        logger.info(f"AI difficulty changed to: {difficulty.value}")
    
    def visualize_prediction(
        self,
        screen: pygame.Surface,
        ball,
        paddle,
        color: Tuple[int, int, int] = (255, 255, 0)
    ) -> None:
        """Draw prediction visualization (debug)"""
        if self.target_y is not None:
            # Draw target point
            pygame.draw.circle(
                screen, color,
                (int(paddle.rect.centerx), int(self.target_y)),
                5
            )
        
        # Draw trajectory
        points = self.predictor.get_trajectory_points(
            (ball.rect.centerx, ball.rect.centery),
            (ball.velocity_x, ball.velocity_y),
            steps=30
        )
        
        if len(points) > 1:
            pygame.draw.lines(screen, color, False, points, 1)


class AIPersonality:
    """AI personality traits"""
    
    def __init__(
        self,
        name: str,
        aggression: float = 0.5,
        accuracy: float = 0.5,
        reaction_speed: float = 0.5
    ):
        self.name = name
        self.aggression = aggression  # 0-1: How much AI tries to score vs defend
        self.accuracy = accuracy  # 0-1: Prediction accuracy
        self.reaction_speed = reaction_speed  # 0-1: How fast AI reacts
        
        logger.debug(f"AI personality created: {name}")
    
    def apply_to_ai(self, ai: EnhancedAI) -> None:
        """Apply personality to AI"""
        # Adjust error margin based on accuracy
        ai.error_margin *= (1 - self.accuracy)
        
        # Adjust reaction delay based on reaction speed
        ai.reaction_delay = int(ai.reaction_delay * (1 - self.reaction_speed))


# Predefined personalities
class AIPersonalities:
    DEFENSIVE = AIPersonality("Defensive", aggression=0.3, accuracy=0.7, reaction_speed=0.6)
    BALANCED = AIPersonality("Balanced", aggression=0.5, accuracy=0.5, reaction_speed=0.5)
    AGGRESSIVE = AIPersonality("Aggressive", aggression=0.8, accuracy=0.6, reaction_speed=0.7)
    PERFECT = AIPersonality("Perfect", aggression=0.5, accuracy=1.0, reaction_speed=1.0)
