import pygame
import sys
from pygame.locals import *
from random import randint

from PyPong.core.config import (
    WINDOW_WIDTH, WINDOW_HEIGHT, FPS,
    WHITE, BLACK, GRAY, LIGHT_BLUE, RED, GREEN, YELLOW,
    PADDLE_WIDTH, PADDLE_HEIGHT, PADDLE_SPEED, PADDLE_OFFSET,
    BALL_SIZE, BALL_INITIAL_SPEED, BALL_SPEED_INCREASE, MAX_BALL_SPEED,
    WINNING_SCORE, POWERUP_DURATION, POWERUP_SPAWN_CHANCE,
    DIFFICULTY_LEVELS, FONT_NAME,
    MAX_PARTICLES, MAX_TRAILS, PARTICLES_PER_HIT, TRAIL_SPAWN_CHANCE,
    SHAKE_INTENSITY_NORMAL, SHAKE_INTENSITY_GOAL,
)
from PyPong.core.entities import Paddle, Ball, PowerUp
from PyPong.core.game_state import GameState, GameStateManager
from PyPong.systems.audio import AudioManager
from PyPong.ui.effects import Particle, Trail, ScreenShake, GoalAnimation
from PyPong.systems.stats import StatsManager
from PyPong.systems.settings import Settings
from PyPong.ui.ui import PowerUpIndicator, FPSCounter, SettingsMenu
from PyPong.content.tournament import Tournament
from PyPong.ui.themes import get_theme
from PyPong.gamepad import GamepadManager
from PyPong.mobile import TouchControls, AdaptiveScreen

class PongGame:
    def __init__(self):
        pygame.init()
        self.settings = Settings()
        
        # Detect platform
        self.is_mobile = self._detect_mobile()
        
        # Setup display
        if self.is_mobile:
            # Mobile: start with fullscreen and touch controls enabled
            self.settings.set("fullscreen", True)
            self.settings.set("touch_controls", True)
            flags = pygame.FULLSCREEN
        else:
            flags = pygame.FULLSCREEN if self.settings.get("fullscreen", False) else pygame.RESIZABLE
        
        self.screen = pygame.display.set_mode((WINDOW_WIDTH, WINDOW_HEIGHT), flags)
        self.game_surface = pygame.Surface((WINDOW_WIDTH, WINDOW_HEIGHT))
        pygame.display.set_caption("Enhanced Pong")
        self.clock = pygame.time.Clock()
        
        # Adaptive screen
        self.adaptive_screen = AdaptiveScreen()
        
        # Theme
        self.theme = get_theme(self.settings.get("theme", "classic"))
        
        # Managers
        self.state_manager = GameStateManager(self.screen, self.game_surface)
        self.audio = AudioManager()
        self.stats = StatsManager()
        self.tournament = Tournament()
        self.gamepad = GamepadManager()
        self.touch = TouchControls(WINDOW_WIDTH, WINDOW_HEIGHT)
        
        # UI
        self.powerup_indicator = PowerUpIndicator()
        self.fps_counter = FPSCounter()
        self.settings_menu = SettingsMenu(self.game_surface, self.settings)
        
        # Effects
        self.particles = pygame.sprite.Group()
        self.trails = pygame.sprite.Group()
        self.shake = ScreenShake()
        self.goal_anim = GoalAnimation()

        # Apply settings
        self.apply_settings()
        self.apply_theme()

        # Input state
        self.input_state = {
            "up1": False,
            "down1": False,
            "up2": False,
            "down2": False,
        }

        # Game objects (инициализируются при старте игры)
        self._init_game_objects()

    def _handle_escape(self) -> None:
        """Обработать нажатие ESC"""
        state = self.state_manager.state
        transitions = {
            GameState.PLAYING: GameState.PAUSED,
            GameState.PAUSED: GameState.MENU,
            GameState.STATS: GameState.MENU,
            GameState.SETTINGS: GameState.MENU,
            GameState.HELP: GameState.MENU,
            GameState.MODE_SELECT: GameState.MENU,
        }
        
        new_state = transitions.get(state)
        if new_state:
            self.state_manager.state = new_state
            if new_state == GameState.MENU:
                self._cleanup_game_objects()
        else:
            # Quit from menu
            raise SystemExit()

    def _handle_enter(self) -> None:
        """Обработать нажатие ENTER"""
        state = self.state_manager.state
        transitions = {
            GameState.MENU: GameState.MODE_SELECT,
            GameState.MODE_SELECT: GameState.PLAYING,
            GameState.PAUSED: GameState.PLAYING,
            GameState.GAME_OVER: GameState.MENU,
            GameState.TOURNAMENT_COMPLETE: GameState.MENU,
        }
        
        new_state = transitions.get(state)
        if new_state:
            self.state_manager.state = new_state
            if new_state == GameState.PLAYING:
                self.audio.play_music()
            elif new_state == GameState.MENU:
                if state == GameState.GAME_OVER:
                    self._cleanup_game_objects()
                    self.state_manager.reset_scores()
                elif state == GameState.TOURNAMENT_COMPLETE:
                    self.tournament.reset()

    def _handle_mode_select_keys(self, key: int) -> None:
        """Обработать клавиши выбора режима"""
        if self.state_manager.state != GameState.MODE_SELECT:
            return
            
        if key == K_1:
            self.state_manager.game_mode = "ai"
        elif key == K_2:
            self.state_manager.game_mode = "pvp"
        elif key == K_3:
            self.state_manager.set_difficulty("Easy")
        elif key == K_4:
            self.state_manager.set_difficulty("Medium")
        elif key == K_t:
            self.state_manager.tournament_mode = not self.state_manager.tournament_mode
            if self.state_manager.tournament_mode:
                self.tournament.reset()
                self.state_manager.set_difficulty("Hard")

    def _handle_movement_input(self, key: int, is_pressed: bool) -> None:
        """Обработать ввод движения"""
        key_map = {
            K_a: ("up1", is_pressed),
            K_z: ("down1", is_pressed),
            K_UP: ("up2", is_pressed),
            K_DOWN: ("down2", is_pressed),
        }
        
        if key in key_map:
            action, value = key_map[key]
            self.input_state[action] = value

    def _detect_mobile(self):
        """Detect if running on mobile platform"""
        try:
            import platform
            system = platform.system().lower()
            # Check for Android
            if system == 'linux':
                try:
                    with open('/proc/version', 'r') as f:
                        if 'android' in f.read().lower():
                            return True
                except (IOError, OSError):
                    pass
            return False
        except Exception:
            return False

    def apply_settings(self):
        pygame.mixer.music.set_volume(self.settings.get("music_volume", 0.5))
        for sound in self.audio.sounds.values():
            sound.set_volume(self.settings.get("sfx_volume", 0.7))
        
        # Check fullscreen toggle
        if self.settings.get("fullscreen", False):
            self.screen = pygame.display.set_mode((WINDOW_WIDTH, WINDOW_HEIGHT), pygame.FULLSCREEN)
        else:
            if not self.is_mobile:
                self.screen = pygame.display.set_mode((WINDOW_WIDTH, WINDOW_HEIGHT), pygame.RESIZABLE)
            else:
                self.screen = pygame.display.set_mode((WINDOW_WIDTH, WINDOW_HEIGHT), pygame.FULLSCREEN)
        
        # Check theme change
        new_theme = get_theme(self.settings.get("theme", "classic"))
        if new_theme.name != self.theme.name:
            self.theme = new_theme
            self.apply_theme()

    def apply_theme(self):
        if hasattr(self, 'paddle1') and self.paddle1:
            self.paddle1.color = self.theme.paddle1_color
            self.paddle1.image.fill(self.theme.paddle1_color)
        if hasattr(self, 'paddle2') and self.paddle2:
            self.paddle2.color = self.theme.paddle2_color
            self.paddle2.image.fill(self.theme.paddle2_color)
        if hasattr(self, 'ball') and self.ball:
            self.ball.image.fill(self.theme.ball_color)

    def _init_game_objects(self):
        """Инициализировать игровые объекты"""
        self.paddle1 = None
        self.paddle2 = None
        self.ball = None
        self.all_sprites = None
        self.powerups = None

    def init_game_objects(self):
        is_ai = self.state_manager.game_mode == "ai"
        self.paddle1 = Paddle(1, is_ai=False, color=self.theme.paddle1_color)
        self.paddle2 = Paddle(2, is_ai=is_ai, color=self.theme.paddle2_color)
        self.ball = Ball()
        self.ball.image.fill(self.theme.ball_color)
        self.all_sprites = pygame.sprite.Group(self.paddle1, self.paddle2, self.ball)
        self.powerups = pygame.sprite.Group()

        # Set AI difficulty
        if is_ai:
            difficulty = self.state_manager.difficulty
            self.paddle2.set_speed(DIFFICULTY_LEVELS[difficulty]["ai_speed"])
        
        # Сброс input state при инициализации
        self.input_state = {
            "up1": False,
            "down1": False,
            "up2": False,
            "down2": False,
        }

    def reset_game(self):
        """Сбросить игру к начальному состоянию"""
        self.state_manager.reset_scores()
        self._init_game_objects()

    def _cleanup_game_objects(self):
        """Очистить игровые объекты"""
        if self.all_sprites:
            self.all_sprites.empty()
        if self.powerups:
            self.powerups.empty()
        if self.particles:
            self.particles.empty()
        if self.trails:
            self.trails.empty()
        self._init_game_objects()

    def handle_events(self) -> bool:
        """
        Обработать события pygame.
        
        Returns:
            bool: True если игра должна продолжаться, False для выхода
        """
        for event in pygame.event.get():
            if event.type == QUIT:
                return False

            # Handle window resize
            if event.type == pygame.VIDEORESIZE:
                if not self.is_mobile:
                    self.adaptive_screen.update_resolution(event.w, event.h)
                    self.screen = pygame.display.set_mode((event.w, event.h), pygame.RESIZABLE)

            # Touch controls
            if event.type in (pygame.MOUSEBUTTONDOWN, pygame.MOUSEBUTTONUP):
                if self.settings.get("touch_controls", False):
                    self.touch.handle_touch(event)

            # Settings menu input
            if self.state_manager.state == GameState.SETTINGS:
                result = self.settings_menu.handle_input(event)
                if result == "back":
                    self.state_manager.state = GameState.MENU
                    self.apply_settings()
                continue

            if event.type == KEYDOWN:
                self._handle_keydown(event.key)
            elif event.type == KEYUP:
                self._handle_keyup(event.key)

        return True

    def _handle_keydown(self, key: int) -> None:
        """Обработать нажатие клавиши"""
        if key == K_ESCAPE:
            try:
                self._handle_escape()
            except SystemExit:
                raise
        
        elif key == K_RETURN:
            self._handle_enter()
        
        elif self.state_manager.state == GameState.MENU:
            if key == K_s:
                self.state_manager.state = GameState.STATS
            elif key == K_o:
                self.state_manager.state = GameState.SETTINGS
            elif key == K_F1:
                self.state_manager.state = GameState.HELP
        
        elif self.state_manager.state == GameState.MODE_SELECT:
            self._handle_mode_select_keys(key)
        
        else:
            self._handle_movement_input(key, is_pressed=True)

    def _handle_keyup(self, key: int) -> None:
        """Обработать отпускание клавиши"""
        self._handle_movement_input(key, is_pressed=False)

    def update_game(self):
        # Инициализация при переходе в PLAYING
        if self.state_manager.state == GameState.PLAYING and self.all_sprites is None:
            self.init_game_objects()
        
        # Обновление только если PLAYING
        if self.state_manager.state == GameState.PLAYING:
            self._update_playing()

    def _update_playing(self):
        """Обновление игровой логики"""
        
        # Move paddles
        # Touch input
        if self.settings.get("touch_controls", False):
            touch_input1 = self.touch.get_input(1)
            self.input_state["up1"] = self.input_state["up1"] or touch_input1["up"]
            self.input_state["down1"] = self.input_state["down1"] or touch_input1["down"]
            
            if self.state_manager.game_mode == "pvp":
                touch_input2 = self.touch.get_input(2)
                self.input_state["up2"] = self.input_state["up2"] or touch_input2["up"]
                self.input_state["down2"] = self.input_state["down2"] or touch_input2["down"]
        
        # Gamepad input
        if self.gamepad.has_gamepad(1):
            gp_input = self.gamepad.get_input(1)
            self.input_state["up1"] = self.input_state["up1"] or gp_input["up"]
            self.input_state["down1"] = self.input_state["down1"] or gp_input["down"]
        
        if self.gamepad.has_gamepad(2) and self.state_manager.game_mode == "pvp":
            gp_input = self.gamepad.get_input(2)
            self.input_state["up2"] = self.input_state["up2"] or gp_input["up"]
            self.input_state["down2"] = self.input_state["down2"] or gp_input["down"]
        
        self.paddle1.move(self.input_state["up1"], self.input_state["down1"])

        if self.state_manager.game_mode == "ai":
            # AI использует предсказание траектории мяча
            predicted_y = self.paddle2.predict_ball_position(
                self.ball.rect.centerx,
                self.ball.rect.centery,
                self.ball.velocity_x,
                self.ball.velocity_y
            )
            self.paddle2.move(False, False, predicted_y)
        else:
            self.paddle2.move(self.input_state["up2"], self.input_state["down2"])
        
        # Move ball and create trail (ограничено для производительности)
        self.ball.move()
        if len(self.trails) < MAX_TRAILS and randint(1, TRAIL_SPAWN_CHANCE) == 1:
            trail = Trail(self.ball.rect.centerx, self.ball.rect.centery)
            self.trails.add(trail)
        
        self.ball.bounce_wall()
        
        # Check paddle collisions
        if pygame.sprite.collide_rect(self.ball, self.paddle1):
            if self.ball.velocity_x < 0:
                self.ball.bounce_paddle(self.paddle1)
                self.audio.play_sound("beep")
                self.create_particles(self.ball.rect.centerx, self.ball.rect.centery, self.theme.accent_color)
                self.shake.start(*SHAKE_INTENSITY_NORMAL)

        if pygame.sprite.collide_rect(self.ball, self.paddle2):
            if self.ball.velocity_x > 0:
                self.ball.bounce_paddle(self.paddle2)
                self.audio.play_sound("beep")
                self.create_particles(self.ball.rect.centerx, self.ball.rect.centery, self.theme.accent_color)
                self.shake.start(*SHAKE_INTENSITY_NORMAL)

        # Check scoring
        if self.ball.is_out_left():
            self.state_manager.add_score(2)
            self.audio.play_sound("score")
            self.goal_anim.start(2)
            self.shake.start(*SHAKE_INTENSITY_GOAL)
            if self.state_manager.state == GameState.PLAYING:
                self.ball.reset_ball()
            elif self.state_manager.state == GameState.GAME_OVER:
                self.stats.record_game(
                    self.state_manager.winner,
                    self.state_manager.player1_score,
                    self.state_manager.player2_score
                )
        elif self.ball.is_out_right():
            self.state_manager.add_score(1)
            self.audio.play_sound("score")
            self.goal_anim.start(1)
            self.shake.start(*SHAKE_INTENSITY_GOAL)
            if self.state_manager.state == GameState.PLAYING:
                self.ball.reset_ball()
            elif self.state_manager.state == GameState.GAME_OVER:
                self.stats.record_game(
                    self.state_manager.winner,
                    self.state_manager.player1_score,
                    self.state_manager.player2_score
                )
        
        # Spawn powerups
        if randint(1, POWERUP_SPAWN_CHANCE) == 1 and len(self.powerups) == 0:
            powerup = PowerUp()
            self.powerups.add(powerup)

        # Check powerup collisions with paddles
        for powerup in self.powerups:
            if not powerup.active:
                if pygame.sprite.collide_rect(powerup, self.paddle1):
                    powerup.activate(self.paddle1)
                    self.audio.play_sound("powerup")
                    self.create_particles(powerup.rect.centerx, powerup.rect.centery, self.theme.accent_color)
                    self.handle_powerup_effect(powerup, self.paddle1, self.paddle2)
                elif pygame.sprite.collide_rect(powerup, self.paddle2):
                    powerup.activate(self.paddle2)
                    self.audio.play_sound("powerup")
                    self.create_particles(powerup.rect.centerx, powerup.rect.centery, self.theme.accent_color)
                    self.handle_powerup_effect(powerup, self.paddle2, self.paddle1)
        
        # Check powerup collision with ball (for slow_ball)
        for powerup in self.powerups:
            if powerup.active and powerup.type == "slow_ball":
                if pygame.sprite.collide_rect(powerup, self.ball):
                    powerup.apply_to_ball(self.ball)
                    self.audio.play_sound("powerup")
                    self.create_particles(powerup.rect.centerx, powerup.rect.centery, self.theme.accent_color)
                    powerup.deactivate()
        
        # Update effects
        self.powerups.update()
        self.particles.update()
        self.trails.update()
        self.shake.update()
        self.goal_anim.update()

    def create_particles(self, x, y, color):
        """Создать частицы с ограничением для производительности"""
        if len(self.particles) < MAX_PARTICLES:
            for _ in range(PARTICLES_PER_HIT):
                particle = Particle(x, y, color)
                self.particles.add(particle)

    def handle_powerup_effect(self, powerup, collector, opponent):
        if powerup.type == "multi_ball":
            # Create extra ball
            new_ball = Ball()
            new_ball.rect.center = self.ball.rect.center
            new_ball.velocity_x = -self.ball.velocity_x
            new_ball.velocity_y = self.ball.velocity_y
            new_ball.image.fill(self.theme.ball_color)
            self.all_sprites.add(new_ball)
        elif powerup.type == "shrink_opponent":
            opponent.resize(50)

    def draw(self):
        self.game_surface.fill(self.theme.bg_color)
        
        if self.state_manager.state == GameState.MENU:
            self.state_manager.draw_menu()
        
        elif self.state_manager.state == GameState.MODE_SELECT:
            self.state_manager.draw_mode_select()
        
        elif self.state_manager.state == GameState.STATS:
            self.state_manager.draw_stats(self.stats)

        elif self.state_manager.state == GameState.HELP:
            self.state_manager.draw_help()

        elif self.state_manager.state == GameState.SETTINGS:
            self.settings_menu.draw()
        
        elif self.state_manager.state == GameState.PLAYING:
            self.state_manager.draw_net()
            self.state_manager.draw_score()
            self.trails.draw(self.game_surface)
            self.all_sprites.draw(self.game_surface)
            self.powerups.draw(self.game_surface)
            self.particles.draw(self.game_surface)
            self.powerup_indicator.draw(self.game_surface, self.powerups, self.paddle1, self.paddle2)
            self.goal_anim.draw(self.game_surface)

            if self.settings.get("touch_controls", False):
                self.touch.draw(self.game_surface)

            if self.state_manager.tournament_mode:
                self.tournament.draw_status(self.game_surface)

            if self.settings.get("show_fps", False):
                self.fps_counter.draw(self.game_surface, self.clock)
        
        elif self.state_manager.state == GameState.PAUSED:
            self.state_manager.draw_net()
            self.state_manager.draw_score()
            self.trails.draw(self.game_surface)
            self.all_sprites.draw(self.game_surface)
            self.powerups.draw(self.game_surface)
            self.particles.draw(self.game_surface)
            self.state_manager.draw_pause()
        
        elif self.state_manager.state == GameState.GAME_OVER:
            self.state_manager.draw_game_over()
        
        elif self.state_manager.state == GameState.TOURNAMENT_COMPLETE:
            self.tournament.draw_winner_screen(self.game_surface)

        # Apply screen shake and scale
        scaled_surface = self.adaptive_screen.get_scaled_surface(self.game_surface)
        self.screen.fill(BLACK)  # Очистка экрана
        self.shake.apply(scaled_surface, self.screen)
        pygame.display.flip()

    def run(self):
        running = True
        while running:
            running = self.handle_events()
            self.update_game()
            self.settings.update()  # Проверка отложенного сохранения настроек
            self.draw()
            self.clock.tick(FPS)

        self.shutdown()

    def shutdown(self):
        """Корректное завершение работы игры"""
        self.settings.force_save()  # Принудительное сохранение при выходе
        self.audio.stop_music()
        self._cleanup_game_objects()
        pygame.quit()

    def __del__(self):
        """Гарантировать очистку ресурсов при уничтожении объекта"""
        try:
            if pygame.get_init():
                pygame.quit()
        except Exception:
            pass

if __name__ == "__main__":
    game = PongGame()
    game.run()
