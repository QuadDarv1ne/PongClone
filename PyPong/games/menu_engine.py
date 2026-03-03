"""
Main menu integration with GameEngine
"""
from enum import Enum
from typing import Optional

import pygame

from PyPong.core.config import FONT_NAME, FPS, WHITE, WINDOW_HEIGHT, WINDOW_WIDTH
from PyPong.games.base import GameModeType
from PyPong.games.engine import GameEngine
from PyPong.ui.localization import get_localization, init_localization
from PyPong.ui.menu import MainMenu, Menu, SettingsMenu


class GameState(Enum):
    """Game states"""

    MENU = "menu"
    MODE_SELECT = "mode_select"
    PLAYING = "playing"
    SETTINGS = "settings"
    PAUSED = "paused"
    GAME_OVER = "game_over"


class GameWithMenu(GameEngine):
    """
    Extended GameEngine with beautiful menu system
    """

    def __init__(self) -> None:
        # Initialize localization first
        init_localization("en")

        super().__init__()

        # Menu state
        self.state = GameState.MENU
        self.main_menu: Optional[MainMenu] = None
        self.settings_menu: Optional[SettingsMenu] = None

        # Initialize menus
        self._init_menus()

        # Language toggle
        self.current_lang = "en"

    def _init_menus(self):
        """Initialize all menus"""
        self.main_menu = MainMenu(self.screen)
        self.settings_menu = SettingsMenu(self.screen)

        # Setup menu actions
        self.main_menu.items[0].action = lambda: self._start_game(GameModeType.CLASSIC)
        self.main_menu.items[1].action = lambda: self._start_game(GameModeType.CAMPAIGN)
        self.main_menu.items[2].action = lambda: self._start_game(GameModeType.CAMPAIGN)  # Challenges
        self.main_menu.items[3].action = lambda: self._start_game(GameModeType.MINIGAME)
        self.main_menu.items[4].action = lambda: self._show_stats()
        self.main_menu.items[5].action = lambda: self._open_settings()
        self.main_menu.items[6].action = lambda: setattr(self, "running", False)

    def _start_game(self, mode: GameModeType):
        """Start game in specified mode"""
        self.set_mode(mode)
        if self.current_mode:
            self.current_mode.start()
        self.state = GameState.PLAYING

    def _show_stats(self):
        """Show statistics placeholder"""
        # Stats screen not implemented yet
        pass

    def _open_settings(self):
        """Open settings menu"""
        self.state = GameState.SETTINGS

    def _toggle_language(self):
        """Toggle between EN and RU"""
        loc = get_localization()
        if self.current_lang == "en":
            loc.set_language("ru")
            self.current_lang = "ru"
        else:
            loc.set_language("en")
            self.current_lang = "en"

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

        elif self.state == GameState.PLAYING:
            super().draw()

        elif self.state == GameState.PAUSED:
            # Draw game in background
            if self.current_mode:
                self.current_mode.draw()

            # Overlay
            overlay = pygame.Surface((WINDOW_WIDTH, WINDOW_HEIGHT))
            overlay.set_alpha(180)
            overlay.fill((0, 0, 0))
            self.screen.blit(overlay, (0, 0))

            # Pause text
            loc = get_localization()
            font = pygame.font.SysFont(FONT_NAME, 72)
            text = font.render(loc.get("game.paused"), True, WHITE)
            rect = text.get_rect(center=(WINDOW_WIDTH // 2, WINDOW_HEIGHT // 2 - 50))
            self.screen.blit(text, rect)

            # Resume hint
            font_small = pygame.font.SysFont(FONT_NAME, 30)
            hint = font_small.render(loc.get("game.resume"), True, (150, 150, 150))
            hint_rect = hint.get_rect(center=(WINDOW_WIDTH // 2, WINDOW_HEIGHT // 2 + 20))
            self.screen.blit(hint, hint_rect)

            # Mode switch hints
            mode_hint = font_small.render("Press 1 for Classic, 2 for Arcade", True, (100, 100, 100))
            mode_rect = mode_hint.get_rect(center=(WINDOW_WIDTH // 2, WINDOW_HEIGHT // 2 + 60))
            self.screen.blit(mode_hint, mode_rect)

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
