"""
Multiplayer game mode
"""
import pygame

from PyPong.core.config import (  # pylint: disable=no-name-in-module
    DARK_GRAY,
    FONT_NAME,
    GREEN,
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
    YELLOW,
)
from PyPong.core.entities import Ball, Paddle
from PyPong.games.base import GameMode, GameModeType
from PyPong.systems.multiplayer import (
    ConnectionType,
    GameState,
    LocalPVP,
    MultiplayerBase,
    NetworkClient,
    NetworkHost,
    create_multiplayer,
)
from PyPong.ui.localization import get_localization


class MultiplayerMode(GameMode):
    """
    Multiplayer game mode - supports local PVP and network play
    """

    def __init__(self, screen: pygame.Surface, settings: dict = None):
        super().__init__(screen, settings)

        self.connection_type = self.settings.get("connection_type", "local")
        self.multiplayer: MultiplayerBase = None

        # Network settings
        self.host = self.settings.get("host", "localhost")
        self.port = self.settings.get("port", 9999)

        # Colors
        self.bg_color = DARK_GRAY
        self.paddle1_color = GREEN
        self.paddle2_color = YELLOW
        self.ball_color = WHITE

        # Connection status
        self.waiting_for_connection = False
        self.connection_failed = False

    @property
    def mode_type(self) -> GameModeType:
        return GameModeType.MULTIPLAYER

    def init_game_objects(self):
        """Initialize multiplayer connection and game objects"""
        # Create multiplayer connection
        if self.connection_type == "local":
            self.multiplayer = create_multiplayer("local")
        elif self.connection_type == "host":
            self.multiplayer = NetworkHost(self.port)
            self.waiting_for_connection = True
        elif self.connection_type == "client":
            self.multiplayer = NetworkClient(self.host, self.port)
            self.waiting_for_connection = True

        # Initialize game objects
        self.paddle1 = Paddle(1, is_ai=False, color=self.paddle1_color)
        self.paddle2 = Paddle(2, is_ai=False, color=self.paddle2_color)

        # If network, determine player number
        if isinstance(self.multiplayer, (NetworkHost, NetworkClient)):
            if not self.multiplayer.connect():
                self.connection_failed = True
                return

        self.ball = Ball()
        self.all_sprites = pygame.sprite.Group(self.paddle1, self.paddle2, self.ball)

        self.waiting_for_connection = False

    def handle_input(self, event: pygame.event.Event) -> bool:
        """Handle input for multiplayer"""
        if event.type == QUIT:
            if self.multiplayer:
                self.multiplayer.disconnect()
            return False

        if event.type == KEYDOWN:
            if event.key == K_ESCAPE:
                if self.is_paused:
                    self.is_paused = False
                else:
                    self.pause()
                return True

            # Player 1 controls (A/Z)
            if event.key == K_a:
                self.input_state["up1"] = True
            elif event.key == K_z:
                self.input_state["down1"] = True
            # Player 2 controls (arrows)
            elif event.key == K_UP:
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

        # Handle network input
        if isinstance(self.multiplayer, NetworkHost):
            # Host receives input from client
            remote_input = self.multiplayer.receive_input()  # pylint: disable=assignment-from-none
            if remote_input:
                # Client controls player 2
                self.input_state["up2"] = remote_input.get("up", False)
                self.input_state["down2"] = remote_input.get("down", False)

        elif isinstance(self.multiplayer, NetworkClient):
            # Client sends input to host
            player_num = self.multiplayer.player_number
            if player_num == 1:
                input_data = {"up": self.input_state["up1"], "down": self.input_state["down1"]}
            else:
                input_data = {"up": self.input_state["up2"], "down": self.input_state["down2"]}
            self.multiplayer.send_input(input_data)

            # Receive game state from host
            state = self.multiplayer.receive_game_state()  # pylint: disable=assignment-from-none
            if state:
                self._apply_network_state(state)
                return  # Skip local update, use network state

        # Local update for host or local PVP
        self._update_local(dt)

        # Send game state for network
        if isinstance(self.multiplayer, NetworkHost):
            state = self._create_network_state()
            self.multiplayer.send_game_state(state)

    def _update_local(self, dt: float):
        """Local game update"""
        # Move paddles
        self.paddle1.move(self.input_state["up1"], self.input_state["down1"])
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

    def _create_network_state(self) -> GameState:
        """Create network game state"""
        return GameState(
            paddle1_y=self.paddle1.rect.centery,
            paddle2_y=self.paddle2.rect.centery,
            ball_x=self.ball.rect.centerx,
            ball_y=self.ball.rect.centery,
            ball_vx=self.ball.velocity_x,
            ball_vy=self.ball.velocity_y,
            player1_score=self.player1_score,
            player2_score=self.player2_score,
            game_over=self.game_over,
            winner=self.winner,
        )

    def _apply_network_state(self, state: GameState):
        """Apply received network state"""
        self.paddle1.rect.centery = state.paddle1_y
        self.paddle2.rect.centery = state.paddle2_y
        self.ball.rect.centerx = state.ball_x
        self.ball.rect.centery = state.ball_y
        self.ball.velocity_x = state.ball_vx
        self.ball.velocity_y = state.ball_vy
        self.player1_score = state.player1_score
        self.player2_score = state.player2_score
        self.game_over = state.game_over
        self.winner = state.winner

    def draw(self):
        """Draw the game"""
        self.screen.fill(self.bg_color)

        if not self.is_active:
            self._draw_connecting()
            return

        # Net
        self._draw_net()

        # Score
        self._draw_score()

        # Sprites
        self.all_sprites.draw(self.screen)

        # Pause
        if self.is_paused:
            self._draw_pause()

        # Game over
        if self.game_over:
            self._draw_game_over()

    def _draw_connecting(self):
        """Draw connection screen"""
        font_big = pygame.font.SysFont(FONT_NAME, 48)
        font_small = pygame.font.SysFont(FONT_NAME, 24)

        if self.connection_failed:
            title = font_big.render("Connection Failed", True, (255, 100, 100))
            hint = font_small.render("Press ESC to return to menu", True, WHITE)
        elif self.waiting_for_connection:
            if self.connection_type == "host":
                title = font_big.render("Waiting for player...", True, WHITE)
                hint = font_small.render(f"Port: {self.port}", True, (150, 150, 150))
            else:
                title = font_big.render("Connecting...", True, WHITE)
                hint = font_small.render(f"To: {self.host}:{self.port}", True, (150, 150, 150))
        else:
            title = font_big.render("MULTIPLAYER", True, WHITE)
            hint = font_small.render("Press Enter to Start", True, WHITE)

        title_rect = title.get_rect(center=(WINDOW_WIDTH // 2, WINDOW_HEIGHT // 2 - 30))
        hint_rect = hint.get_rect(center=(WINDOW_WIDTH // 2, WINDOW_HEIGHT // 2 + 30))

        self.screen.blit(title, title_rect)
        self.screen.blit(hint, hint_rect)

    def _draw_net(self):
        net_x = WINDOW_WIDTH // 2
        for i in range(0, WINDOW_HEIGHT, 60):
            pygame.draw.rect(self.screen, WHITE, (net_x - 2, i, 4, 30))

    def _draw_score(self):
        font = pygame.font.SysFont(FONT_NAME, 120)
        score_text = font.render(self.get_score_display(), True, WHITE, self.bg_color)
        score_rect = score_text.get_rect(centerx=WINDOW_WIDTH // 2, y=10)
        self.screen.blit(score_text, score_rect)

    def _draw_pause(self):
        loc = get_localization()
        font = pygame.font.SysFont(FONT_NAME, 72)
        text = font.render(loc.get("game.paused"), True, WHITE)
        rect = text.get_rect(center=(WINDOW_WIDTH // 2, WINDOW_HEIGHT // 2))
        self.screen.blit(text, rect)

    def _draw_game_over(self):
        loc = get_localization()
        font_big = pygame.font.SysFont(FONT_NAME, 72)
        font_small = pygame.font.SysFont(FONT_NAME, 50)

        game_over = font_big.render(loc.get("game.game_over"), True, WHITE)
        winner = font_small.render(self.get_winner_name(), True, YELLOW)

        go_rect = game_over.get_rect(center=(WINDOW_WIDTH // 2, WINDOW_HEIGHT // 2 - 50))
        win_rect = winner.get_rect(center=(WINDOW_WIDTH // 2, WINDOW_HEIGHT // 2 + 25))

        self.screen.blit(game_over, go_rect)
        self.screen.blit(winner, win_rect)

    def start(self):
        """Start the game"""
        self.is_active = True
        if not self.multiplayer:
            self.init_game_objects()

    def stop(self):
        """Stop the game and disconnect"""
        self.is_active = False
        if self.multiplayer:
            self.multiplayer.disconnect()
