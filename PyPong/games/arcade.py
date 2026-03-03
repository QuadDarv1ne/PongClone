"""
Arcade game mode - with power-ups and AI
"""
from random import choice, randint

import pygame

from PyPong.core.config import (  # pylint: disable=no-name-in-module
    BLACK,
    DIFFICULTY_LEVELS,
    FONT_NAME,
    GRAY,
    GREEN,
    KEYDOWN,
    KEYUP,
    K_ESCAPE,
    K_a,
    K_DOWN,
    K_UP,
    K_z,
    POWERUP_SPAWN_CHANCE,
    QUIT,
    WHITE,
    WINDOW_HEIGHT,
    WINDOW_WIDTH,
    YELLOW,
)
from PyPong.core.entities import Ball, Paddle, PowerUp

from .base import GameMode, GameModeType


class ArcadeMode(GameMode):
    """
    Arcade mode - includes power-ups and more dynamic gameplay
    """

    def __init__(self, screen: pygame.Surface, settings: dict = None):
        super().__init__(screen, settings)

        self.ai_enabled = self.settings.get("ai_enabled", True)
        self.ai_difficulty = self.settings.get("ai_difficulty", "Medium")

        # Colors
        self.bg_color = GRAY
        self.paddle1_color = GREEN
        self.paddle2_color = YELLOW
        self.ball_color = WHITE

        # Power-ups
        self.powerups = pygame.sprite.Group()
        self.powerup_spawn_chance = self.settings.get("powerup_spawn_chance", POWERUP_SPAWN_CHANCE)

    @property
    def mode_type(self) -> GameModeType:
        return GameModeType.ARCADE

    def init_game_objects(self):
        """Initialize paddles and ball"""
        ai_speed = DIFFICULTY_LEVELS[self.ai_difficulty]["ai_speed"]

        self.paddle1 = Paddle(1, is_ai=False, color=self.paddle1_color)
        self.paddle2 = Paddle(2, is_ai=self.ai_enabled, color=self.paddle2_color)

        if self.ai_enabled:
            self.paddle2.set_speed(ai_speed)

        self.ball = Ball()
        self.ball.image.fill(self.ball_color)

        self.all_sprites = pygame.sprite.Group(self.paddle1, self.paddle2, self.ball)
        self.powerups.empty()

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

            # Player 1 controls
            elif event.key == K_a:
                self.input_state["up1"] = True
            elif event.key == K_z:
                self.input_state["down1"] = True

            # Player 2 controls (PVP)
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

        # Spawn power-ups
        if randint(1, self.powerup_spawn_chance) == 1 and len(self.powerups) == 0:
            powerup = PowerUp()
            self.powerups.add(powerup)

        # Update power-ups
        self.powerups.update()

        # Check power-up collisions
        for powerup in self.powerups:
            if not powerup.active:
                if pygame.sprite.collide_rect(powerup, self.paddle1):
                    self._apply_powerup(powerup, self.paddle1, self.paddle2)
                elif pygame.sprite.collide_rect(powerup, self.paddle2):
                    self._apply_powerup(powerup, self.paddle2, self.paddle1)

    def _apply_powerup(self, powerup: PowerUp, collector: Paddle, opponent: Paddle):
        """Apply power-up effect"""
        powerup.activate(collector)

        if powerup.type == "shrink_opponent":
            opponent.resize(50)
        elif powerup.type == "multi_ball":
            # Create extra ball (simplified - just speed up current)
            self.ball.set_speed(self.ball.speed * 1.2)

    def draw(self):
        """Draw the game"""
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
        self.powerups.draw(self.screen)

        # Pause
        if self.is_paused:
            self._draw_pause()

        # Game over
        if self.game_over:
            self._draw_game_over()

    def _draw_net(self):
        net_x = WINDOW_WIDTH // 2
        for i in range(0, WINDOW_HEIGHT, 60):
            pygame.draw.rect(self.screen, WHITE, (net_x - 2, i, 4, 30))

    def _draw_score(self):
        font = pygame.font.SysFont(FONT_NAME, 120)
        score_text = font.render(self.get_score_display(), True, WHITE, self.bg_color)
        score_rect = score_text.get_rect(centerx=WINDOW_WIDTH // 2, y=10)
        self.screen.blit(score_text, score_rect)

    def _draw_menu(self):
        font_big = pygame.font.SysFont(FONT_NAME, 72)
        font_small = pygame.font.SysFont(FONT_NAME, 40)

        title = font_big.render("ARCADE PONG", True, WHITE, self.bg_color)
        start = font_small.render("Press Enter to Start", True, WHITE, self.bg_color)

        title_rect = title.get_rect(center=(WINDOW_WIDTH // 2, WINDOW_HEIGHT // 2 - 50))
        start_rect = start.get_rect(center=(WINDOW_WIDTH // 2, WINDOW_HEIGHT // 2 + 50))

        self.screen.blit(title, title_rect)
        self.screen.blit(start, start_rect)

    def _draw_pause(self):
        overlay = pygame.Surface((WINDOW_WIDTH, WINDOW_HEIGHT))
        overlay.set_alpha(128)
        overlay.fill(BLACK)
        self.screen.blit(overlay, (0, 0))

        font = pygame.font.SysFont(FONT_NAME, 72)
        text = font.render("PAUSED", True, WHITE)
        rect = text.get_rect(center=(WINDOW_WIDTH // 2, WINDOW_HEIGHT // 2))
        self.screen.blit(text, rect)

    def _draw_game_over(self):
        overlay = pygame.Surface((WINDOW_WIDTH, WINDOW_HEIGHT))
        overlay.set_alpha(180)
        overlay.fill(BLACK)
        self.screen.blit(overlay, (0, 0))

        font_big = pygame.font.SysFont(FONT_NAME, 72)
        font_small = pygame.font.SysFont(FONT_NAME, 50)

        game_over = font_big.render("GAME OVER", True, WHITE)
        winner = font_small.render(self.get_winner_name(), True, YELLOW)

        go_rect = game_over.get_rect(center=(WINDOW_WIDTH // 2, WINDOW_HEIGHT // 2 - 50))
        win_rect = winner.get_rect(center=(WINDOW_WIDTH // 2, WINDOW_HEIGHT // 2 + 25))

        self.screen.blit(game_over, go_rect)
        self.screen.blit(winner, win_rect)

    def start(self):
        self.is_active = True
        self.init_game_objects()

    def stop(self):
        self.is_active = False
