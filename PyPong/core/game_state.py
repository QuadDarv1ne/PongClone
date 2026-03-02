"""
Game state management with state machine pattern
"""
from typing import Optional, TYPE_CHECKING
import pygame
from enum import Enum
from PyPong.core.config import (
    WHITE, BLACK, GRAY, LIGHT_BLUE, RED, GREEN, YELLOW,
    FONT_NAME, WINDOW_WIDTH, WINDOW_HEIGHT, WINNING_SCORE,
    DIFFICULTY_LEVELS,
)

if TYPE_CHECKING:
    from PyPong.systems.stats import StatsManager


class GameState(Enum):
    """Enumeration of all game states"""
    MENU = 1
    MODE_SELECT = 2
    PLAYING = 3
    PAUSED = 4
    GAME_OVER = 5
    STATS = 6
    SETTINGS = 7
    TOURNAMENT_COMPLETE = 8
    CAMPAIGN_SELECT = 9
    CAMPAIGN_PLAYING = 10
    CAMPAIGN_COMPLETE = 11
    CHALLENGES = 12
    MINIGAME_SELECT = 13
    MINIGAME_PLAYING = 14
    MINIGAME_COMPLETE = 15
    HELP = 16


class GameStateManager:
    """Manages game state transitions and rendering"""
    
    def __init__(
        self, 
        screen: pygame.Surface, 
        game_surface: Optional[pygame.Surface] = None
    ):
        self.screen = screen
        self.game_surface = game_surface if game_surface else screen
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
        
        # Пре-рендер сетки для производительности
        self._net_surface = self._create_net_surface()

    def reset_scores(self) -> None:
        """Сбросить очки"""
        self.player1_score = 0
        self.player2_score = 0
        self.winner = None

    def add_score(self, player: int) -> None:
        """Добавить очко игроку"""
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

    def set_difficulty(self, difficulty: str) -> None:
        """Установить сложность"""
        if difficulty in DIFFICULTY_LEVELS:
            self.difficulty = difficulty

    def draw_menu(self) -> None:
        """Отрисовать главное меню"""
        self.game_surface.fill(GRAY)

        title = self.title_font.render("Enhanced Pong", True, WHITE)
        start = self.menu_font.render("Press ENTER to Start", True, WHITE)
        campaign = self.small_font.render("Press C for Campaign", True, YELLOW)
        challenges = self.small_font.render("Press H for Challenges", True, GREEN)
        minigames = self.small_font.render("Press M for Mini-Games", True, LIGHT_BLUE)
        stats_text = self.small_font.render("Press S for Stats | Press O for Settings | Press F1 for Help", True, WHITE)

        self.game_surface.blit(title, title.get_rect(center=(WINDOW_WIDTH // 2, 180)))
        self.game_surface.blit(start, start.get_rect(center=(WINDOW_WIDTH // 2, 300)))
        self.game_surface.blit(campaign, campaign.get_rect(center=(WINDOW_WIDTH // 2, 380)))
        self.game_surface.blit(challenges, challenges.get_rect(center=(WINDOW_WIDTH // 2, 430)))
        self.game_surface.blit(minigames, minigames.get_rect(center=(WINDOW_WIDTH // 2, 480)))
        self.game_surface.blit(stats_text, stats_text.get_rect(center=(WINDOW_WIDTH // 2, 620)))

    def draw_mode_select(self) -> None:
        """Отрисовать выбор режима игры"""
        self.game_surface.fill(GRAY)

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

        self.game_surface.blit(title, title.get_rect(center=(WINDOW_WIDTH // 2, 120)))
        self.game_surface.blit(ai_text, ai_text.get_rect(center=(WINDOW_WIDTH // 2, 240)))
        self.game_surface.blit(pvp_text, pvp_text.get_rect(center=(WINDOW_WIDTH // 2, 300)))
        self.game_surface.blit(tournament_text, tournament_text.get_rect(center=(WINDOW_WIDTH // 2, 370)))

        if self.game_mode == "ai":
            self.game_surface.blit(diff_text, diff_text.get_rect(center=(WINDOW_WIDTH // 2, 450)))
            self.game_surface.blit(controls_ai, controls_ai.get_rect(center=(WINDOW_WIDTH // 2, 510)))
        else:
            self.game_surface.blit(controls_pvp, controls_pvp.get_rect(center=(WINDOW_WIDTH // 2, 480)))

        self.game_surface.blit(start, start.get_rect(center=(WINDOW_WIDTH // 2, 600)))

    def draw_pause(self) -> None:
        """Отрисовать экран паузы"""
        overlay = pygame.Surface((WINDOW_WIDTH, WINDOW_HEIGHT))
        overlay.set_alpha(128)
        overlay.fill(BLACK)
        self.game_surface.blit(overlay, (0, 0))
        
        pause = self.title_font.render("PAUSED", True, WHITE)
        resume = self.menu_font.render("Press ENTER to Resume", True, WHITE)
        quit_text = self.menu_font.render("Press ESC to Quit", True, WHITE)
        
        self.game_surface.blit(pause, pause.get_rect(center=(WINDOW_WIDTH // 2, 250)))
        self.game_surface.blit(resume, resume.get_rect(center=(WINDOW_WIDTH // 2, 350)))
        self.game_surface.blit(quit_text, quit_text.get_rect(center=(WINDOW_WIDTH // 2, 450)))

    def draw_game_over(self) -> None:
        """Отрисовать экран конца игры"""
        self.game_surface.fill(GRAY)
        
        game_over = self.title_font.render("GAME OVER", True, WHITE)
        winner_text = self.menu_font.render(f"Player {self.winner} Wins!", True, WHITE)
        restart = self.menu_font.render("Press ENTER to Restart", True, WHITE)
        
        self.game_surface.blit(game_over, game_over.get_rect(center=(WINDOW_WIDTH // 2, 250)))
        self.game_surface.blit(winner_text, winner_text.get_rect(center=(WINDOW_WIDTH // 2, 350)))
        self.game_surface.blit(restart, restart.get_rect(center=(WINDOW_WIDTH // 2, 450)))

    def draw_score(self) -> None:
        """Отрисовать счёт"""
        score_text = self.score_font.render(
            f"{self.player1_score}   {self.player2_score}", 
            True, WHITE
        )
        self.game_surface.blit(score_text, score_text.get_rect(centerx=WINDOW_WIDTH // 2, y=10))

    def _create_net_surface(self) -> pygame.Surface:
        """Создать пре-рендерную поверхность сетки"""
        net = pygame.Surface((4, WINDOW_HEIGHT), pygame.SRCALPHA)
        for i in range(0, WINDOW_HEIGHT, 60):
            pygame.draw.rect(net, WHITE, (0, i, 4, 30))
        return net

    def draw_net(self) -> None:
        """Отрисовать сетку (blit вместо draw каждый кадр)"""
        self.game_surface.blit(self._net_surface, (WINDOW_WIDTH // 2 - 2, 0))

    def draw_stats(self, stats_manager: "StatsManager") -> None:
        """Отрисовать статистику"""
        self.game_surface.fill(GRAY)
        
        title = self.title_font.render("Statistics", True, WHITE)
        games = self.menu_font.render(f"Games Played: {stats_manager.stats['games_played']}", True, WHITE)
        p1_wins = self.menu_font.render(f"Player 1 Wins: {stats_manager.stats['player1_wins']}", True, WHITE)
        p2_wins = self.menu_font.render(f"Player 2 Wins: {stats_manager.stats['player2_wins']}", True, WHITE)
        high_score = self.menu_font.render(f"Highest Score: {stats_manager.stats['highest_score']}", True, WHITE)
        total_goals = self.menu_font.render(f"Total Goals: {stats_manager.stats['total_goals']}", True, WHITE)
        back = self.small_font.render("Press ESC to go back", True, WHITE)
        
        self.game_surface.blit(title, title.get_rect(center=(WINDOW_WIDTH // 2, 100)))
        self.game_surface.blit(games, games.get_rect(center=(WINDOW_WIDTH // 2, 220)))
        self.game_surface.blit(p1_wins, p1_wins.get_rect(center=(WINDOW_WIDTH // 2, 300)))
        self.game_surface.blit(p2_wins, p2_wins.get_rect(center=(WINDOW_WIDTH // 2, 380)))
        self.game_surface.blit(high_score, high_score.get_rect(center=(WINDOW_WIDTH // 2, 460)))
        self.game_surface.blit(total_goals, total_goals.get_rect(center=(WINDOW_WIDTH // 2, 540)))
        self.game_surface.blit(back, back.get_rect(center=(WINDOW_WIDTH // 2, 640)))

    def draw_help(self) -> None:
        """Отрисовать справку"""
        self.game_surface.fill(GRAY)

        title = self.title_font.render("How to Play", True, WHITE)
        
        # Player 1 controls
        p1_title = self.menu_font.render("Player 1 (Left)", True, GREEN)
        p1_up = self.small_font.render("A - Move Up", True, WHITE)
        p1_down = self.small_font.render("Z - Move Down", True, WHITE)
        
        # Player 2 controls
        p2_title = self.menu_font.render("Player 2 (Right / AI)", True, YELLOW)
        p2_up = self.small_font.render("UP Arrow - Move Up", True, WHITE)
        p2_down = self.small_font.render("DOWN Arrow - Move Down", True, WHITE)
        
        # General controls
        gen_title = self.menu_font.render("General Controls", True, LIGHT_BLUE)
        gen_start = self.small_font.render("ENTER - Start / Resume", True, WHITE)
        gen_pause = self.small_font.render("ESCAPE - Pause / Back", True, WHITE)
        gen_stats = self.small_font.render("S - Statistics (from Menu)", True, WHITE)
        gen_settings = self.small_font.render("O - Settings (from Menu)", True, WHITE)
        
        # Power-ups info
        power_title = self.menu_font.render("Power-Ups", True, (255, 165, 0))
        power_speed = self.small_font.render("Green - Speed Boost (faster paddle)", True, WHITE)
        power_large = self.small_font.render("Yellow - Large Paddle (bigger racket)", True, WHITE)
        power_slow = self.small_font.render("Blue - Slow Ball (slower ball speed)", True, WHITE)
        
        # Objective
        obj_title = self.menu_font.render("Objective", True, WHITE)
        obj_text = self.small_font.render(f"First to {WINNING_SCORE} points wins!", True, WHITE)
        obj_tip = self.small_font.render("Tip: Hit the ball with the edge of your paddle for angled shots!", True, (200, 200, 200))
        
        back = self.small_font.render("Press ESC to go back", True, WHITE)

        # Blit all text
        self.game_surface.blit(title, title.get_rect(center=(WINDOW_WIDTH // 2, 60)))
        
        self.game_surface.blit(p1_title, p1_title.get_rect(center=(WINDOW_WIDTH // 4, 130)))
        self.game_surface.blit(p1_up, p1_up.get_rect(center=(WINDOW_WIDTH // 4, 170)))
        self.game_surface.blit(p1_down, p1_down.get_rect(center=(WINDOW_WIDTH // 4, 200)))
        
        self.game_surface.blit(p2_title, p2_title.get_rect(center=(3 * WINDOW_WIDTH // 4, 130)))
        self.game_surface.blit(p2_up, p2_up.get_rect(center=(3 * WINDOW_WIDTH // 4, 170)))
        self.game_surface.blit(p2_down, p2_down.get_rect(center=(3 * WINDOW_WIDTH // 4, 200)))
        
        self.game_surface.blit(gen_title, gen_title.get_rect(center=(WINDOW_WIDTH // 2, 260)))
        self.game_surface.blit(gen_start, gen_start.get_rect(center=(WINDOW_WIDTH // 2, 300)))
        self.game_surface.blit(gen_pause, gen_pause.get_rect(center=(WINDOW_WIDTH // 2, 330)))
        self.game_surface.blit(gen_stats, gen_stats.get_rect(center=(WINDOW_WIDTH // 2, 360)))
        self.game_surface.blit(gen_settings, gen_settings.get_rect(center=(WINDOW_WIDTH // 2, 390)))
        
        self.game_surface.blit(power_title, power_title.get_rect(center=(WINDOW_WIDTH // 2, 450)))
        self.game_surface.blit(power_speed, power_speed.get_rect(center=(WINDOW_WIDTH // 2, 485)))
        self.game_surface.blit(power_large, power_large.get_rect(center=(WINDOW_WIDTH // 2, 515)))
        self.game_surface.blit(power_slow, power_slow.get_rect(center=(WINDOW_WIDTH // 2, 545)))
        
        self.game_surface.blit(obj_title, obj_title.get_rect(center=(WINDOW_WIDTH // 2, 590)))
        self.game_surface.blit(obj_text, obj_text.get_rect(center=(WINDOW_WIDTH // 2, 625)))
        self.game_surface.blit(obj_tip, obj_tip.get_rect(center=(WINDOW_WIDTH // 2, 660)))
        
        self.game_surface.blit(back, back.get_rect(center=(WINDOW_WIDTH // 2, WINDOW_HEIGHT - 30)))
