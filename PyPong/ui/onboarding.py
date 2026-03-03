"""
Enhanced onboarding and tutorial system
"""
from dataclasses import dataclass
from enum import Enum, auto
from typing import Any, Callable, Dict, List, Optional, Tuple

import pygame

from PyPong.core.logger import logger


class OnboardingStepType(Enum):
    """Types of onboarding steps"""

    INFO = auto()  # Just show information
    INTERACTIVE = auto()  # Wait for user action
    HIGHLIGHT = auto()  # Highlight UI element
    TOOLTIP = auto()  # Show tooltip
    ANIMATION = auto()  # Play animation


@dataclass
class OnboardingStep:
    """Single onboarding step"""

    id: str
    type: OnboardingStepType
    title: str
    description: str

    # Optional fields
    condition: Optional[Callable[[], bool]] = None
    highlight_rect: Optional[pygame.Rect] = None
    arrow_position: Optional[Tuple[int, int]] = None
    auto_advance: bool = False
    duration_ms: int = 3000
    skip_allowed: bool = True

    # Callbacks
    on_enter: Optional[Callable] = None
    on_exit: Optional[Callable] = None
    on_complete: Optional[Callable] = None


class OnboardingManager:
    """
    Enhanced onboarding system with:
    - Progressive disclosure
    - Context-sensitive tips
    - Skip/replay options
    - Progress tracking
    - Adaptive difficulty
    """

    def __init__(self):
        self.active = False
        self.current_step_index = 0
        self.steps: List[OnboardingStep] = []
        self.completed_steps: set[str] = set()
        self.skipped = False

        # Timing
        self.step_start_time = 0
        self.total_start_time = 0

        # UI
        self.font_title = pygame.font.SysFont("Arial", 32, bold=True)
        self.font_body = pygame.font.SysFont("Arial", 20)
        self.font_small = pygame.font.SysFont("Arial", 16)

        # Animation
        self.fade_alpha = 0
        self.fade_speed = 5
        self.arrow_bounce = 0

        # Progress tracking
        self.user_actions: Dict[str, int] = {}

        logger.info("Onboarding manager initialized")

    def start(self, tutorial_name: str = "basic") -> None:
        """Start onboarding tutorial"""
        self.active = True
        self.current_step_index = 0
        self.completed_steps.clear()
        self.skipped = False
        self.total_start_time = pygame.time.get_ticks()

        # Load tutorial steps
        if tutorial_name == "basic":
            self._create_basic_tutorial()
        elif tutorial_name == "advanced":
            self._create_advanced_tutorial()
        elif tutorial_name == "mobile":
            self._create_mobile_tutorial()

        if self.steps:
            self._enter_step(self.steps[0])

        logger.info(f"Started onboarding: {tutorial_name}")

    def _create_basic_tutorial(self) -> None:
        """Create basic tutorial steps"""
        self.steps = [
            OnboardingStep(
                id="welcome",
                type=OnboardingStepType.INFO,
                title="Welcome to PyPong!",
                description="Learn the basics in this quick tutorial.",
                auto_advance=True,
                duration_ms=3000,
            ),
            OnboardingStep(
                id="objective",
                type=OnboardingStepType.INFO,
                title="Game Objective",
                description="Score points by hitting the ball past your opponent.",
                auto_advance=True,
                duration_ms=4000,
            ),
            OnboardingStep(
                id="controls",
                type=OnboardingStepType.INTERACTIVE,
                title="Controls",
                description="Use W/S or Arrow keys to move your paddle up and down.",
                condition=lambda: self.user_actions.get("paddle_moved", 0) >= 3,
                highlight_rect=pygame.Rect(50, 300, 20, 120),
            ),
            OnboardingStep(
                id="hit_ball",
                type=OnboardingStepType.INTERACTIVE,
                title="Hit the Ball",
                description="Try to hit the ball with your paddle!",
                condition=lambda: self.user_actions.get("ball_hit", 0) >= 1,
                arrow_position=(512, 360),
            ),
            OnboardingStep(
                id="scoring",
                type=OnboardingStepType.INFO,
                title="Scoring",
                description="First to 5 points wins! Good luck!",
                auto_advance=True,
                duration_ms=3000,
            ),
        ]

    def _create_advanced_tutorial(self) -> None:
        """Create advanced tutorial steps"""
        self.steps = [
            OnboardingStep(
                id="powerups",
                type=OnboardingStepType.INTERACTIVE,
                title="Power-ups",
                description="Collect glowing power-ups for special abilities!",
                condition=lambda: self.user_actions.get("powerup_collected", 0) >= 1,
            ),
            OnboardingStep(
                id="combo",
                type=OnboardingStepType.INFO,
                title="Combo System",
                description="Hit the ball multiple times in a row for bonus points!",
                auto_advance=True,
                duration_ms=4000,
            ),
            OnboardingStep(
                id="special_moves",
                type=OnboardingStepType.INFO,
                title="Special Moves",
                description="Hit the ball at different angles for curve shots!",
                auto_advance=True,
                duration_ms=4000,
            ),
        ]

    def _create_mobile_tutorial(self) -> None:
        """Create mobile-specific tutorial"""
        self.steps = [
            OnboardingStep(
                id="touch_controls",
                type=OnboardingStepType.INTERACTIVE,
                title="Touch Controls",
                description="Tap the top half to move up, bottom half to move down.",
                condition=lambda: self.user_actions.get("touch_used", 0) >= 3,
            ),
            OnboardingStep(
                id="gestures",
                type=OnboardingStepType.INFO,
                title="Gestures",
                description="Swipe for quick movements!",
                auto_advance=True,
                duration_ms=3000,
            ),
        ]

    def _enter_step(self, step: OnboardingStep) -> None:
        """Enter a new step"""
        self.step_start_time = pygame.time.get_ticks()
        self.fade_alpha = 0

        if step.on_enter:
            step.on_enter()

        logger.debug(f"Entered step: {step.id}")

    def _exit_step(self, step: OnboardingStep) -> None:
        """Exit current step"""
        self.completed_steps.add(step.id)

        if step.on_exit:
            step.on_exit()

        if step.on_complete:
            step.on_complete()

        logger.debug(f"Completed step: {step.id}")

    def update(self) -> None:
        """Update onboarding state"""
        if not self.active or not self.steps:
            return

        current_step = self.steps[self.current_step_index]
        current_time = pygame.time.get_ticks()
        elapsed = current_time - self.step_start_time

        # Fade in animation
        if self.fade_alpha < 255:
            self.fade_alpha = min(255, self.fade_alpha + self.fade_speed)

        # Arrow bounce animation
        self.arrow_bounce = (current_time // 100) % 20 - 10

        # Check auto-advance
        if current_step.auto_advance and elapsed >= current_step.duration_ms:
            self.next_step()
            return

        # Check condition
        if current_step.condition and current_step.condition():
            self.next_step()

    def next_step(self) -> None:
        """Advance to next step"""
        if not self.steps:
            return

        current_step = self.steps[self.current_step_index]
        self._exit_step(current_step)

        self.current_step_index += 1

        if self.current_step_index >= len(self.steps):
            self.complete()
        else:
            self._enter_step(self.steps[self.current_step_index])

    def previous_step(self) -> None:
        """Go back to previous step"""
        if self.current_step_index > 0:
            self.current_step_index -= 1
            self._enter_step(self.steps[self.current_step_index])

    def skip(self) -> None:
        """Skip tutorial"""
        self.skipped = True
        self.complete()
        logger.info("Tutorial skipped")

    def complete(self) -> None:
        """Complete onboarding"""
        self.active = False
        total_time = pygame.time.get_ticks() - self.total_start_time

        logger.info(f"Onboarding completed in {total_time}ms, skipped={self.skipped}")

        # Save completion status
        self._save_progress()

    def _save_progress(self) -> None:
        """Save onboarding progress"""
        try:
            import json
            from pathlib import Path

            data = {
                "completed": True,
                "completed_steps": list(self.completed_steps),
                "skipped": self.skipped,
            }

            save_path = Path("PyPong/data/onboarding.json")
            save_path.parent.mkdir(exist_ok=True)

            with open(save_path, "w") as f:
                json.dump(data, f)
        except Exception as e:
            logger.error(f"Failed to save onboarding progress: {e}")

    def track_action(self, action: str) -> None:
        """Track user action for tutorial conditions"""
        self.user_actions[action] = self.user_actions.get(action, 0) + 1

    def draw(self, surface: pygame.Surface) -> None:
        """Draw onboarding UI"""
        if not self.active or not self.steps:
            return

        current_step = self.steps[self.current_step_index]

        # Draw overlay
        overlay = pygame.Surface(surface.get_size())
        overlay.set_alpha(180)
        overlay.fill((0, 0, 0))
        surface.blit(overlay, (0, 0))

        # Draw highlight area
        if current_step.highlight_rect:
            self._draw_highlight(surface, current_step.highlight_rect)

        # Draw arrow
        if current_step.arrow_position:
            self._draw_arrow(surface, current_step.arrow_position)

        # Draw text box
        self._draw_text_box(surface, current_step)

        # Draw progress
        self._draw_progress(surface)

        # Draw skip button
        if current_step.skip_allowed:
            self._draw_skip_button(surface)

    def _draw_highlight(self, surface: pygame.Surface, rect: pygame.Rect) -> None:
        """Draw highlight around area"""
        # Clear area
        clear_surface = pygame.Surface(rect.size)
        clear_surface.set_alpha(255)
        clear_surface.fill((0, 0, 0))
        surface.blit(clear_surface, rect.topleft)

        # Draw border
        pygame.draw.rect(surface, (255, 255, 0), rect, 3)

    def _draw_arrow(self, surface: pygame.Surface, position: Tuple[int, int]) -> None:
        """Draw animated arrow pointing to position"""
        x, y = position
        y += self.arrow_bounce

        # Draw arrow
        points = [
            (x, y),
            (x - 10, y - 20),
            (x + 10, y - 20),
        ]
        pygame.draw.polygon(surface, (255, 255, 0), points)

    def _draw_text_box(self, surface: pygame.Surface, step: OnboardingStep) -> None:
        """Draw text box with step information"""
        width, height = surface.get_size()
        box_width = min(600, width - 100)
        box_height = 200
        box_x = (width - box_width) // 2
        box_y = height - box_height - 50

        # Draw box
        box_rect = pygame.Rect(box_x, box_y, box_width, box_height)
        pygame.draw.rect(surface, (40, 40, 40), box_rect)
        pygame.draw.rect(surface, (255, 255, 255), box_rect, 2)

        # Draw title
        title_surface = self.font_title.render(step.title, True, (255, 255, 255))
        title_rect = title_surface.get_rect(centerx=box_x + box_width // 2, top=box_y + 20)
        surface.blit(title_surface, title_rect)

        # Draw description (word wrap)
        self._draw_wrapped_text(
            surface,
            step.description,
            pygame.Rect(box_x + 20, box_y + 70, box_width - 40, box_height - 90),
            self.font_body,
            (200, 200, 200),
        )

    def _draw_wrapped_text(
        self, surface: pygame.Surface, text: str, rect: pygame.Rect, font: pygame.font.Font, color: Tuple[int, int, int]
    ) -> None:
        """Draw text with word wrapping"""
        words = text.split(" ")
        lines = []
        current_line = []

        for word in words:
            test_line = " ".join(current_line + [word])
            if font.size(test_line)[0] <= rect.width:
                current_line.append(word)
            else:
                if current_line:
                    lines.append(" ".join(current_line))
                current_line = [word]

        if current_line:
            lines.append(" ".join(current_line))

        # Draw lines
        y = rect.top
        for line in lines:
            line_surface = font.render(line, True, color)
            surface.blit(line_surface, (rect.left, y))
            y += font.get_height() + 5

    def _draw_progress(self, surface: pygame.Surface) -> None:
        """Draw progress indicator"""
        width, height = surface.get_size()
        progress = (self.current_step_index + 1) / len(self.steps)

        bar_width = 300
        bar_height = 10
        bar_x = (width - bar_width) // 2
        bar_y = height - 30

        # Background
        pygame.draw.rect(surface, (60, 60, 60), (bar_x, bar_y, bar_width, bar_height))

        # Progress
        progress_width = int(bar_width * progress)
        pygame.draw.rect(surface, (0, 255, 0), (bar_x, bar_y, progress_width, bar_height))

        # Text
        text = f"{self.current_step_index + 1}/{len(self.steps)}"
        text_surface = self.font_small.render(text, True, (255, 255, 255))
        text_rect = text_surface.get_rect(center=(width // 2, bar_y - 15))
        surface.blit(text_surface, text_rect)

    def _draw_skip_button(self, surface: pygame.Surface) -> None:
        """Draw skip button"""
        width, height = surface.get_size()
        text = "Press ESC to skip"
        text_surface = self.font_small.render(text, True, (150, 150, 150))
        text_rect = text_surface.get_rect(topright=(width - 20, 20))
        surface.blit(text_surface, text_rect)

    def handle_event(self, event: pygame.event.Event) -> bool:
        """
        Handle input event.

        Returns:
            True if event was handled
        """
        if not self.active:
            return False

        if event.type == pygame.KEYDOWN:
            if event.key == pygame.K_ESCAPE:
                self.skip()
                return True
            elif event.key == pygame.K_SPACE or event.key == pygame.K_RETURN:
                if not self.steps[self.current_step_index].condition:
                    self.next_step()
                return True

        return False


# Global instance
_onboarding_manager: Optional[OnboardingManager] = None


def get_onboarding_manager() -> OnboardingManager:
    """Get global onboarding manager"""
    global _onboarding_manager
    if _onboarding_manager is None:
        _onboarding_manager = OnboardingManager()
    return _onboarding_manager
