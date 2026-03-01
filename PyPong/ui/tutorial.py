"""
Interactive tutorial system
"""
import pygame
from typing import List, Optional, Callable
from dataclasses import dataclass
from PyPong.core.constants import Colors
from PyPong.core.logger import logger
from PyPong.ui.localization import t


@dataclass
class TutorialStep:
    """Single tutorial step"""
    id: str
    title: str
    description: str
    condition: Optional[Callable] = None
    highlight_area: Optional[pygame.Rect] = None
    arrow_to: Optional[tuple[int, int]] = None
    auto_advance: bool = False
    duration: int = 0  # Auto-advance after duration (ms)


class TutorialManager:
    """Manages interactive tutorial"""
    
    def __init__(self):
        self.active = False
        self.current_step = 0
        self.steps: List[TutorialStep] = []
        self.completed_steps: List[str] = []
        self.start_time = 0
        self.step_start_time = 0
        
        self.font = pygame.font.SysFont("Helvetica", 24)
        self.title_font = pygame.font.SysFont("Helvetica", 32, bold=True)
        
        self._create_tutorial_steps()
        logger.info("Tutorial manager initialized")
    
    def _create_tutorial_steps(self) -> None:
        """Create tutorial steps"""
        self.steps = [
            # Step 1: Welcome
            TutorialStep(
                id="welcome",
                title=t("tutorial.welcome"),
                description="Learn the basics of Pong in this quick tutorial.",
                auto_advance=True,
                duration=3000
            ),
            
            # Step 2: Objective
            TutorialStep(
                id="objective",
                title=t("tutorial.objective"),
                description="Score points by hitting the ball past your opponent's paddle.",
                auto_advance=True,
                duration=4000
            ),
            
            # Step 3: Controls
            TutorialStep(
                id="controls",
                title=t("tutorial.controls"),
                description="Press A to move up, Z to move down. Try moving your paddle!",
                condition=lambda: self._check_paddle_moved(),
                highlight_area=pygame.Rect(50, 310, 10, 100)
            ),
            
            # Step 4: Hit the ball
            TutorialStep(
                id="hit_ball",
                title="Hit the Ball",
                description="Now try to hit the ball with your paddle!",
                condition=lambda: self._check_ball_hit(),
                arrow_to=(512, 360)
            ),
            
            # Step 5: Scoring
            TutorialStep(
                id="scoring",
                title="Scoring",
                description="When the ball passes your opponent, you score a point!",
                condition=lambda: self._check_scored(),
            ),
            
            # Step 6: Power-ups
            TutorialStep(
                id="powerups",
                title=t("tutorial.powerups"),
                description="Collect glowing power-ups for special abilities!",
                condition=lambda: self._check_powerup_collected(),
            ),
            
            # Step 7: Combo
            TutorialStep(
                id="combo",
                title=t("tutorial.combo"),
                description="Hit the ball multiple times in a row for combo bonuses!",
                condition=lambda: self._check_combo(),
            ),
            
            # Step 8: Complete
            TutorialStep(
                id="complete",
                title=t("tutorial.complete"),
                description="You're ready to play! Press ENTER to start a real game.",
                auto_advance=False
            ),
        ]
    
    def start_tutorial(self) -> None:
        """Start tutorial"""
        self.active = True
        self.current_step = 0
        self.completed_steps = []
        self.start_time = pygame.time.get_ticks()
        self.step_start_time = self.start_time
        
        logger.info("Tutorial started")
    
    def stop_tutorial(self) -> None:
        """Stop tutorial"""
        self.active = False
        logger.info("Tutorial stopped")
    
    def update(self, game_state: dict) -> bool:
        """
        Update tutorial state
        Returns True if tutorial is complete
        """
        if not self.active or self.current_step >= len(self.steps):
            return True
        
        step = self.steps[self.current_step]
        current_time = pygame.time.get_ticks()
        
        # Check auto-advance
        if step.auto_advance and step.duration > 0:
            if current_time - self.step_start_time >= step.duration:
                self._advance_step()
                return False
        
        # Check condition
        if step.condition:
            try:
                if step.condition():
                    self._advance_step()
            except Exception as e:
                logger.error(f"Tutorial condition error: {e}")
        
        return self.current_step >= len(self.steps)
    
    def _advance_step(self) -> None:
        """Advance to next step"""
        if self.current_step < len(self.steps):
            step = self.steps[self.current_step]
            self.completed_steps.append(step.id)
            logger.debug(f"Tutorial step completed: {step.id}")
        
        self.current_step += 1
        self.step_start_time = pygame.time.get_ticks()
        
        if self.current_step >= len(self.steps):
            logger.info("Tutorial completed")
    
    def skip_tutorial(self) -> None:
        """Skip to end of tutorial"""
        self.current_step = len(self.steps)
        logger.info("Tutorial skipped")
    
    def draw(self, screen: pygame.Surface) -> None:
        """Draw tutorial overlay"""
        if not self.active or self.current_step >= len(self.steps):
            return
        
        step = self.steps[self.current_step]
        
        # Semi-transparent overlay
        overlay = pygame.Surface(screen.get_size())
        overlay.set_alpha(180)
        overlay.fill((0, 0, 0))
        screen.blit(overlay, (0, 0))
        
        # Highlight area
        if step.highlight_area:
            # Cut out highlight area
            highlight_surf = pygame.Surface(step.highlight_area.size)
            highlight_surf.fill((255, 255, 255))
            highlight_surf.set_alpha(100)
            screen.blit(highlight_surf, step.highlight_area)
            
            # Draw border
            pygame.draw.rect(screen, Colors.YELLOW.to_tuple(), step.highlight_area, 3)
        
        # Arrow
        if step.arrow_to:
            self._draw_arrow(screen, step.arrow_to)
        
        # Tutorial box
        box_width = 600
        box_height = 200
        box_x = (screen.get_width() - box_width) // 2
        box_y = screen.get_height() - box_height - 50
        
        box_rect = pygame.Rect(box_x, box_y, box_width, box_height)
        pygame.draw.rect(screen, (40, 40, 40), box_rect)
        pygame.draw.rect(screen, Colors.YELLOW.to_tuple(), box_rect, 3)
        
        # Title
        title = self.title_font.render(step.title, True, Colors.YELLOW.to_tuple())
        title_rect = title.get_rect(centerx=box_rect.centerx, top=box_y + 20)
        screen.blit(title, title_rect)
        
        # Description (word wrap)
        self._draw_wrapped_text(
            screen, step.description,
            box_x + 30, box_y + 70,
            box_width - 60, Colors.WHITE.to_tuple()
        )
        
        # Progress
        progress_text = f"Step {self.current_step + 1}/{len(self.steps)}"
        progress = self.font.render(progress_text, True, Colors.LIGHT_BLUE.to_tuple())
        screen.blit(progress, (box_x + 20, box_y + box_height - 40))
        
        # Skip hint
        skip_text = "Press ESC to skip"
        skip = self.font.render(skip_text, True, Colors.GRAY.to_tuple())
        skip_rect = skip.get_rect(right=box_x + box_width - 20, bottom=box_y + box_height - 20)
        screen.blit(skip, skip_rect)
    
    def _draw_arrow(self, screen: pygame.Surface, target: tuple[int, int]) -> None:
        """Draw arrow pointing to target"""
        # Animated arrow
        offset = int(10 * abs(pygame.math.Vector2(0, 1).rotate(pygame.time.get_ticks() * 0.1).y))
        
        arrow_points = [
            (target[0], target[1] - 50 - offset),
            (target[0] - 15, target[1] - 70 - offset),
            (target[0] + 15, target[1] - 70 - offset),
        ]
        
        pygame.draw.polygon(screen, Colors.YELLOW.to_tuple(), arrow_points)
    
    def _draw_wrapped_text(
        self,
        screen: pygame.Surface,
        text: str,
        x: int,
        y: int,
        max_width: int,
        color: tuple[int, int, int]
    ) -> None:
        """Draw text with word wrapping"""
        words = text.split(' ')
        lines = []
        current_line = []
        
        for word in words:
            test_line = ' '.join(current_line + [word])
            test_surface = self.font.render(test_line, True, color)
            
            if test_surface.get_width() <= max_width:
                current_line.append(word)
            else:
                if current_line:
                    lines.append(' '.join(current_line))
                current_line = [word]
        
        if current_line:
            lines.append(' '.join(current_line))
        
        # Draw lines
        for i, line in enumerate(lines):
            line_surface = self.font.render(line, True, color)
            screen.blit(line_surface, (x, y + i * 30))
    
    # Condition checkers (to be implemented with game state)
    def _check_paddle_moved(self) -> bool:
        """Check if paddle has moved"""
        # This would check game state
        return False
    
    def _check_ball_hit(self) -> bool:
        """Check if ball was hit"""
        return False
    
    def _check_scored(self) -> bool:
        """Check if player scored"""
        return False
    
    def _check_powerup_collected(self) -> bool:
        """Check if power-up was collected"""
        return False
    
    def _check_combo(self) -> bool:
        """Check if combo was achieved"""
        return False
