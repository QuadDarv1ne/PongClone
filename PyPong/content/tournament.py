from typing import Optional

import pygame

from PyPong.core.config import FONT_NAME, WHITE, WINDOW_HEIGHT, WINDOW_WIDTH


class Tournament:
    def __init__(self) -> None:
        self.mode = "best_of_3"  # best_of_3 or best_of_5
        self.player1_wins = 0
        self.player2_wins = 0
        self.current_game = 1
        self.winner: Optional[int] = None
        self.font = pygame.font.SysFont(FONT_NAME, 36)
        self.small_font = pygame.font.SysFont(FONT_NAME, 24)

    def reset(self) -> None:
        self.player1_wins = 0
        self.player2_wins = 0
        self.current_game = 1
        self.winner = None

    def record_game_win(self, winner):
        if winner == 1:
            self.player1_wins += 1
        else:
            self.player2_wins += 1

        self.current_game += 1

        # Check tournament winner
        target = 2 if self.mode == "best_of_3" else 3
        if self.player1_wins >= target:
            self.winner = 1
        elif self.player2_wins >= target:
            self.winner = 2

    def is_complete(self):
        return self.winner is not None

    def get_games_needed(self):
        return 3 if self.mode == "best_of_3" else 5

    def draw_status(self, screen):
        # Tournament status bar
        status_text = f"Tournament: Game {self.current_game} | P1: {self.player1_wins} | P2: {self.player2_wins}"
        text = self.small_font.render(status_text, True, WHITE)
        screen.blit(text, (WINDOW_WIDTH // 2 - text.get_width() // 2, WINDOW_HEIGHT - 40))

    def draw_winner_screen(self, screen):
        screen.fill(GRAY)

        title = self.font.render("TOURNAMENT COMPLETE!", True, WHITE)
        winner_text = self.font.render(f"Player {self.winner} Wins the Tournament!", True, YELLOW)
        score_text = self.small_font.render(f"Final Score: {self.player1_wins} - {self.player2_wins}", True, WHITE)
        restart = self.small_font.render("Press ENTER to return to menu", True, WHITE)

        screen.blit(title, title.get_rect(center=(WINDOW_WIDTH // 2, 200)))
        screen.blit(winner_text, winner_text.get_rect(center=(WINDOW_WIDTH // 2, 300)))
        screen.blit(score_text, score_text.get_rect(center=(WINDOW_WIDTH // 2, 400)))
        screen.blit(restart, restart.get_rect(center=(WINDOW_WIDTH // 2, 500)))
