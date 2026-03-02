"""
Enhanced UI components with animations and effects
"""
import pygame
from typing import Optional, List, Tuple, Callable, Dict, Any
from dataclasses import dataclass, field
from PyPong.core.constants import Colors
from PyPong.core.logger import logger


@dataclass
class Animation:
    """Animation data"""
    start_time: int
    duration: int
    start_value: float
    end_value: float
    easing: str = "linear"

    def get_value(self, current_time: int) -> float:
        """Get current animation value"""
        elapsed = current_time - self.start_time
        if elapsed >= self.duration:
            return self.end_value

        progress = elapsed / self.duration

        # Apply easing
        if self.easing == "ease_in":
            progress = progress ** 2
        elif self.easing == "ease_out":
            progress = 1 - (1 - progress) ** 2
        elif self.easing == "ease_in_out":
            if progress < 0.5:
                progress = 2 * progress ** 2
            else:
                progress = 1 - 2 * (1 - progress) ** 2

        return self.start_value + (self.end_value - self.start_value) * progress

    def is_complete(self, current_time: int) -> bool:
        """Check if animation is complete"""
        return current_time - self.start_time >= self.duration


class ParticleEffect:
    """Particle effect system"""

    def __init__(
        self,
        x: float,
        y: float,
        color: Tuple[int, int, int],
        count: int = 20,
        lifetime: int = 1000
    ):
        self.particles: List[dict] = []
        self.lifetime = lifetime
        
        import random
        for _ in range(count):
            angle = random.uniform(0, 360)
            speed = random.uniform(1, 5)
            
            particle = {
                'x': x,
                'y': y,
                'vx': speed * pygame.math.Vector2(1, 0).rotate(angle).x,
                'vy': speed * pygame.math.Vector2(1, 0).rotate(angle).y,
                'color': color,
                'size': random.randint(2, 5),
                'life': lifetime,
                'max_life': lifetime
            }
            self.particles.append(particle)
    
    def update(self) -> bool:
        """Update particles, returns False when all dead"""
        for particle in self.particles[:]:
            particle['x'] += particle['vx']
            particle['y'] += particle['vy']
            particle['vy'] += 0.2  # Gravity
            particle['life'] -= 16  # Assuming 60 FPS
            
            if particle['life'] <= 0:
                self.particles.remove(particle)
        
        return len(self.particles) > 0
    
    def draw(self, screen: pygame.Surface) -> None:
        """Draw particles"""
        for particle in self.particles:
            alpha = int(255 * (particle['life'] / particle['max_life']))
            color = (*particle['color'], alpha)
            
            # Create surface with alpha
            surf = pygame.Surface((particle['size'], particle['size']))
            surf.set_alpha(alpha)
            surf.fill(particle['color'])
            
            screen.blit(surf, (int(particle['x']), int(particle['y'])))


class ComboDisplay:
    """Displays combo counter with animations"""
    
    def __init__(self, x: int, y: int):
        self.x = x
        self.y = y
        self.combo = 0
        self.multiplier = 1.0
        self.animation: Optional[Animation] = None
        self.font = pygame.font.SysFont("Helvetica", 48, bold=True)
        self.small_font = pygame.font.SysFont("Helvetica", 24)
    
    def update_combo(self, combo: int, multiplier: float) -> None:
        """Update combo value"""
        if combo > self.combo:
            # Start scale animation
            current_time = pygame.time.get_ticks()
            self.animation = Animation(
                start_time=current_time,
                duration=200,
                start_value=1.5,
                end_value=1.0,
                easing="ease_out"
            )
        
        self.combo = combo
        self.multiplier = multiplier
    
    def draw(self, screen: pygame.Surface) -> None:
        """Draw combo display"""
        if self.combo <= 1:
            return
        
        current_time = pygame.time.get_ticks()
        
        # Get scale from animation
        scale = 1.0
        if self.animation and not self.animation.is_complete(current_time):
            scale = self.animation.get_value(current_time)
        
        # Combo text
        combo_text = self.font.render(f"{self.combo}x COMBO!", True, Colors.YELLOW.to_tuple())
        
        # Scale text
        if scale != 1.0:
            width = int(combo_text.get_width() * scale)
            height = int(combo_text.get_height() * scale)
            combo_text = pygame.transform.scale(combo_text, (width, height))
        
        combo_rect = combo_text.get_rect(center=(self.x, self.y))
        screen.blit(combo_text, combo_rect)
        
        # Multiplier text
        mult_text = self.small_font.render(
            f"{self.multiplier:.1f}x points",
            True, Colors.GREEN.to_tuple()
        )
        mult_rect = mult_text.get_rect(center=(self.x, self.y + 40))
        screen.blit(mult_text, mult_rect)


class AchievementNotification:
    """Achievement unlock notification"""
    
    def __init__(self, achievement_name: str, points: int):
        self.name = achievement_name
        self.points = points
        self.start_time = pygame.time.get_ticks()
        self.duration = 3000
        self.y_animation: Optional[Animation] = None
        self.alpha_animation: Optional[Animation] = None
        
        # Start animations
        self.y_animation = Animation(
            start_time=self.start_time,
            duration=500,
            start_value=-100,
            end_value=50,
            easing="ease_out"
        )
        
        fade_start = self.start_time + self.duration - 500
        self.alpha_animation = Animation(
            start_time=fade_start,
            duration=500,
            start_value=255,
            end_value=0,
            easing="ease_in"
        )
        
        self.font = pygame.font.SysFont("Helvetica", 32, bold=True)
        self.small_font = pygame.font.SysFont("Helvetica", 20)
    
    def is_active(self) -> bool:
        """Check if notification is still active"""
        elapsed = pygame.time.get_ticks() - self.start_time
        return elapsed < self.duration
    
    def draw(self, screen: pygame.Surface, x: int) -> None:
        """Draw notification"""
        if not self.is_active():
            return
        
        current_time = pygame.time.get_ticks()
        
        # Get position
        y = self.y_animation.get_value(current_time)
        
        # Get alpha
        alpha = 255
        if current_time >= self.alpha_animation.start_time:
            alpha = int(self.alpha_animation.get_value(current_time))
        
        # Background
        bg_width = 400
        bg_height = 80
        bg_rect = pygame.Rect(x - bg_width // 2, int(y), bg_width, bg_height)
        
        bg_surf = pygame.Surface((bg_width, bg_height))
        bg_surf.set_alpha(alpha)
        bg_surf.fill((40, 40, 40))
        screen.blit(bg_surf, bg_rect)
        
        pygame.draw.rect(screen, Colors.YELLOW.to_tuple(), bg_rect, 2)
        
        # Text
        title = self.font.render("🏆 Achievement Unlocked!", True, Colors.YELLOW.to_tuple())
        title_surf = pygame.Surface(title.get_size())
        title_surf.set_alpha(alpha)
        title_surf.blit(title, (0, 0))
        screen.blit(title_surf, (x - title.get_width() // 2, int(y) + 10))
        
        name = self.small_font.render(self.name, True, Colors.WHITE.to_tuple())
        name_surf = pygame.Surface(name.get_size())
        name_surf.set_alpha(alpha)
        name_surf.blit(name, (0, 0))
        screen.blit(name_surf, (x - name.get_width() // 2, int(y) + 45))


class ProgressBar:
    """Animated progress bar"""
    
    def __init__(
        self,
        x: int,
        y: int,
        width: int,
        height: int,
        color: Tuple[int, int, int] = Colors.GREEN.to_tuple()
    ):
        self.x = x
        self.y = y
        self.width = width
        self.height = height
        self.color = color
        self.current_progress = 0.0
        self.target_progress = 0.0
        self.animation: Optional[Animation] = None
    
    def set_progress(self, progress: float) -> None:
        """Set target progress (0-1)"""
        self.target_progress = max(0, min(1, progress))
        
        # Start animation
        current_time = pygame.time.get_ticks()
        self.animation = Animation(
            start_time=current_time,
            duration=300,
            start_value=self.current_progress,
            end_value=self.target_progress,
            easing="ease_out"
        )
    
    def update(self) -> None:
        """Update progress bar"""
        if self.animation:
            current_time = pygame.time.get_ticks()
            self.current_progress = self.animation.get_value(current_time)
    
    def draw(self, screen: pygame.Surface) -> None:
        """Draw progress bar"""
        # Background
        pygame.draw.rect(
            screen, (60, 60, 60),
            (self.x, self.y, self.width, self.height)
        )
        
        # Progress fill
        fill_width = int(self.width * self.current_progress)
        if fill_width > 0:
            pygame.draw.rect(
                screen, self.color,
                (self.x, self.y, fill_width, self.height)
            )
        
        # Border
        pygame.draw.rect(
            screen, Colors.WHITE.to_tuple(),
            (self.x, self.y, self.width, self.height),
            2
        )


class Button:
    """Interactive button with hover effects"""
    
    def __init__(
        self,
        x: int,
        y: int,
        width: int,
        height: int,
        text: str,
        callback: Optional[Callable] = None,
        color: Tuple[int, int, int] = Colors.GRAY.to_tuple()
    ):
        self.rect = pygame.Rect(x, y, width, height)
        self.text = text
        self.callback = callback
        self.color = color
        self.hover_color = tuple(min(c + 40, 255) for c in color)
        self.is_hovered = False
        self.is_pressed = False
        self.font = pygame.font.SysFont("Helvetica", 24)
    
    def handle_event(self, event: pygame.event.Event) -> bool:
        """Handle mouse events, returns True if clicked"""
        if event.type == pygame.MOUSEMOTION:
            self.is_hovered = self.rect.collidepoint(event.pos)
        
        elif event.type == pygame.MOUSEBUTTONDOWN:
            if self.is_hovered:
                self.is_pressed = True
        
        elif event.type == pygame.MOUSEBUTTONUP:
            if self.is_pressed and self.is_hovered:
                self.is_pressed = False
                if self.callback:
                    self.callback()
                return True
            self.is_pressed = False
        
        return False
    
    def draw(self, screen: pygame.Surface) -> None:
        """Draw button"""
        color = self.hover_color if self.is_hovered else self.color
        
        # Button background
        pygame.draw.rect(screen, color, self.rect)
        pygame.draw.rect(screen, Colors.WHITE.to_tuple(), self.rect, 2)
        
        # Text
        text_surf = self.font.render(self.text, True, Colors.WHITE.to_tuple())
        text_rect = text_surf.get_rect(center=self.rect.center)
        screen.blit(text_surf, text_rect)


class NotificationManager:
    """Manages multiple notifications"""
    
    def __init__(self):
        self.notifications: List[AchievementNotification] = []
        self.particles: List[ParticleEffect] = []
    
    def add_achievement(self, name: str, points: int) -> None:
        """Add achievement notification"""
        notification = AchievementNotification(name, points)
        self.notifications.append(notification)
        logger.debug(f"Added achievement notification: {name}")
    
    def add_particles(self, x: float, y: float, color: Tuple[int, int, int]) -> None:
        """Add particle effect"""
        effect = ParticleEffect(x, y, color)
        self.particles.append(effect)
    
    def update(self) -> None:
        """Update all notifications"""
        # Remove inactive notifications
        self.notifications = [n for n in self.notifications if n.is_active()]
        
        # Update particles
        self.particles = [p for p in self.particles if p.update()]
    
    def draw(self, screen: pygame.Surface) -> None:
        """Draw all notifications"""
        # Draw particles
        for particle in self.particles:
            particle.draw(screen)
        
        # Draw notifications
        for i, notification in enumerate(self.notifications):
            notification.draw(screen, screen.get_width() // 2)
