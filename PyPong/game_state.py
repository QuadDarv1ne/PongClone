import pygame
from enum import Enum
from config import *

class GameState(Enum):
    MENU = 1
    MODE_SELECT = 2
    PLAYING = 3
    PAUSED = 4
    GAME_OVER = 5
    STATS = 6
    SETTINGS = 7
    TOURNAMENT_COMPLETE = 8

class GameStateManager:
    def __init__(self, screen):
        self.screen = screen
        self.state = GameState.MENU
        self.player1_score = 0
        self.player2_score = 0
        self.winner = None
        self.difficulty = "Medium"
        self.game_mode = "ai"
        self.tournament_mode = False
        
        # Fonts
        self.title_font = pygame.font.SysFont(FONT_NAME, 72)
        self.menu_font = pygame.font.SysFont(FONT_NAME, 40)
        self.score_font = pygame.font.SysFont(FONT_NAME, 120)
        self.small_font = pygame.font.SysFont(FONT_NAME, 30)

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
        stats_text = self.small_font.render("Press S for Stats | Press O for Settings", True, WHITE)
        
        self.screen.blit(title, title.get_rect(center=(WINDOW_WIDTH // 2, 250)))
        self.screen.blit(start, start.get_rect(center=(WINDOW_WIDTH // 2, 400)))
        self.screen.blit(stats_text, stats_text.get_rect(center=(WINDOW_WIDTH // 2, 620)))

    def draw_mode_select(self):
        self.screen.fill(GRAY)
        
        title = self.title_font.render("Select Mode", True, WHITE)
        ai_text = self.menu_font.render("1. vs AI", True, YELLOW if self.game_mode == "ai" else WHITE)
        pvp_text = self.menu_font.render("2. Player vs Player", True, YELLOW if self.game_mode == "pvp" else WHITE)
        tournament_text = self.small_font.render(
            f"Tournament: {'ON (Best of 3)' if self.tournament_mode else 'OFF'} (Press T)", 
            True, GREEN if self.tournament_mode else WHITE
        )
        diff_text = self.small_font.render(f"AI Difficulty: {self.difficulty} (3/4/5)", True, WHITE)
        controls_ai = self.small_font.render("Controls: A/Z - Player 1", True, WHITE)
        controls_pvp = self.small_font.render("Controls: A/Z - Player 1 | Arrows - Player 2", True, WHITE)
        start = self.menu_font.render("Press ENTER to Start", True, GREEN)
        
        self.screen.blit(title, title.get_rect(center=(WINDOW_WIDTH // 2, 120)))
        self.screen.blit(ai_text, ai_text.get_rect(center=(WINDOW_WIDTH // 2, 240)))
        self.screen.blit(pvp_text, pvp_text.get_rect(center=(WINDOW_WIDTH // 2, 300)))
        self.screen.blit(tournament_text, tournament_text.get_rect(center=(WINDOW_WIDTH // 2, 370)))
        
        if self.game_mode == "ai":
            self.screen.blit(diff_text, diff_text.get_rect(center=(WINDOW_WIDTH // 2, 450)))
            self.screen.blit(controls_ai, controls_ai.get_rect(center=(WINDOW_WIDTH // 2, 510)))
        else:
            self.screen.blit(controls_pvp, controls_pvp.get_rect(center=(WINDOW_WIDTH // 2, 480)))
        
        self.screen.blit(start, start.get_rect(center=(WINDOW_WIDTH // 2, 600)))

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

    def draw_stats(self, stats_manager):
        self.screen.fill(GRAY)
        
        title = self.title_font.render("Statistics", True, WHITE)
        games = self.menu_font.render(f"Games Played: {stats_manager.stats['games_played']}", True, WHITE)
        p1_wins = self.menu_font.render(f"Player 1 Wins: {stats_manager.stats['player1_wins']}", True, WHITE)
        p2_wins = self.menu_font.render(f"Player 2 Wins: {stats_manager.stats['player2_wins']}", True, WHITE)
        high_score = self.menu_font.render(f"Highest Score: {stats_manager.stats['highest_score']}", True, WHITE)
        total_goals = self.menu_font.render(f"Total Goals: {stats_manager.stats['total_goals']}", True, WHITE)
        back = self.small_font.render("Press ESC to go back", True, WHITE)
        
        self.screen.blit(title, title.get_rect(center=(WINDOW_WIDTH // 2, 100)))
        self.screen.blit(games, games.get_rect(center=(WINDOW_WIDTH // 2, 220)))
        self.screen.blit(p1_wins, p1_wins.get_rect(center=(WINDOW_WIDTH // 2, 300)))
        self.screen.blit(p2_wins, p2_wins.get_rect(center=(WINDOW_WIDTH // 2, 380)))
        self.screen.blit(high_score, high_score.get_rect(center=(WINDOW_WIDTH // 2, 460)))
        self.screen.blit(total_goals, total_goals.get_rect(center=(WINDOW_WIDTH // 2, 540)))
        self.screen.blit(back, back.get_rect(center=(WINDOW_WIDTH // 2, 640)))
