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
from PyPong.ui.localization import t

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
    GOAL_CELEBRATION = 17
    ONBOARDING = 18


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

        # Onboarding
        self.onboarding_slide = 0
        self.onboarding_total_slides = 4

        # Fonts
        self.title_font = pygame.font.SysFont(FONT_NAME, 72)
        self.menu_font = pygame.font.SysFont(FONT_NAME, 40)
        self.score_font = pygame.font.SysFont(FONT_NAME, 120)
        self.small_font = pygame.font.SysFont(FONT_NAME, 30)
        
        # Пре-рендер сетки для производительности
        self._net_surface = self._create_net_surface()

    def on_resize(self, screen_width: int, screen_height: int) -> None:
        """Regenerate fonts and net surface proportionally after window resize."""
        scale_x = screen_width / WINDOW_WIDTH
        scale_y = screen_height / WINDOW_HEIGHT
        scale = min(scale_x, scale_y)
        self.title_font = pygame.font.SysFont(FONT_NAME, int(72 * scale))
        self.menu_font = pygame.font.SysFont(FONT_NAME, int(40 * scale))
        self.score_font = pygame.font.SysFont(FONT_NAME, int(120 * scale))
        self.small_font = pygame.font.SysFont(FONT_NAME, int(30 * scale))
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
            self.state = GameState.GOAL_CELEBRATION
        elif self.player2_score >= WINNING_SCORE:
            self.winner = 2
            self.state = GameState.GOAL_CELEBRATION

    def set_difficulty(self, difficulty: str) -> None:
        """Установить сложность"""
        if difficulty in DIFFICULTY_LEVELS:
            self.difficulty = difficulty

    def draw_menu(self) -> None:
        """Отрисовать главное меню"""
        self.game_surface.fill(GRAY)

        title = self.title_font.render(t("menu.title"), True, WHITE)
        start = self.menu_font.render(t("menu.start"), True, WHITE)
        campaign = self.small_font.render(t("menu.campaign"), True, YELLOW)
        challenges = self.small_font.render(t("menu.challenges"), True, GREEN)
        minigames = self.small_font.render(t("menu.minigames"), True, LIGHT_BLUE)
        stats_text = self.small_font.render(
            f"{t('menu.stats')} | {t('menu.settings')} | {t('menu.help')}",
            True, WHITE
        )

        self.game_surface.blit(title, title.get_rect(center=(WINDOW_WIDTH // 2, 180)))
        self.game_surface.blit(start, start.get_rect(center=(WINDOW_WIDTH // 2, 300)))
        self.game_surface.blit(campaign, campaign.get_rect(center=(WINDOW_WIDTH // 2, 380)))
        self.game_surface.blit(challenges, challenges.get_rect(center=(WINDOW_WIDTH // 2, 430)))
        self.game_surface.blit(minigames, minigames.get_rect(center=(WINDOW_WIDTH // 2, 480)))
        self.game_surface.blit(stats_text, stats_text.get_rect(center=(WINDOW_WIDTH // 2, 620)))

    def draw_mode_select(self) -> None:
        """Отрисовать выбор режима игры"""
        self.game_surface.fill(GRAY)

        title = self.title_font.render(t("mode.select_title"), True, WHITE)
        ai_text = self.menu_font.render(t("mode.ai"), True, YELLOW if self.game_mode == "ai" else WHITE)
        pvp_text = self.menu_font.render(t("mode.pvp"), True, YELLOW if self.game_mode == "pvp" else WHITE)
        
        tournament_key = "mode.tournament_on" if self.tournament_mode else "mode.tournament_off"
        tournament_text = self.small_font.render(t(tournament_key), True, GREEN if self.tournament_mode else WHITE)
        
        diff_text = self.small_font.render(t("mode.difficulty").format(self.difficulty), True, WHITE)
        controls_ai = self.small_font.render(t("mode.controls_ai"), True, WHITE)
        controls_pvp = self.small_font.render(t("mode.controls_pvp"), True, WHITE)
        start = self.menu_font.render(t("mode.start"), True, GREEN)

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

        pause = self.title_font.render(t("game.paused"), True, WHITE)
        resume = self.menu_font.render(t("game.resume"), True, WHITE)
        quit_text = self.menu_font.render(t("game.quit_to_menu"), True, WHITE)

        self.game_surface.blit(pause, pause.get_rect(center=(WINDOW_WIDTH // 2, 250)))
        self.game_surface.blit(resume, resume.get_rect(center=(WINDOW_WIDTH // 2, 350)))
        self.game_surface.blit(quit_text, quit_text.get_rect(center=(WINDOW_WIDTH // 2, 450)))

    def draw_game_over(self) -> None:
        """Отрисовать экран конца игры"""
        self.game_surface.fill(GRAY)

        game_over = self.title_font.render(t("game.game_over"), True, WHITE)
        winner_text = self.menu_font.render(t("game.winner").format(self.winner), True, WHITE)
        restart = self.menu_font.render(t("game.restart"), True, WHITE)

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

        title = self.title_font.render(t("stats.title"), True, WHITE)
        games = self.menu_font.render(t("stats.games_played").format(stats_manager.stats['games_played']), True, WHITE)
        p1_wins = self.menu_font.render(t("stats.player1_wins").format(stats_manager.stats['player1_wins']), True, WHITE)
        p2_wins = self.menu_font.render(t("stats.player2_wins").format(stats_manager.stats['player2_wins']), True, WHITE)
        high_score = self.menu_font.render(t("stats.highest_score").format(stats_manager.stats['highest_score']), True, WHITE)
        total_goals = self.menu_font.render(t("stats.total_goals").format(stats_manager.stats['total_goals']), True, WHITE)
        back = self.small_font.render(t("stats.back"), True, WHITE)

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

        title = self.title_font.render(t("help.title"), True, WHITE)

        # Player 1 controls
        p1_title = self.menu_font.render(t("help.player1_title"), True, GREEN)
        p1_up = self.small_font.render(t("help.player1_up"), True, WHITE)
        p1_down = self.small_font.render(t("help.player1_down"), True, WHITE)

        # Player 2 controls
        p2_title = self.menu_font.render(t("help.player2_title"), True, YELLOW)
        p2_up = self.small_font.render(t("help.player2_up"), True, WHITE)
        p2_down = self.small_font.render(t("help.player2_down"), True, WHITE)

        # General controls
        gen_title = self.menu_font.render(t("help.general_title"), True, LIGHT_BLUE)
        gen_start = self.small_font.render(t("help.general_start"), True, WHITE)
        gen_pause = self.small_font.render(t("help.general_pause"), True, WHITE)
        gen_stats = self.small_font.render(t("help.general_stats"), True, WHITE)
        gen_settings = self.small_font.render(t("help.general_settings"), True, WHITE)

        # Power-ups info
        power_title = self.menu_font.render(t("help.powerups_title"), True, (255, 165, 0))
        power_speed = self.small_font.render(t("help.powerups_speed"), True, WHITE)
        power_large = self.small_font.render(t("help.powerups_large"), True, WHITE)
        power_slow = self.small_font.render(t("help.powerups_slow"), True, WHITE)
        power_multi = self.small_font.render(t("help.powerups_multi"), True, WHITE)
        power_shrink = self.small_font.render(t("help.powerups_shrink"), True, WHITE)
        power_invisible = self.small_font.render(t("help.powerups_invisible"), True, WHITE)
        power_reverse = self.small_font.render(t("help.powerups_reverse"), True, WHITE)
        power_shield = self.small_font.render(t("help.powerups_shield"), True, WHITE)
        power_freeze = self.small_font.render(t("help.powerups_freeze"), True, WHITE)
        power_magnet = self.small_font.render(t("help.powerups_magnet"), True, WHITE)

        # Objective
        obj_title = self.menu_font.render(t("help.objective_title"), True, WHITE)
        obj_text = self.small_font.render(t("help.objective_text").format(WINNING_SCORE), True, WHITE)
        obj_tip = self.small_font.render(t("help.objective_tip"), True, (200, 200, 200))

        back = self.small_font.render(t("help.back"), True, WHITE)

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

        self.game_surface.blit(power_title, power_title.get_rect(center=(WINDOW_WIDTH // 2, 420)))
        # Left column
        self.game_surface.blit(power_speed, power_speed.get_rect(center=(WINDOW_WIDTH // 3, 460)))
        self.game_surface.blit(power_large, power_large.get_rect(center=(WINDOW_WIDTH // 3, 488)))
        self.game_surface.blit(power_slow, power_slow.get_rect(center=(WINDOW_WIDTH // 3, 516)))
        self.game_surface.blit(power_multi, power_multi.get_rect(center=(WINDOW_WIDTH // 3, 544)))
        self.game_surface.blit(power_shrink, power_shrink.get_rect(center=(WINDOW_WIDTH // 3, 572)))
        # Right column
        self.game_surface.blit(power_invisible, power_invisible.get_rect(center=(2 * WINDOW_WIDTH // 3, 460)))
        self.game_surface.blit(power_reverse, power_reverse.get_rect(center=(2 * WINDOW_WIDTH // 3, 488)))
        self.game_surface.blit(power_shield, power_shield.get_rect(center=(2 * WINDOW_WIDTH // 3, 516)))
        self.game_surface.blit(power_freeze, power_freeze.get_rect(center=(2 * WINDOW_WIDTH // 3, 544)))
        self.game_surface.blit(power_magnet, power_magnet.get_rect(center=(2 * WINDOW_WIDTH // 3, 572)))

        self.game_surface.blit(obj_title, obj_title.get_rect(center=(WINDOW_WIDTH // 2, 610)))
        self.game_surface.blit(obj_text, obj_text.get_rect(center=(WINDOW_WIDTH // 2, 640)))
        self.game_surface.blit(obj_tip, obj_tip.get_rect(center=(WINDOW_WIDTH // 2, 665)))

        self.game_surface.blit(back, back.get_rect(center=(WINDOW_WIDTH // 2, WINDOW_HEIGHT - 30)))

    def draw_onboarding(self) -> None:
        """Отрисовать экран обучения"""
        self.game_surface.fill(GRAY)

        slide = self.onboarding_slide

        if slide == 0:
            self._draw_slide_welcome()
        elif slide == 1:
            self._draw_slide_controls()
        elif slide == 2:
            self._draw_slide_powerups()
        elif slide == 3:
            self._draw_slide_ready()

        # Slide counter
        progress = self.small_font.render(
            t("onboarding.progress").format(slide + 1, self.onboarding_total_slides),
            True, (150, 150, 150)
        )
        self.game_surface.blit(progress, progress.get_rect(center=(WINDOW_WIDTH // 2, WINDOW_HEIGHT - 60)))

        # Navigation hints
        if slide < self.onboarding_total_slides - 1:
            next_text = self.small_font.render(t("onboarding.next"), True, WHITE)
            self.game_surface.blit(next_text, next_text.get_rect(center=(WINDOW_WIDTH // 2, WINDOW_HEIGHT - 30)))
        else:
            start_text = self.small_font.render(t("onboarding.start"), True, GREEN)
            self.game_surface.blit(start_text, start_text.get_rect(center=(WINDOW_WIDTH // 2, WINDOW_HEIGHT - 30)))

        skip_text = self.small_font.render(t("onboarding.skip"), True, (150, 150, 150))
        self.game_surface.blit(skip_text, skip_text.get_rect(center=(WINDOW_WIDTH // 2, WINDOW_HEIGHT - 10)))

    def _draw_slide_welcome(self) -> None:
        """Slide 1: Welcome"""
        title = self.title_font.render(t("onboarding.slide_1_title"), True, WHITE)
        c1 = self.small_font.render(t("onboarding.slide_1_content_1"), True, WHITE)
        c2 = self.small_font.render(t("onboarding.slide_1_content_2"), True, WHITE)
        c3 = self.small_font.render(t("onboarding.slide_1_content_3"), True, WHITE)

        self.game_surface.blit(title, title.get_rect(center=(WINDOW_WIDTH // 2, 150)))
        self.game_surface.blit(c1, c1.get_rect(center=(WINDOW_WIDTH // 2, 280)))
        self.game_surface.blit(c2, c2.get_rect(center=(WINDOW_WIDTH // 2, 340)))
        self.game_surface.blit(c3, c3.get_rect(center=(WINDOW_WIDTH // 2, 400)))

    def _draw_slide_controls(self) -> None:
        """Slide 2: Controls (two-column)"""
        title = self.title_font.render(t("onboarding.slide_2_title"), True, WHITE)

        p1_title = self.menu_font.render(t("help.player1_title"), True, GREEN)
        p1_up = self.small_font.render(t("help.player1_up"), True, WHITE)
        p1_down = self.small_font.render(t("help.player1_down"), True, WHITE)

        p2_title = self.menu_font.render(t("help.player2_title"), True, YELLOW)
        p2_up = self.small_font.render(t("help.player2_up"), True, WHITE)
        p2_down = self.small_font.render(t("help.player2_down"), True, WHITE)

        gen_start = self.small_font.render(t("help.general_start"), True, WHITE)
        gen_pause = self.small_font.render(t("help.general_pause"), True, WHITE)

        self.game_surface.blit(title, title.get_rect(center=(WINDOW_WIDTH // 2, 80)))

        self.game_surface.blit(p1_title, p1_title.get_rect(center=(WINDOW_WIDTH // 4, 180)))
        self.game_surface.blit(p1_up, p1_up.get_rect(center=(WINDOW_WIDTH // 4, 230)))
        self.game_surface.blit(p1_down, p1_down.get_rect(center=(WINDOW_WIDTH // 4, 270)))

        self.game_surface.blit(p2_title, p2_title.get_rect(center=(3 * WINDOW_WIDTH // 4, 180)))
        self.game_surface.blit(p2_up, p2_up.get_rect(center=(3 * WINDOW_WIDTH // 4, 230)))
        self.game_surface.blit(p2_down, p2_down.get_rect(center=(3 * WINDOW_WIDTH // 4, 270)))

        self.game_surface.blit(gen_start, gen_start.get_rect(center=(WINDOW_WIDTH // 2, 370)))
        self.game_surface.blit(gen_pause, gen_pause.get_rect(center=(WINDOW_WIDTH // 2, 410)))

    def _draw_slide_powerups(self) -> None:
        """Slide 3: Power-ups (two-column)"""
        title = self.title_font.render(t("onboarding.slide_3_title"), True, (255, 165, 0))

        p_speed = self.small_font.render(t("help.powerups_speed"), True, WHITE)
        p_large = self.small_font.render(t("help.powerups_large"), True, WHITE)
        p_slow = self.small_font.render(t("help.powerups_slow"), True, WHITE)
        p_multi = self.small_font.render(t("help.powerups_multi"), True, WHITE)
        p_shrink = self.small_font.render(t("help.powerups_shrink"), True, WHITE)

        p_invis = self.small_font.render(t("help.powerups_invisible"), True, WHITE)
        p_reverse = self.small_font.render(t("help.powerups_reverse"), True, WHITE)
        p_shield = self.small_font.render(t("help.powerups_shield"), True, WHITE)
        p_freeze = self.small_font.render(t("help.powerups_freeze"), True, WHITE)
        p_magnet = self.small_font.render(t("help.powerups_magnet"), True, WHITE)

        self.game_surface.blit(title, title.get_rect(center=(WINDOW_WIDTH // 2, 100)))

        self.game_surface.blit(p_speed, p_speed.get_rect(center=(WINDOW_WIDTH // 3, 200)))
        self.game_surface.blit(p_large, p_large.get_rect(center=(WINDOW_WIDTH // 3, 250)))
        self.game_surface.blit(p_slow, p_slow.get_rect(center=(WINDOW_WIDTH // 3, 300)))
        self.game_surface.blit(p_multi, p_multi.get_rect(center=(WINDOW_WIDTH // 3, 350)))
        self.game_surface.blit(p_shrink, p_shrink.get_rect(center=(WINDOW_WIDTH // 3, 400)))

        self.game_surface.blit(p_invis, p_invis.get_rect(center=(2 * WINDOW_WIDTH // 3, 200)))
        self.game_surface.blit(p_reverse, p_reverse.get_rect(center=(2 * WINDOW_WIDTH // 3, 250)))
        self.game_surface.blit(p_shield, p_shield.get_rect(center=(2 * WINDOW_WIDTH // 3, 300)))
        self.game_surface.blit(p_freeze, p_freeze.get_rect(center=(2 * WINDOW_WIDTH // 3, 350)))
        self.game_surface.blit(p_magnet, p_magnet.get_rect(center=(2 * WINDOW_WIDTH // 3, 400)))

    def _draw_slide_ready(self) -> None:
        """Slide 4: Ready to Play"""
        title = self.title_font.render(t("onboarding.slide_4_title"), True, GREEN)
        c1 = self.small_font.render(t("onboarding.slide_4_content_1"), True, WHITE)
        c2 = self.small_font.render(t("onboarding.slide_4_content_2"), True, WHITE)
        c3 = self.small_font.render(t("onboarding.slide_4_content_3"), True, WHITE)

        self.game_surface.blit(title, title.get_rect(center=(WINDOW_WIDTH // 2, 200)))
        self.game_surface.blit(c1, c1.get_rect(center=(WINDOW_WIDTH // 2, 320)))
        self.game_surface.blit(c2, c2.get_rect(center=(WINDOW_WIDTH // 2, 380)))
        self.game_surface.blit(c3, c3.get_rect(center=(WINDOW_WIDTH // 2, 440)))
