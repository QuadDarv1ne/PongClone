"""Enhanced statistics screen with detailed match history"""
import pygame
from typing import List, Dict, Any, Optional
from datetime import datetime

from PyPong.core.config import FONT_NAME, WINDOW_WIDTH, WINDOW_HEIGHT
from PyPong.ui.localization import t
from PyPong.systems.stats import StatsManager


class StatsScreen:
    """Enhanced statistics screen with detailed information"""

    def __init__(self, screen: pygame.Surface, stats_manager: StatsManager) -> None:
        self.screen = screen
        self.stats = stats_manager

        # Fonts
        self.title_font = pygame.font.SysFont(FONT_NAME, 44, bold=True)
        self.font = pygame.font.SysFont(FONT_NAME, 30)
        self.small_font = pygame.font.SysFont(FONT_NAME, 24)
        self.tiny_font = pygame.font.SysFont(FONT_NAME, 18)

        # State
        self.scroll_offset = 0
        self.max_visible_items = 8
        self.selected_tab = 0
        self.tabs = ["overview", "history", "records"]

    def draw(self) -> None:
        """Draw the statistics screen"""
        self.screen.fill((15, 15, 25))

        # Title
        title = self.title_font.render(t("stats.title"), True, (100, 200, 255))
        title_rect = title.get_rect(center=(WINDOW_WIDTH // 2, 30))
        self.screen.blit(title, title_rect)

        # Tabs
        self._draw_tabs()

        # Content based on selected tab
        if self.tabs[self.selected_tab] == "overview":
            self._draw_overview()
        elif self.tabs[self.selected_tab] == "history":
            self._draw_history()
        elif self.tabs[self.selected_tab] == "records":
            self._draw_records()

        # Bottom hint
        self._draw_hints()

    def _draw_tabs(self) -> None:
        """Draw tab buttons"""
        tab_width = 250
        tab_height = 32
        tab_y = 80
        total_width = tab_width * len(self.tabs)
        start_x = (WINDOW_WIDTH - total_width) // 2

        tab_labels = [
            t("stats.tab_overview"),
            t("stats.tab_history"),
            t("stats.tab_records"),
        ]

        for i, label in enumerate(tab_labels):
            x = start_x + i * tab_width
            is_active = (i == self.selected_tab)

            color = (60, 120, 180) if is_active else (40, 40, 50)
            pygame.draw.rect(self.screen, color, (x, tab_y, tab_width - 4, tab_height), border_radius=6)

            if is_active:
                pygame.draw.rect(self.screen, (100, 200, 255), (x, tab_y, tab_width - 4, tab_height), 2, border_radius=6)

            text = self.small_font.render(label, True, (255, 255, 255) if is_active else (150, 150, 150))
            text_rect = text.get_rect(center=(x + tab_width // 2 - 2, tab_y + tab_height // 2))
            self.screen.blit(text, text_rect)

    def _draw_overview(self) -> None:
        """Draw overview statistics"""
        s = self.stats.stats
        y = 130

        # Main stats cards
        cards = [
            (t("stats.games_played").format(s.get("games_played", 0)), (100, 200, 255)),
            (t("stats.total_goals").format(s.get("total_goals", 0)), (255, 200, 100)),
            (t("stats.highest_score").format(s.get("highest_score", 0)), (255, 100, 100)),
        ]

        card_width = 280
        card_height = 70
        spacing = 20
        total_width = card_width * 3 + spacing * 2
        start_x = (WINDOW_WIDTH - total_width) // 2

        for i, (text, color) in enumerate(cards):
            x = start_x + i * (card_width + spacing)

            # Card background
            pygame.draw.rect(self.screen, (30, 30, 40), (x, y, card_width, card_height), border_radius=8)
            pygame.draw.rect(self.screen, color, (x, y, card_width, card_height), 2, border_radius=8)

            # Text
            text_surf = self.font.render(text, True, (255, 255, 255))
            text_rect = text_surf.get_rect(center=(x + card_width // 2, y + card_height // 2))
            self.screen.blit(text_surf, text_rect)

        # Win rate section
        y += 100
        section_header = self.font.render(t("stats.win_rates"), True, (150, 150, 150))
        self.screen.blit(section_header, (WINDOW_WIDTH // 2 - section_header.get_width() // 2, y))

        y += 50
        p1_wins = s.get("player1_wins", 0)
        p2_wins = s.get("player2_wins", 0)
        total_games = s.get("games_played", 0)

        p1_rate = (p1_wins / total_games * 100) if total_games > 0 else 0
        p2_rate = (p2_wins / total_games * 100) if total_games > 0 else 0

        # Player 1 stats
        self._draw_player_stat(WINDOW_WIDTH // 2 - 200, y, "Player 1", p1_wins, p1_rate, (100, 200, 100))

        # Player 2 stats
        self._draw_player_stat(WINDOW_WIDTH // 2 + 50, y, "Player 2 / AI", p2_wins, p2_rate, (200, 200, 100))

        # Additional stats
        y += 120
        additional_stats = [
            (t("stats.best_streak").format(s.get("best_streak", 0)), (150, 150, 150)),
            (t("stats.longest_rally").format(s.get("longest_rally", 0)), (150, 150, 150)),
            (t("stats.powerups_collected").format(s.get("powerups_collected", 0)), (150, 150, 150)),
        ]

        for label, color in additional_stats:
            text_surf = self.small_font.render(label, True, color)
            self.screen.blit(text_surf, (WINDOW_WIDTH // 2 - text_surf.get_width() // 2, y))
            y += 35

    def _draw_player_stat(self, x: int, y: int, player_name: str, wins: int, win_rate: float, color: tuple) -> None:
        """Draw player statistics card"""
        card_w = 280
        card_h = 80

        # Card background
        pygame.draw.rect(self.screen, (30, 30, 40), (x, y, card_w, card_h), border_radius=8)
        pygame.draw.rect(self.screen, color, (x, y, card_w, card_h), 2, border_radius=8)

        # Player name
        name_surf = self.small_font.render(player_name, True, color)
        self.screen.blit(name_surf, (x + 20, y + 10))

        # Wins
        wins_surf = self.font.render(f"Wins: {wins}", True, (255, 255, 255))
        self.screen.blit(wins_surf, (x + 20, y + 40))

        # Win rate bar
        bar_x = x + 160
        bar_w = 100
        bar_h = 12
        pygame.draw.rect(self.screen, (40, 40, 40), (bar_x, y + 45, bar_w, bar_h), border_radius=4)
        fill_w = int(bar_w * win_rate / 100)
        pygame.draw.rect(self.screen, color, (bar_x, y + 45, fill_w, bar_h), border_radius=4)

        # Win rate percentage
        pct_surf = self.small_font.render(f"{win_rate:.0f}%", True, (255, 255, 255))
        self.screen.blit(pct_surf, (bar_x + 10, y + 42))

    def _draw_history(self) -> None:
        """Draw match history"""
        history = self.stats.stats.get("match_history", [])

        if not history:
            no_history = self.font.render(t("stats.no_history"), True, (100, 100, 100))
            self.screen.blit(no_history, (WINDOW_WIDTH // 2 - no_history.get_width() // 2, 150))
            return

        # Table header
        header_y = 130
        headers = [
            (t("stats.date"), 80),
            (t("stats.mode"), 100),
            (t("stats.score"), 80),
            (t("stats.winner"), 100),
            (t("stats.duration"), 80),
        ]

        x_offset = 50
        for header, width in headers:
            header_surf = self.small_font.render(header, True, (150, 200, 255))
            self.screen.blit(header_surf, (x_offset, header_y))
            x_offset += width + 10

        # Separator line
        pygame.draw.line(self.screen, (60, 80, 100), (50, header_y + 30), (WINDOW_WIDTH - 50, header_y + 30), 2)

        # History rows
        row_y = header_y + 45
        row_height = 32

        for i, match in enumerate(history):
            y = row_y + i * row_height
            if y > WINDOW_HEIGHT - 80:
                break

            # Alternate row colors
            if i % 2 == 1:
                pygame.draw.rect(self.screen, (25, 25, 35), (50, y - 5, WINDOW_WIDTH - 100, row_height))

            x_offset = 50
            values = [
                match.get("date", "")[:10],  # Just the date part
                match.get("mode", "classic").title(),
                match.get("score", "0-0"),
                f"Player {match.get('winner', '?')}",
                f"{match.get('duration', 0)}s",
            ]

            for value, (header, width) in zip(values, headers):
                color = (255, 255, 255)
                # Highlight winner
                if header == t("stats.winner"):
                    color = (255, 220, 100)

                val_surf = self.tiny_font.render(value, True, color)
                self.screen.blit(val_surf, (x_offset, y))
                x_offset += width + 10

    def _draw_records(self) -> None:
        """Draw records and achievements"""
        s = self.stats.stats
        y = 140

        records = [
            ("Highest Score", str(s.get("highest_score", 0)), (255, 200, 100)),
            ("Best Streak", str(s.get("best_streak", 0)), (100, 200, 255)),
            ("Longest Rally", f"{s.get('longest_rally', 0)} hits", (100, 255, 100)),
            ("Total Playtime", f"{s.get('total_playtime', 0) // 60} min", (255, 100, 255)),
            ("Power-Ups Collected", str(s.get('powerups_collected', 0)), (255, 150, 100)),
            ("Achievements", f"{s.get('achievements_unlocked', 0)}", (200, 200, 100)),
        ]

        for label, value, color in records:
            # Label
            label_surf = self.font.render(label, True, (150, 150, 150))
            self.screen.blit(label_surf, (WINDOW_WIDTH // 2 - 200, y))

            # Value
            value_surf = self.font.render(value, True, color)
            self.screen.blit(value_surf, (WINDOW_WIDTH // 2 + 100, y))

            # Separator
            pygame.draw.line(self.screen, (40, 40, 50), (WINDOW_WIDTH // 2 - 200, y + 35), (WINDOW_WIDTH // 2 + 200, y + 35))

            y += 50

    def _draw_hints(self) -> None:
        """Draw control hints"""
        hint_font = pygame.font.SysFont(FONT_NAME, 18)
        hints = [
            ("←→", t("stats.hint_tabs")),
            ("Esc", t("misc.back")),
        ]

        y = WINDOW_HEIGHT - 35
        for i, (key, action) in enumerate(hints):
            text = f"{key}: {action}"
            surf = hint_font.render(text, True, (100, 100, 100))
            x = 20 + i * 200
            self.screen.blit(surf, (x, y))

    def handle_input(self, event: pygame.event.Event) -> Optional[str]:
        """Handle input. Returns 'back' to exit."""
        if event.type != pygame.KEYDOWN:
            return None

        if event.key == pygame.K_ESCAPE:
            return "back"

        if event.key == pygame.K_LEFT:
            self.selected_tab = max(0, self.selected_tab - 1)

        elif event.key == pygame.K_RIGHT:
            self.selected_tab = min(len(self.tabs) - 1, self.selected_tab + 1)

        return None
