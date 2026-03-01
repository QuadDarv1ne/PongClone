import pygame
from enum import Enum
from config import *

class GameState(Enum):
    MENU = 1
    PLAYING = 2
    PAUSED = 3
    GAME_OVER = 4

class GameStateManager:
    def __init__(self, screen):
        self.screen = screen
        self.state = GameState.MENU
        self.player1_score = 0
        self.player2_score = 0
        self.winner = None
        self.difficulty = "Medium"
        
        # Fonts
        self.title_font = pygame.font.SysFont(FONT_NAME, 72)
        self.menu_font = pygame.font.SysFont(FONT_NAME, 40)
        self.score_font = pygame.font.SysFont(FONT_NAME, 120)

    def reset_scores(self):
        self.player1_score = 0
        self.player2_score = 0
        self.winner = None

    def add_score(self, player):
        if player == 1:
            self.player1_score += 1
        else:
            self.player2_score += 1

        if self.player1_score >= WINNING_SCORE:
            self.winner = 1
            self.state = GameState.GAME_OVER
        elif self.player2_score >= WINNING_SCORE:
            self.winner = 2
            self.state = GameState.GAME_OVER

    def set_difficulty(self, difficulty):
        if difficulty in DIFFICULTY_LEVELS:
            self.difficulty = difficulty

    def draw_menu(self):
        self.screen.fill(GRAY)
        
        title = self.title_font.render("Enhanced Pong", True, WHITE)
        start = self.menu_font.render("Press ENTER to Start", True, WHITE)
        diff_text = self.menu_font.render(f"Difficulty: {self.difficulty} (1/2/3)", True, WHITE)
        controls = self.menu_font.render("Controls: A/Z - Player 1", True, WHITE)
        
        self.screen.blit(title, title.get_rect(center=(WINDOW_WIDTH // 2, 200)))
        self.screen.blit(start, start.get_rect(center=(WINDOW_WIDTH // 2, 350)))
        self.screen.blit(diff_text, diff_text.get_rect(center=(WINDOW_WIDTH // 2, 450)))
        self.screen.blit(controls, controls.get_rect(center=(WINDOW_WIDTH // 2, 550)))

    def draw_pause(self):
        overlay = pygame.Surface((WINDOW_WIDTH, WINDOW_HEIGHT))
        overlay.set_alpha(128)
        overlay.fill(BLACK)
        self.screen.blit(overlay, (0, 0))
        
        pause = self.title_font.render("PAUSED", True, WHITE)
        resume = self.menu_font.render("Press ENTER to Resume", True, WHITE)
        quit_text = self.menu_font.render("Press ESC to Quit", True, WHITE)
        
        self.screen.blit(pause, pause.get_rect(center=(WINDOW_WIDTH // 2, 250)))
        self.screen.blit(resume, resume.get_rect(center=(WINDOW_WIDTH // 2, 350)))
        self.screen.blit(quit_text, quit_text.get_rect(center=(WINDOW_WIDTH // 2, 450)))

    def draw_game_over(self):
        self.screen.fill(GRAY)
        
        game_over = self.title_font.render("GAME OVER", True, WHITE)
        winner_text = self.menu_font.render(f"Player {self.winner} Wins!", True, WHITE)
        restart = self.menu_font.render("Press ENTER to Restart", True, WHITE)
        
        self.screen.blit(game_over, game_over.get_rect(center=(WINDOW_WIDTH // 2, 250)))
        self.screen.blit(winner_text, winner_text.get_rect(center=(WINDOW_WIDTH // 2, 350)))
        self.screen.blit(restart, restart.get_rect(center=(WINDOW_WIDTH // 2, 450)))

    def draw_score(self):
        score_text = self.score_font.render(
            f"{self.player1_score}   {self.player2_score}", 
            True, WHITE
        )
        self.screen.blit(score_text, score_text.get_rect(centerx=WINDOW_WIDTH // 2, y=10))

    def draw_net(self):
        for i in range(0, WINDOW_HEIGHT, 60):
            pygame.draw.rect(self.screen, WHITE, (WINDOW_WIDTH // 2 - 2, i, 4, 30))
