"""Customization menu for selecting paddle skins, ball skins, and court themes"""
import pygame
from typing import Optional, List, Dict, Any

from PyPong.core.config import FONT_NAME, WINDOW_WIDTH, WINDOW_HEIGHT
from PyPong.core.logger import logger
from PyPong.ui.localization import t
from PyPong.ui.themes import get_theme
from PyPong.systems.settings import Settings
from PyPong.ui.customization import CustomizationManager, PaddleSkin, BallSkin, CourtTheme


class CustomizationMenu:
    """Menu for customizing paddles, balls, and court appearance"""

    # Menu tabs
    TAB_PADDLE = "paddle"
    TAB_BALL = "ball"
    TAB_COURT = "court"

    def __init__(self, screen: pygame.Surface, customization: CustomizationManager, settings: Settings) -> None:
        self.screen = screen
        self.customization = customization
        self.settings = settings

        # Fonts
        self.title_font = pygame.font.SysFont(FONT_NAME, 40, bold=True)
        self.font = pygame.font.SysFont(FONT_NAME, 32)
        self.small_font = pygame.font.SysFont(FONT_NAME, 24)
        self.desc_font = pygame.font.SysFont(FONT_NAME, 20)

        # State
        self.current_tab = self.TAB_PADDLE
        self.selected_index = 0
        self.scroll_offset = 0
        self.max_visible = 8

        # Preview state
        self.preview_paddle_color = None
        self.preview_ball_color = None
        self.preview_court_color = None

        # Tabs
        self.tabs = [
            (self.TAB_PADDLE, t("customize.tab_paddle")),
            (self.TAB_BALL, t("customize.tab_ball")),
            (self.TAB_COURT, t("customize.tab_court")),
        ]

        self._update_preview()

    def _update_preview(self) -> None:
        """Update preview colors based on current tab"""
        if self.current_tab == self.TAB_PADDLE:
            skins = self.customization.get_unlocked_paddle_skins()
            if skins:
                idx = min(self.selected_index, len(skins) - 1)
                self.preview_paddle_color = skins[idx].color
        elif self.current_tab == self.TAB_BALL:
            skins = self.customization.get_unlocked_ball_skins()
            if skins:
                idx = min(self.selected_index, len(skins) - 1)
                self.preview_ball_color = skins[idx].color
        elif self.current_tab == self.TAB_COURT:
            themes = self.customization.get_unlocked_court_themes()
            if themes:
                idx = min(self.selected_index, len(themes) - 1)
                theme = themes[idx]
                self.preview_court_color = theme.background_color

    def _get_current_items(self) -> List[Any]:
        """Get items for the current tab"""
        if self.current_tab == self.TAB_PADDLE:
            return self.customization.get_unlocked_paddle_skins()
        elif self.current_tab == self.TAB_BALL:
            return self.customization.get_unlocked_ball_skins()
        elif self.current_tab == self.TAB_COURT:
            return self.customization.get_unlocked_court_themes()
        return []

    def _apply_selection(self) -> None:
        """Apply the currently selected item"""
        items = self._get_current_items()
        if not items:
            return

        idx = min(self.selected_index, len(items) - 1)
        item = items[idx]

        if self.current_tab == self.TAB_PADDLE:
            # Apply to both players for preview
            self.customization.set_paddle_skin(1, item.id)
            self.customization.set_paddle_skin(2, item.id)
            logger.info(f"Paddle skin applied: {item.name}")
        elif self.current_tab == self.TAB_BALL:
            self.customization.set_ball_skin(item.id)
            logger.info(f"Ball skin applied: {item.name}")
        elif self.current_tab == self.TAB_COURT:
            self.customization.set_court_theme(item.id)
            logger.info(f"Court theme applied: {item.name}")

    def draw(self) -> None:
        """Draw the customization menu"""
        self.screen.fill((15, 15, 25))

        # Title
        title = self.title_font.render(t("customize.title"), True, (100, 200, 255))
        title_rect = title.get_rect(center=(WINDOW_WIDTH // 2, 30))
        self.screen.blit(title, title_rect)

        # Tabs
        self._draw_tabs()

        # Preview area (top right)
        self._draw_preview()

        # Items list
        self._draw_items()

        # Bottom hint
        self._draw_hints()

    def _draw_tabs(self) -> None:
        """Draw tab buttons"""
        tab_width = 200
        tab_height = 35
        tab_y = 75
        total_width = tab_width * len(self.tabs)
        start_x = (WINDOW_WIDTH - total_width) // 2

        for i, (tab_id, tab_label) in enumerate(self.tabs):
            x = start_x + i * tab_width
            is_active = tab_id == self.current_tab

            # Tab background
            color = (60, 120, 180) if is_active else (40, 40, 50)
            pygame.draw.rect(self.screen, color, (x, tab_y, tab_width - 4, tab_height), border_radius=6)

            if is_active:
                pygame.draw.rect(self.screen, (100, 200, 255), (x, tab_y, tab_width - 4, tab_height), 2, border_radius=6)

            # Tab text
            text = self.small_font.render(tab_label, True, (255, 255, 255) if is_active else (150, 150, 150))
            text_rect = text.get_rect(center=(x + tab_width // 2 - 2, tab_y + tab_height // 2))
            self.screen.blit(text, text_rect)

    def _draw_preview(self) -> None:
        """Draw preview area"""
        preview_x = WINDOW_WIDTH - 280
        preview_y = 130
        preview_w = 250
        preview_h = 300

        # Preview box
        pygame.draw.rect(self.screen, (25, 25, 35), (preview_x, preview_y, preview_w, preview_h), border_radius=8)
        pygame.draw.rect(self.screen, (60, 80, 100), (preview_x, preview_y, preview_w, preview_h), 2, border_radius=8)

        # Preview label
        label = self.small_font.render(t("customize.preview"), True, (150, 150, 150))
        self.screen.blit(label, (preview_x + 10, preview_y - 25))

        # Draw preview content
        if self.current_tab == self.TAB_PADDLE and self.preview_paddle_color:
            self._draw_paddle_preview(preview_x, preview_y, preview_w, preview_h)
        elif self.current_tab == self.TAB_BALL and self.preview_ball_color:
            self._draw_ball_preview(preview_x, preview_y, preview_w, preview_h)
        elif self.current_tab == self.TAB_COURT and self.preview_court_color:
            self._draw_court_preview(preview_x, preview_y, preview_w, preview_h)

    def _draw_paddle_preview(self, x: int, y: int, w: int, h: int) -> None:
        """Draw paddle preview"""
        # Mini court
        pygame.draw.rect(self.screen, (30, 30, 40), (x + 20, y + 20, w - 40, h - 40))

        # Left paddle (player 1)
        paddle_w = 12
        paddle_h = 80
        paddle1_x = x + 40
        paddle1_y = y + h // 2 - paddle_h // 2
        pygame.draw.rect(self.screen, self.preview_paddle_color, (paddle1_x, paddle1_y, paddle_w, paddle_h))

        # Right paddle (player 2)
        paddle2_x = x + w - 40 - paddle_w
        pygame.draw.rect(self.screen, self.preview_paddle_color, (paddle2_x, paddle1_y, paddle_w, paddle_h))

        # Ball
        ball_x = x + w // 2
        ball_y = y + h // 2
        pygame.draw.circle(self.screen, (255, 255, 255), (ball_x, ball_y), 8)

        # Net
        for ny in range(y + 30, y + h - 30, 20):
            pygame.draw.rect(self.screen, (60, 60, 70), (x + w // 2 - 1, ny, 2, 10))

    def _draw_ball_preview(self, x: int, y: int, w: int, h: int) -> None:
        """Draw ball preview"""
        # Mini court
        pygame.draw.rect(self.screen, (30, 30, 40), (x + 20, y + 20, w - 40, h - 40))

        # Ball with trail
        ball_x = x + w // 2
        ball_y = y + h // 2

        # Trail
        trail_color = self.preview_ball_color
        for i in range(5, 0, -1):
            trail_x = ball_x - i * 12
            alpha = int(255 * (1 - i / 6))
            trail_surf = pygame.Surface((10, 10))
            trail_surf.set_alpha(alpha)
            pygame.draw.circle(trail_surf, trail_color, (5, 5), 8 - i)
            self.screen.blit(trail_surf, (trail_x, ball_y))

        # Main ball
        pygame.draw.circle(self.screen, self.preview_ball_color, (ball_x, ball_y), 10)

        # Glow effect
        for r in range(20, 10, -2):
            glow_surf = pygame.Surface((r * 2, r * 2))
            glow_surf.set_alpha(30)
            pygame.draw.circle(glow_surf, self.preview_ball_color, (r, r), r)
            self.screen.blit(glow_surf, (ball_x - r, ball_y - r))

        # Paddles (default)
        paddle_w = 12
        paddle_h = 80
        pygame.draw.rect(self.screen, (100, 200, 100), (x + 40, y + h // 2 - paddle_h // 2, paddle_w, paddle_h))
        pygame.draw.rect(self.screen, (200, 200, 100), (x + w - 40 - paddle_w, y + h // 2 - paddle_h // 2, paddle_w, paddle_h))

    def _draw_court_preview(self, x: int, y: int, w: int, h: int) -> None:
        """Draw court preview"""
        # Court background
        pygame.draw.rect(self.screen, self.preview_court_color, (x + 20, y + 20, w - 40, h - 40))

        # Net
        pygame.draw.line(self.screen, (150, 150, 150), (x + w // 2, y + 20), (x + w // 2, y + h - 20), 2)

        # Lines
        pygame.draw.rect(self.screen, (150, 150, 150), (x + 20, y + 20, w - 40, h - 40), 2)

        # Paddles
        paddle_w = 12
        paddle_h = 80
        pygame.draw.rect(self.screen, (100, 200, 100), (x + 40, y + h // 2 - paddle_h // 2, paddle_w, paddle_h))
        pygame.draw.rect(self.screen, (200, 200, 100), (x + w - 40 - paddle_w, y + h // 2 - paddle_h // 2, paddle_w, paddle_h))

        # Ball
        pygame.draw.circle(self.screen, (255, 255, 255), (x + w // 2, y + h // 2), 8)

    def _draw_items(self) -> None:
        """Draw items list for current tab"""
        items = self._get_current_items()
        if not items:
            no_items = self.font.render(t("customize.no_items"), True, (100, 100, 100))
            self.screen.blit(no_items, (60, 200))
            return

        # Calculate scroll
        if self.selected_index < self.scroll_offset:
            self.scroll_offset = self.selected_index
        elif self.selected_index >= self.scroll_offset + self.max_visible:
            self.scroll_offset = self.selected_index - self.max_visible + 1

        start_y = 130
        line_height = 38

        for i in range(self.scroll_offset, min(len(items), self.scroll_offset + self.max_visible)):
            item = items[i]
            visible_idx = i - self.scroll_offset
            y = start_y + visible_idx * line_height

            # Highlight selected
            if i == self.selected_index:
                highlight_rect = pygame.Rect(40, y - 2, 600, line_height)
                pygame.draw.rect(self.screen, (30, 40, 60), highlight_rect, border_radius=4)
                pygame.draw.rect(self.screen, (80, 160, 255), highlight_rect, 1, border_radius=4)

            # Item name
            color = (255, 220, 100) if i == self.selected_index else (200, 200, 210)
            name_text = self.font.render(item.name, True, color)
            self.screen.blit(name_text, (60, y))

            # Color swatch
            swatch_x = 550
            swatch_y = y + 5
            pygame.draw.rect(self.screen, item.color, (swatch_x, swatch_y, 28, 28), border_radius=4)
            pygame.draw.rect(self.screen, (100, 100, 100), (swatch_x, swatch_y, 28, 28), 1, border_radius=4)

            # Locked indicator (if applicable)
            if hasattr(item, 'unlock_requirement') and item.unlock_requirement and not getattr(item, 'unlocked', True):
                lock_text = self.small_font.render("🔒", True, (100, 100, 100))
                self.screen.blit(lock_text, (swatch_x + 35, swatch_y))

        # Item description
        if items:
            idx = min(self.selected_index, len(items) - 1)
            item = items[idx]
            if hasattr(item, 'unlock_requirement') and item.unlock_requirement:
                desc_text = self.desc_font.render(
                    t("customize.unlock_requirement", item.unlock_requirement),
                    True, (120, 140, 160)
                )
                self.screen.blit(desc_text, (60, start_y + self.max_visible * line_height + 10))

    def _draw_hints(self) -> None:
        """Draw control hints at bottom"""
        hint_font = pygame.font.SysFont(FONT_NAME, 18)
        hints = [
            ("←→", t("customize.hint_tabs")),
            ("↑↓", t("customize.hint_select")),
            ("Enter", t("customize.hint_apply")),
            ("Esc", t("misc.back")),
        ]

        y = WINDOW_HEIGHT - 35
        for i, (key, action) in enumerate(hints):
            text = f"{key}: {action}"
            surf = hint_font.render(text, True, (100, 100, 100))
            x = 20 + i * 220
            self.screen.blit(surf, (x, y))

    def handle_input(self, event: pygame.event.Event) -> Optional[str]:
        """Handle input. Returns "back" to exit."""
        if event.type != pygame.KEYDOWN:
            return None

        if event.key == pygame.K_ESCAPE:
            return "back"

        if event.key == pygame.K_LEFT:
            # Switch tab
            tabs = [t[0] for t in self.tabs]
            current_idx = tabs.index(self.current_tab)
            new_idx = (current_idx - 1) % len(tabs)
            self.current_tab = tabs[new_idx]
            self.selected_index = 0
            self.scroll_offset = 0
            self._update_preview()

        elif event.key == pygame.K_RIGHT:
            # Switch tab
            tabs = [t[0] for t in self.tabs]
            current_idx = tabs.index(self.current_tab)
            new_idx = (current_idx + 1) % len(tabs)
            self.current_tab = tabs[new_idx]
            self.selected_index = 0
            self.scroll_offset = 0
            self._update_preview()

        elif event.key == pygame.K_UP:
            items = self._get_current_items()
            if items:
                self.selected_index = max(0, self.selected_index - 1)
                self._update_preview()

        elif event.key == pygame.K_DOWN:
            items = self._get_current_items()
            if items:
                self.selected_index = min(len(items) - 1, self.selected_index + 1)
                self._update_preview()

        elif event.key == pygame.K_RETURN:
            self._apply_selection()

        return None
