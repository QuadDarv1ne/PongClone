"""
Classic game mode - basic pong gameplay
"""
import pygame

from PyPong.core.config import (
    BLACK,
    DIFFICULTY_LEVELS,
    FONT_NAME,
    KEYDOWN,
    KEYUP,
    K_ESCAPE,
    K_a,
    K_DOWN,
    K_UP,
    K_z,
    QUIT,
    WHITE,
    WINDOW_HEIGHT,
    WINDOW_WIDTH,
)
from PyPong.core.entities import Ball, Paddle

from .base import GameMode, GameModeType


class ClassicMode(GameMode):
    """
    Classic pong mode - simple 1v1 or vs AI
    First to winning_score wins
    """

    def __init__(self, screen: pygame.Surface, settings: dict = None):
        super().__init__(screen, settings)

        self.ai_enabled = self.settings.get("ai_enabled", False)
        self.ai_difficulty = self.settings.get("ai_difficulty", "Medium")

        # Colors
        self.bg_color = BLACK
        self.paddle1_color = WHITE
        self.paddle2_color = WHITE
        self.ball_color = WHITE
        self.net_color = WHITE

    @property
    def mode_type(self) -> GameModeType:
        return GameModeType.CLASSIC

    def init_game_objects(self):
        """Initialize paddles and ball"""
        ai_speed = DIFFICULTY_LEVELS[self.ai_difficulty]["ai_speed"]

        self.paddle1 = Paddle(1, is_ai=False, color=self.paddle1_color)
        self.paddle2 = Paddle(2, is_ai=self.ai_enabled, color=self.paddle2_color)

        if self.ai_enabled:
            self.paddle2.set_speed(ai_speed)

        self.ball = Ball()
        self.all_sprites = pygame.sprite.Group(self.paddle1, self.paddle2, self.ball)

    def handle_input(self, event: pygame.event.Event) -> bool:
        """Handle keyboard input"""
        if event.type == QUIT:
            return False

        if event.type == KEYDOWN:
            if event.key == K_ESCAPE:
                if self.is_paused:
                    self.is_paused = False
                else:
                    self.pause()

            # Player 1 controls (A/Z)
            elif event.key == K_a:
                self.input_state["up1"] = True
            elif event.key == K_z:
                self.input_state["down1"] = True

            # Player 2 controls (arrows) - only in PVP
            elif not self.ai_enabled:
                if event.key == K_UP:
                    self.input_state["up2"] = True
                elif event.key == K_DOWN:
                    self.input_state["down2"] = True

        elif event.type == KEYUP:
            if event.key == K_a:
                self.input_state["up1"] = False
            elif event.key == K_z:
                self.input_state["down1"] = False
            elif event.key == K_UP:
                self.input_state["up2"] = False
            elif event.key == K_DOWN:
                self.input_state["down2"] = False

        return True

    def update(self, dt: float):
        """Update game logic"""
        if not self.is_active or self.is_paused or self.game_over:
            return

        # Move paddles
        self.paddle1.move(self.input_state["up1"], self.input_state["down1"])

        if self.ai_enabled:
            # AI uses prediction
            predicted_y = self.paddle2.predict_ball_position(
                self.ball.rect.centerx, self.ball.rect.centery, self.ball.velocity_x, self.ball.velocity_y
            )
            self.paddle2.move(False, False, predicted_y)
        else:
            self.paddle2.move(self.input_state["up2"], self.input_state["down2"])

        # Move ball
        self.ball.move()
        self.ball.bounce_wall()

        # Paddle collisions
        if pygame.sprite.collide_rect(self.ball, self.paddle1):
            self.ball.bounce_paddle(self.paddle1)

        if pygame.sprite.collide_rect(self.ball, self.paddle2):
            self.ball.bounce_paddle(self.paddle2)

        # Scoring
        if self.ball.is_out_left():
            self.add_score(2)
            self.ball.reset_ball()

        if self.ball.is_out_right():
            self.add_score(1)
            self.ball.reset_ball()

    def draw(self):
        """Draw the game"""
        # Background
        self.screen.fill(self.bg_color)

        if not self.is_active:
            self._draw_menu()
            return

        # Net
        self._draw_net()

        # Score
        self._draw_score()

        # Sprites
        self.all_sprites.draw(self.screen)

        # Pause overlay
        if self.is_paused:
            self._draw_pause()

        # Game over
        if self.game_over:
            self._draw_game_over()

    def _draw_net(self):
        """Draw center net"""
        net_x = WINDOW_WIDTH // 2
        for i in range(0, WINDOW_HEIGHT, 60):
            pygame.draw.rect(self.screen, self.net_color, (net_x - 2, i, 4, 30))

    def _draw_score(self):
        """Draw score display"""
        font = pygame.font.SysFont(FONT_NAME, 120)
        score_text = font.render(self.get_score_display(), True, self.ball_color, self.bg_color)
        score_rect = score_text.get_rect(centerx=WINDOW_WIDTH // 2, y=10)
        self.screen.blit(score_text, score_rect)

    def _draw_menu(self):
        """Draw start menu"""
        font_big = pygame.font.SysFont(FONT_NAME, 72)
        font_small = pygame.font.SysFont(FONT_NAME, 40)

        title = font_big.render("CLASSIC PONG", True, WHITE, BLACK)
        start = font_small.render("Press Enter to Start", True, WHITE, BLACK)

        title_rect = title.get_rect(center=(WINDOW_WIDTH // 2, WINDOW_HEIGHT // 2 - 50))
        start_rect = start.get_rect(center=(WINDOW_WIDTH // 2, WINDOW_HEIGHT // 2 + 50))

        self.screen.blit(title, title_rect)
        self.screen.blit(start, start_rect)

    def _draw_pause(self):
        """Draw pause overlay"""
        font = pygame.font.SysFont(FONT_NAME, 72)
        text = font.render("PAUSED", True, WHITE, GRAY)
        rect = text.get_rect(center=(WINDOW_WIDTH // 2, WINDOW_HEIGHT // 2))
        self.screen.blit(text, rect)

    def _draw_game_over(self):
        """Draw game over screen"""
        font_big = pygame.font.SysFont(FONT_NAME, 72)
        font_small = pygame.font.SysFont(FONT_NAME, 50)

        game_over = font_big.render("GAME OVER", True, WHITE, BLACK)
        winner = font_small.render(self.get_winner_name(), True, WHITE, BLACK)

        go_rect = game_over.get_rect(center=(WINDOW_WIDTH // 2, WINDOW_HEIGHT // 2 - 50))
        win_rect = winner.get_rect(center=(WINDOW_WIDTH // 2, WINDOW_HEIGHT // 2 + 25))

        self.screen.blit(game_over, go_rect)
        self.screen.blit(winner, win_rect)

    def start(self):
        """Start the game"""
        self.is_active = True
        self.init_game_objects()

    def stop(self):
        """Stop the game"""
        self.is_active = False
