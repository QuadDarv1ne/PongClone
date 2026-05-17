""" Main menu integration with GameEngine """
import pygame
from enum import Enum
from typing import Optional

import pygame
from PyPong.core.config import FONT_NAME, FPS, WHITE, WINDOW_HEIGHT, WINDOW_WIDTH
from PyPong.ui.localization import get_localization, init_localization
from PyPong.ui.menu import MainMenu, SettingsMenu, Menu
from PyPong.ui.customization import CustomizationManager
from PyPong.ui.customize_menu import CustomizationMenu
from PyPong.ui.stats_screen import StatsScreen

from PyPong.games.base import GameModeType
from PyPong.games.engine import GameEngine


class GameState(Enum):
    """Game states"""
    MENU = "menu"
    MODE_SELECT = "mode_select"
    PLAYING = "playing"
    SETTINGS = "settings"
    CUSTOMIZE = "customize"
    STATS = "stats"
    PAUSED = "paused"
    GAME_OVER = "game_over"


class GameWithMenu(GameEngine):
    """Extended GameEngine with beautiful menu system"""

    def __init__(self) -> None:
        # Initialize localization first
        init_localization('en')
        super().__init__()

        # Menu state
        self.state = GameState.MENU
        self.main_menu: Optional[MainMenu] = None
        self.settings_menu: Optional[SettingsMenu] = None
        self.customization_menu: Optional[CustomizationMenu] = None
        self.stats_screen: Optional[StatsScreen] = None

        # Initialize customization and stats systems
        self.customization = CustomizationManager()
        from PyPong.systems.stats import StatsManager
        self.stats_manager = StatsManager()

        # Initialize menus
        self._init_menus()

        # Language toggle
        self.current_lang = 'en'

    def _init_menus(self) -> None:
        """Initialize all menus"""
        self.main_menu = MainMenu(self.screen)
        self.settings_menu = SettingsMenu(self.screen, self.settings)
        self.customization_menu = CustomizationMenu(self.screen, self.customization, self.settings)
        self.stats_screen = StatsScreen(self.screen, self.stats_manager)

        # Setup menu actions
        # 0: Quick Match
        self.main_menu.items[0].action = lambda: self._start_game(GameModeType.CLASSIC)
        # 1: Start (Mode Select)
        self.main_menu.items[1].action = lambda: self._start_game(GameModeType.CLASSIC)
        # 2: Multiplayer
        self.main_menu.items[2].action = lambda: self._start_game(GameModeType.MULTIPLAYER)
        # 3: Campaign
        self.main_menu.items[3].action = lambda: self._start_game(GameModeType.CAMPAIGN)
        # 4: Challenges
        self.main_menu.items[4].action = lambda: self._start_game(GameModeType.CAMPAIGN)
        # 5: Minigames
        self.main_menu.items[5].action = lambda: self._start_game(GameModeType.MINIGAME)
        # 6: Customize
        self.main_menu.items[6].action = self._open_customize
        # 7: Stats
        self.main_menu.items[7].action = lambda: self._show_stats()
        # 8: Settings
        self.main_menu.items[8].action = lambda: self._open_settings()
        # 9: Quit
        self.main_menu.items[9].action = lambda: setattr(self, 'running', False)

    def _start_game(self, mode: GameModeType):
        """Start game in specified mode"""
        self.set_mode(mode)
        if self.current_mode:
            self.current_mode.start()
        self.state = GameState.PLAYING

    def _show_stats(self):
        """Show statistics screen"""
        self.state = GameState.STATS

    def _open_settings(self):
        """Open settings menu"""
        self.state = GameState.SETTINGS

    def _open_customize(self):
        """Open customization menu"""
        self.state = GameState.CUSTOMIZE

    def _draw_pause_menu(self) -> None:
        """Draw enhanced pause menu with quick settings"""
        loc = get_localization()
        title_font = pygame.font.SysFont(FONT_NAME, 64, bold=True)
        menu_font = pygame.font.SysFont(FONT_NAME, 32)
        hint_font = pygame.font.SysFont(FONT_NAME, 24)
        small_font = pygame.font.SysFont(FONT_NAME, 22)

        center_x = WINDOW_WIDTH // 2
        center_y = WINDOW_HEIGHT // 2

        # Title
        title = title_font.render(loc.get("game.paused"), True, (100, 200, 255))
        title_rect = title.get_rect(center=(center_x, center_y - 180))
        self.screen.blit(title, title_rect)

        # Separator line
        pygame.draw.line(
            self.screen, (60, 120, 180),
            (center_x - 150, center_y - 140),
            (center_x + 150, center_y - 140),
            2,
        )

        # Menu items
        menu_items = [
            ("Enter", loc.get("game.resume"), (255, 255, 255)),
            ("Esc", loc.get("menu.quit"), (255, 100, 100)),
        ]

        y_offset = center_y - 110
        for key, action, color in menu_items:
            # Key label
            key_surf = hint_font.render(f"[{key}]", True, (150, 200, 255))
            self.screen.blit(key_surf, (center_x - 150, y_offset))

            # Action text
            action_surf = menu_font.render(action, True, color)
            self.screen.blit(action_surf, (center_x - 80, y_offset - 2))

            y_offset += 45

        # Quick Settings section
        quick_settings_y = center_y + 10

        # Section header
        header = hint_font.render("— Quick Settings —", True, (150, 150, 150))
        header_rect = header.get_rect(center=(center_x, quick_settings_y))
        self.screen.blit(header, header_rect)

        # Music Volume
        qs_y = quick_settings_y + 40
        music_vol = self.settings.get("music_volume", 0.5)
        music_label = small_font.render("Music:", True, (180, 180, 180))
        self.screen.blit(music_label, (center_x - 150, qs_y))

        # Volume bar background
        bar_x = center_x - 50
        bar_w = 200
        bar_h = 16
        pygame.draw.rect(self.screen, (40, 40, 40), (bar_x, qs_y + 2, bar_w, bar_h), border_radius=4)
        # Volume fill
        fill_w = int(bar_w * music_vol)
        pygame.draw.rect(self.screen, (100, 200, 100), (bar_x, qs_y + 2, fill_w, bar_h), border_radius=4)
        # Volume value
        vol_text = small_font.render(f"{music_vol:.0%}", True, (200, 200, 200))
        self.screen.blit(vol_text, (bar_x + bar_w + 10, qs_y))

        # SFX Volume
        sfx_vol = self.settings.get("sfx_volume", 0.7)
        sfx_label = small_font.render("SFX:", True, (180, 180, 180))
        self.screen.blit(sfx_label, (center_x - 150, qs_y + 35))

        pygame.draw.rect(self.screen, (40, 40, 40), (bar_x, qs_y + 37, bar_w, bar_h), border_radius=4)
        fill_w = int(bar_w * sfx_vol)
        pygame.draw.rect(self.screen, (100, 150, 255), (bar_x, qs_y + 37, fill_w, bar_h), border_radius=4)
        vol_text = small_font.render(f"{sfx_vol:.0%}", True, (200, 200, 200))
        self.screen.blit(vol_text, (bar_x + bar_w + 10, qs_y + 35))

        # FPS toggle
        show_fps = self.settings.get("show_fps", False)
        fps_label = small_font.render(f"Show FPS: {'ON' if show_fps else 'OFF'}", True, (180, 180, 180))
        self.screen.blit(fps_label, (center_x - 150, qs_y + 75))

        # Hint for quick settings
        hint_y = qs_y + 110
        hint1 = small_font.render("←/→: Adjust Volume  |  F: Toggle FPS", True, (100, 100, 100))
        self.screen.blit(hint1, (center_x - hint1.get_width() // 2, hint_y))

        # Game info section
        info_y = center_y + 180
        pygame.draw.line(
            self.screen, (60, 60, 80),
            (center_x - 200, info_y - 15),
            (center_x + 200, info_y - 15),
            1,
        )

        info_header = hint_font.render("— Game Info —", True, (150, 150, 150))
        self.screen.blit(info_header, (center_x - info_header.get_width() // 2, info_y))

        # Score if available
        if self.current_mode and hasattr(self.current_mode, 'score1') and hasattr(self.current_mode, 'score2'):
            score_text = menu_font.render(
                f"{self.current_mode.score1}  —  {self.current_mode.score2}",
                True, (255, 255, 255)
            )
            self.screen.blit(score_text, (center_x - score_text.get_width() // 2, info_y + 35))

            # Player labels
            p1_label = small_font.render("Player 1", True, (100, 200, 100))
            p2_label = small_font.render("Player 2 / AI", True, (200, 200, 100))
            self.screen.blit(p1_label, (center_x - 100, info_y + 65))
            self.screen.blit(p2_label, (center_x + 20, info_y + 65))

    def _toggle_language(self):
        """Toggle between EN and RU"""
        loc = get_localization()
        if self.current_lang == 'en':
            loc.set_language('ru')
            self.current_lang = 'ru'
        else:
            loc.set_language('en')
            self.current_lang = 'en'

    def handle_events(self) -> bool:
        """Handle all events including menu"""
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                return False

            # Global language toggle
            if event.type == pygame.KEYDOWN and event.key == pygame.K_l:
                self._toggle_language()

            # Handle based on state
            if self.state == GameState.MENU:
                result = self.main_menu.handle_input(event)
                if result == "back":
                    return False  # Quit on ESC from menu

            elif self.state == GameState.SETTINGS:
                result = self.settings_menu.handle_input(event)
                if result == "back":
                    self.state = GameState.MENU

            elif self.state == GameState.CUSTOMIZE:
                result = self.customization_menu.handle_input(event)
                if result == "back":
                    self.state = GameState.MENU

            elif self.state == GameState.STATS:
                result = self.stats_screen.handle_input(event)
                if result == "back":
                    self.state = GameState.MENU

            elif self.state == GameState.PLAYING:
                if not self.current_mode.handle_input(event):
                    return False

                # Handle pause
                if event.type == pygame.KEYDOWN and event.key == pygame.K_ESCAPE:
                    self.state = GameState.PAUSED

            elif self.state == GameState.PAUSED:
                if event.type == pygame.KEYDOWN:
                    if event.key == pygame.K_ESCAPE:
                        self.state = GameState.MENU
                    elif event.key == pygame.K_RETURN:
                        self.state = GameState.PLAYING
                    elif event.key == pygame.K_1:
                        self.state = GameState.PLAYING
                        self.set_mode(GameModeType.CLASSIC)
                        if self.current_mode:
                            self.current_mode.start()
                    elif event.key == pygame.K_2:
                        self.state = GameState.PLAYING
                        self.set_mode(GameModeType.ARCADE)
                        if self.current_mode:
                            self.current_mode.start()
                    # Quick settings controls
                    elif event.key == pygame.K_LEFT:
                        # Decrease music volume
                        current = self.settings.get("music_volume", 0.5)
                        self.settings.set("music_volume", max(0.0, current - 0.1))
                    elif event.key == pygame.K_RIGHT:
                        # Increase music volume
                        current = self.settings.get("music_volume", 0.5)
                        self.settings.set("music_volume", min(1.0, current + 0.1))
                    elif event.key == pygame.K_UP:
                        # Decrease sfx volume
                        current = self.settings.get("sfx_volume", 0.7)
                        self.settings.set("sfx_volume", max(0.0, current - 0.1))
                    elif event.key == pygame.K_DOWN:
                        # Increase sfx volume
                        current = self.settings.get("sfx_volume", 0.7)
                        self.settings.set("sfx_volume", min(1.0, current + 0.1))
                    elif event.key == pygame.K_f:
                        # Toggle FPS display
                        current = self.settings.get("show_fps", False)
                        self.settings.set("show_fps", not current)

            elif self.state == GameState.GAME_OVER:
                if event.type == pygame.KEYDOWN:
                    if event.key == pygame.K_RETURN:
                        self.state = GameState.MENU
                    elif event.key == pygame.K_ESCAPE:
                        self.state = GameState.MENU

        return True

    def update(self):
        """Update based on game state"""
        if self.state == GameState.MENU:
            dt = self.clock.tick(FPS) / 1000.0
            self.main_menu.update(dt)

        elif self.state == GameState.SETTINGS:
            dt = self.clock.tick(FPS) / 1000.0
            self.settings_menu.update(dt)

        elif self.state == GameState.CUSTOMIZE:
            dt = self.clock.tick(FPS) / 1000.0
            # CustomizationMenu doesn't have update yet, but we keep the state handling

        elif self.state == GameState.PLAYING:
            super().update()

            # Check for game over
            if self.current_mode and self.current_mode.game_over:
                self.state = GameState.GAME_OVER

    def draw(self):
        """Draw based on game state"""
        if self.state == GameState.MENU:
            self.main_menu.draw()

        elif self.state == GameState.SETTINGS:
            self.screen.fill((20, 20, 40))
            self.settings_menu.draw()

        elif self.state == GameState.CUSTOMIZE:
            self.customization_menu.draw()

        elif self.state == GameState.STATS:
            self.stats_screen.draw()

        elif self.state == GameState.PLAYING:
            super().draw()

        elif self.state == GameState.PAUSED:
            # Draw game in background
            if self.current_mode:
                self.current_mode.draw()

            # Overlay
            overlay = pygame.Surface((WINDOW_WIDTH, WINDOW_HEIGHT))
            overlay.set_alpha(200)
            overlay.fill((0, 0, 0))
            self.screen.blit(overlay, (0, 0))

            # Pause menu
            self._draw_pause_menu()

        elif self.state == GameState.GAME_OVER:
            # Draw game in background
            if self.current_mode:
                self.current_mode.draw()

            # Overlay
            overlay = pygame.Surface((WINDOW_WIDTH, WINDOW_HEIGHT))
            overlay.set_alpha(200)
            overlay.fill((0, 0, 0))
            self.screen.blit(overlay, (0, 0))

            # Game over text
            loc = get_localization()
            font = pygame.font.SysFont(FONT_NAME, 72)
            text = font.render(loc.get("game.game_over"), True, WHITE)
            rect = text.get_rect(center=(WINDOW_WIDTH // 2, WINDOW_HEIGHT // 2 - 50))
            self.screen.blit(text, rect)

            # Winner
            if self.current_mode:
                winner = self.current_mode.get_winner_name()
                font_small = pygame.font.SysFont(FONT_NAME, 40)
                win_text = font_small.render(winner, True, (255, 215, 0))
                win_rect = win_text.get_rect(center=(WINDOW_WIDTH // 2, WINDOW_HEIGHT // 2 + 10))
                self.screen.blit(win_text, win_rect)

            # Restart hint
            font_hint = pygame.font.SysFont(FONT_NAME, 30)
            hint = font_hint.render(loc.get("game.restart"), True, (150, 150, 150))
            hint_rect = hint.get_rect(center=(WINDOW_WIDTH // 2, WINDOW_HEIGHT // 2 + 60))
            self.screen.blit(hint, hint_rect)

        pygame.display.flip()

    def run(self):
        """Main game loop"""
        while self.running:
            self.running = self.handle_events()
            self.update()
            self.draw()

        pygame.quit()


def main():
    """Entry point"""
    game = GameWithMenu()
    game.run()


if __name__ == "__main__":
    main()
