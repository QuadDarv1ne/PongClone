"""
Beautiful main menu with localization support
"""
import math
import random
from typing import Any, Callable, Dict, List, Optional

import pygame
from pygame import Surface

from PyPong.ui.localization import get_localization, t
from PyPong.ui.themes import get_theme


class MenuItem:
    """Single menu item"""

    def __init__(self, text_key: str, action: Callable[[], None], shortcut: str = "", icon: str = ""):
        self.text_key = text_key
        self.action = action
        self.shortcut = shortcut
        self.icon = icon
        self.hovered = False


class AnimatedText:
    """Animated text with pulse effect"""

    def __init__(self, text: str, font: pygame.font.Font, color: tuple, pulse: bool = True):
        self.text = text
        self.font = font
        self.base_color = color
        self.pulse = pulse
        self.anim_phase = 0.0
        self.surface = None
        self._render()

    def _render(self):
        self.surface = self.font.render(self.text, True, self.base_color)

    def update(self, dt: float):
        if self.pulse:
            self.anim_phase += dt * 3
            # Subtle color pulse
            pulse = (math.sin(self.anim_phase) + 1) / 2 * 30
            r = min(255, self.base_color[0] + pulse)
            g = min(255, self.base_color[1] + pulse)
            b = min(255, self.base_color[2] + pulse)
            self.surface = self.font.render(self.text, True, (r, g, b))


class Menu:
    """
    Beautiful animated menu system
    """

    def __init__(self, screen: Surface, title: str = "menu.title"):
        self.screen = screen
        self.loc = get_localization()
        self.theme = get_theme("dark")  # Default theme

        # Menu state
        self.items: List[MenuItem] = []
        self.selected_index = 0
        self.visible = True

        # Animation
        self.anim_time = 0.0
        self.transition_progress = 1.0
        self.enter_animation = True

        # Background animation
        self.bg_particles: List[Dict[str, Any]] = []
        self._init_particles()

        # Title
        self.title_text = title

    def _init_particles(self):
        """Initialize background particles"""
        for _ in range(30):
            self.bg_particles.append(
                {
                    "x": random.randint(0, 1024),
                    "y": random.randint(0, 720),
                    "size": random.randint(2, 6),
                    "speed": random.uniform(0.2, 1.0),
                    "color": random.choice([(100, 200, 255), (255, 100, 150), (100, 255, 150), (255, 200, 100)]),
                }
            )

    def add_item(self, text_key: str, action: Callable[[], None], shortcut: str = "", icon: str = ""):
        """Add menu item"""
        self.items.append(MenuItem(text_key, action, shortcut, icon))

    def update(self, dt: float):
        """Update menu animations"""
        self.anim_time += dt

        # Enter animation
        if self.enter_animation:
            self.transition_progress = min(1.0, self.transition_progress + dt * 2)

        # Update particles
        for p in self.bg_particles:
            p["y"] -= p["speed"]
            if p["y"] < -10:
                p["y"] = 730
                p["x"] = pygame.display.get_surface().get_width() * (p["x"] / 1024)

    def handle_input(self, event: pygame.event.Event) -> Optional[str]:
        """Handle menu input. Returns action result."""
        if event.type != pygame.KEYDOWN:
            return None

        if event.key == pygame.K_UP:
            self.selected_index = (self.selected_index - 1) % len(self.items)
            return "navigate"

        elif event.key == pygame.K_DOWN:
            self.selected_index = (self.selected_index + 1) % len(self.items)
            return "navigate"

        elif event.key == pygame.K_RETURN:
            if self.items:
                self.items[self.selected_index].action()
                return "select"

        elif event.key == pygame.K_ESCAPE:
            return "back"

        # Number keys for quick selection
        elif event.key in (
            pygame.K_1,
            pygame.K_2,
            pygame.K_3,
            pygame.K_4,
            pygame.K_5,
            pygame.K_6,
            pygame.K_7,
            pygame.K_8,
            pygame.K_9,
        ):
            idx = event.key - pygame.K_1
            if idx < len(self.items):
                self.selected_index = idx
                self.items[idx].action()
                return "select"

        return None

    def draw(self):
        """Draw the menu"""
        if not self.visible:
            return

        # Draw background
        self._draw_background()

        # Draw title with animation
        self._draw_title()

        # Draw menu items
        self._draw_items()

        # Draw controls hint
        self._draw_controls()

    def _draw_background(self):
        """Draw animated background"""
        # Gradient background
        bg_color = self.theme.get("bg_color", (20, 20, 40))
        self.screen.fill(bg_color)

        # Draw particles
        for p in self.bg_particles:
            alpha = 50 + int(math.sin(self.anim_time + p["x"]) * 30)
            pygame.draw.circle(self.screen, p["color"], (int(p["x"]), int(p["y"])), p["size"])

    def _draw_title(self):
        """Draw animated title"""
        # Get localized title
        title = self.loc.get(self.title_text)

        # Large title font
        title_font = pygame.font.SysFont("arial", 72, bold=True)

        # Animated title with glow
        glow_color = (100, 150, 255)
        for offset in range(3, 0, -1):
            glow_text = title_font.render(title, True, glow_color)
            glow_rect = glow_text.get_rect(center=(self.screen.get_width() // 2, 120 - offset * 2))
            glow_text.set_alpha(50 * offset)
            self.screen.blit(glow_text, glow_rect)

        # Main title
        title_surf = title_font.render(title, True, (255, 255, 255))
        title_rect = title_surf.get_rect(center=(self.screen.get_width() // 2, 120))
        self.screen.blit(title_surf, title_rect)

    def _draw_items(self):
        """Draw menu items with selection animation"""
        if not self.items:
            return

        shortcut_font = pygame.font.SysFont("arial", 24)

        start_y = 250
        spacing = 60

        for i, item in enumerate(self.items):
            # Get localized text
            text = self.loc.get(item.text_key)

            # Animation offset
            delay = i * 0.1
            anim = min(1.0, self.transition_progress - delay)
            if anim < 0:
                anim = 0

            # Selection animation
            is_selected = i == self.selected_index
            if is_selected:
                # Pulsing effect
                scale = math.sin(self.anim_time * 4) * 0.2 + 1
                color = (255, 215, 0)  # Gold
            else:
                scale = 0.9
                color = (200, 200, 200)

            # Render text
            item_font = pygame.font.SysFont("arial", int(36 * scale), bold=is_selected)
            text_surf = item_font.render(text, True, color)

            # Position with animation
            x = self.screen.get_width() // 2 - text_surf.get_width() // 2
            y = start_y + i * spacing
            y = int(y + (1 - anim) * 50)  # Slide in animation

            # Draw shortcut
            if item.shortcut:
                shortcut_surf = shortcut_font.render(item.shortcut, True, (100, 100, 100))
                self.screen.blit(shortcut_surf, (x - 50, y + 5))

            # Draw selection indicator
            if is_selected:
                # Arrow indicator
                arrow = pygame.font.SysFont("arial", 30).render("▶", True, color)
                self.screen.blit(arrow, (x - 40, y))

                # Background highlight
                highlight_rect = pygame.Rect(x - 60, y - 10, text_surf.get_width() + 120, 50)
                pygame.draw.rect(self.screen, (50, 50, 80), highlight_rect, border_radius=10)

            self.screen.blit(text_surf, (x, y))

    def _draw_controls(self):
        """Draw control hints at bottom"""
        hint_font = pygame.font.SysFont("arial", 20)

        controls = [("↑↓", "navigate"), ("Enter", "select"), ("Esc", "back")]

        y = self.screen.get_height() - 40

        for i, (key, action) in enumerate(controls):
            text = f"{key}: {self.loc.get(f'controls.{action}', action)}"
            surf = hint_font.render(text, True, (100, 100, 100))
            x = 20 + i * 200
            self.screen.blit(surf, (x, y))


class MainMenu(Menu):
    """Main game menu"""

    def __init__(self, screen: Surface):
        super().__init__(screen, "menu.title")
        self._setup_items()

    def _setup_items(self):
        """Setup menu items"""
        # These will be connected to actual actions
        self.add_item("menu.start", lambda: None, "Enter")
        self.add_item("menu.campaign", lambda: None, "C")
        self.add_item("menu.challenges", lambda: None, "H")
        self.add_item("menu.minigames", lambda: None, "M")
        self.add_item("menu.stats", lambda: None, "S")
        self.add_item("menu.settings", lambda: None, "O")
        self.add_item("menu.quit", lambda: None, "Esc")


class SettingsMenu(Menu):
    """Settings menu with language selection"""

    def __init__(self, screen: Surface):
        super().__init__(screen, "settings.title")
        self._setup_items()

    def _setup_items(self):
        """Setup settings items"""
        self.add_item("settings.language", lambda: None, "L")
        self.add_item("settings.music_volume", lambda: None, "M")
        self.add_item("settings.sfx_volume", lambda: None, "S")
        self.add_item("settings.fullscreen", lambda: None, "F")
        self.add_item("settings.show_fps", lambda: None, "D")
        self.add_item("settings.back", lambda: None, "Esc")


# Test function
def test_menu():
    """Test the menu system"""
    pygame.init()
    screen = pygame.display.set_mode((1024, 720))
    pygame.display.set_caption("PyPong Menu Test")

    # Initialize localization
    from PyPong.ui.localization import init_localization

    init_localization("en")

    # Create menu
    menu = MainMenu(screen)

    running = True
    clock = pygame.time.Clock()

    while running:
        dt = clock.tick(60) / 1000

        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                running = False
            elif event.type == pygame.KEYDOWN:
                if event.key == pygame.K_ESCAPE:
                    running = False
                menu.handle_input(event)

        menu.update(dt)
        menu.draw()
        pygame.display.flip()

    pygame.quit()


if __name__ == "__main__":
    test_menu()
