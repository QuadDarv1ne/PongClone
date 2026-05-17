"""Enhanced Pong v4 - Main game module with modular architecture"""
import pygame
from pygame.locals import *
from typing import Optional

from PyPong.core.env_config import init_env_config, get_env_config
from PyPong.core.config import (
    WINDOW_WIDTH,
    WINDOW_HEIGHT,
    FPS,
    BLACK,
    DIFFICULTY_LEVELS,
    FONT_NAME,
)
from PyPong.core.config_extended import config
from PyPong.core.event_bus import get_event_bus, GameEvent
from PyPong.core.constants import EventType
from PyPong.core.profiler import get_profiler
from PyPong.core.game_state import GameState, GameStateManager
from PyPong.game.input_handler import InputHandler
from PyPong.game.collision_manager import CollisionManager
from PyPong.game.game_loop import GameLoop
from PyPong.rendering.renderer import Renderer
from PyPong.systems.audio import AudioManager
from PyPong.systems.stats import StatsManager
from PyPong.systems.settings import Settings
from PyPong.systems.achievements import AchievementManager
from PyPong.systems.leaderboard import Leaderboard
from PyPong.ui.ui import PowerUpIndicator, FPSCounter, SettingsMenu
from PyPong.content.tournament import Tournament
from PyPong.ui.themes import get_theme
from PyPong.gamepad import GamepadManager
import PyPong.mobile as mobile_module
from PyPong.core.logger import logger, log_exception
from PyPong.ui.localization import init_localization, get_localization
from PyPong.ui.accessibility import get_accessibility_manager


class PongGame:
    """Main game class with modular architecture"""

    def __init__(self) -> None:
        # Инициализация конфигурации из .env
        init_env_config()
        self.env = get_env_config()

        # Инициализация систем
        self.event_bus = get_event_bus()
        self.profiler = get_profiler()
        self.accessibility = get_accessibility_manager()

        # Включить профилирование в debug режиме
        if self.env.get_bool('DEBUG', False):
            self.profiler.enable()

        try:
            pygame.init()
        except pygame.error as e:
            logger.error(f"Failed to initialize pygame: {e}")
            raise

        # Инициализация настроек (до локализации, чтобы считать сохранённый язык)
        self._init_settings()

        # Инициализация локализации: приоритет — settings.json, затем .env, затем английский
        language = self.env.get('LANGUAGE', 'en')
        saved_lang = self.settings.get("language")
        if saved_lang:
            language = saved_lang
        init_localization(language)

        self._auto_detect_and_apply()
        self._init_display()
        self._init_managers()
        self._init_modules()
        self._init_ui()
        self._init_effects()
        self._apply_startup_settings()

    def _init_settings(self) -> None:
        """Инициализация настроек"""
        self.settings = Settings()
        self.is_mobile = self._detect_mobile()

    @log_exception
    def _auto_detect_and_apply(self) -> None:
        """Автоматическое определение настроек оборудования при каждом запуске.
        Обновляет настройки только если обнаружены изменения в оборудовании."""
        from PyPong.core.auto_detect import get_recommended_settings

        recommended = get_recommended_settings()

        # Check if anything changed
        current_profile = self.settings.get("performance_profile")
        new_profile = recommended.get("profile")
        current_width = self.settings.get("window_width")
        current_height = self.settings.get("window_height")

        changed = False

        if recommended.get("width") and recommended.get("height"):
            if current_width != recommended["width"] or current_height != recommended["height"]:
                logger.info(
                    f"Auto-detect: resolution changed from "
                    f"{current_width}x{current_height} to "
                    f"{recommended['width']}x{recommended['height']}"
                )
                self.settings.set("window_width", recommended["width"])
                self.settings.set("window_height", recommended["height"])
                changed = True

        if new_profile and current_profile != new_profile:
            logger.info(
                f"Auto-detect: performance profile changed from "
                f"{current_profile} to {new_profile}"
            )
            self.settings.set("performance_profile", new_profile)
            self._apply_performance_profile(new_profile)
            changed = True

        if not changed:
            logger.info("Auto-detect: no hardware changes detected")

        self.settings.set("auto_detected", True)

    @log_exception
    def _apply_performance_profile(self, profile_name: str) -> None:
        """Применить профиль производительности к настройкам"""
        from PyPong.core.config import PERFORMANCE_PROFILES

        profile = PERFORMANCE_PROFILES.get(profile_name, PERFORMANCE_PROFILES["medium"])

        self.settings.set("max_particles", profile["max_particles"])
        self.settings.set("max_trails", profile["max_trails"])
        self.settings.set("target_fps", profile["target_fps"])
        self.settings.set("enable_shake", profile["enable_shake"])
        self.settings.set("enable_effects", profile["enable_effects"])

    def _init_display(self) -> None:
        """Инициализация дисплея"""
        try:
            width = self.settings.get("window_width", WINDOW_WIDTH) or WINDOW_WIDTH
            height = self.settings.get("window_height", WINDOW_HEIGHT) or WINDOW_HEIGHT

            if self.is_mobile:
                self.settings.set("fullscreen", True)
                self.settings.set("touch_controls", True)
                flags = pygame.FULLSCREEN
            else:
                flags = pygame.FULLSCREEN if self.settings.get("fullscreen", False) else pygame.RESIZABLE

            self.screen = pygame.display.set_mode((width, height), flags)
            self.game_surface = pygame.Surface((WINDOW_WIDTH, WINDOW_HEIGHT))
            pygame.display.set_caption("Enhanced Pong")
            self.clock = pygame.time.Clock()
            self.adaptive_screen = mobile_module.AdaptiveScreen(WINDOW_WIDTH, WINDOW_HEIGHT)
            self.theme = get_theme(self.settings.get("theme", "classic"))
        except pygame.error as e:
            logger.error(f"Failed to initialize display: {e}")
            raise

    def _init_managers(self) -> None:
        """Инициализация менеджеров"""
        try:
            self.state_manager = GameStateManager(self.screen, self.game_surface)
            self.audio = AudioManager()
            self.stats = StatsManager()
            self.achievements = AchievementManager()
            self.leaderboard = Leaderboard()
            self.tournament = Tournament()
            self.gamepad = GamepadManager()
            self.touch = mobile_module.TouchControls(WINDOW_WIDTH, WINDOW_HEIGHT)
        except Exception as e:
            logger.error(f"Failed to initialize managers: {e}")
            raise

    def _init_modules(self) -> None:
        """Инициализация новых модулей"""
        self.input_handler = InputHandler()
        self.collision_manager = CollisionManager()

        self.game_loop = GameLoop(
            state_manager=self.state_manager,
            input_handler=self.input_handler,
            collision_manager=self.collision_manager,
            audio=self.audio,
            settings=self.settings,
            theme=self.theme,
            gamepad=self.gamepad,
            touch=self.touch,
        )

        self.renderer = Renderer(
            screen=self.screen,
            game_surface=self.game_surface,
            theme=self.theme,
            settings=self.settings,
            adaptive_screen=self.adaptive_screen,
        )

    def _init_ui(self) -> None:
        """Инициализация UI"""
        self.settings_menu = SettingsMenu(self.game_surface, self.settings)
        self.powerup_indicator = PowerUpIndicator()
        self.fps_counter = FPSCounter()

    def _init_effects(self) -> None:
        """Инициализация эффектов"""
        from PyPong.ui.effects_optimized import OptimizedParticlePool, TrailPool
        from PyPong.ui.effects import ScreenShake, GoalAnimation

        max_particles = self.settings.get("max_particles", config.get('max_particles', 50))
        max_trails = self.settings.get("max_trails", config.get('max_trails', 20))
        self.particle_pool = OptimizedParticlePool(max_size=max_particles)
        self.trails = TrailPool(max_size=max_trails)
        self.shake = ScreenShake()
        self.goal_anim = GoalAnimation()

        # Передать эффекты в game_loop и renderer
        self.game_loop.set_effects(
            self.particle_pool,
            self.trails,
            self.shake,
            self.goal_anim,
        )

        self.renderer.set_sprite_groups(
            None,  # all_sprites будет установлен в game_loop
            None,  # powerups будет установлен в game_loop
            self.particle_pool,
            self.trails,
        )

    def _apply_startup_settings(self) -> None:
        """Применить настройки при запуске"""
        try:
            self._apply_settings()
            self._apply_theme()
            self._apply_accessibility_settings()
        except Exception as e:
            logger.error(f"Failed to apply settings: {e}")

    @log_exception
    def _detect_mobile(self) -> bool:
        """Detect if running on mobile platform (Android/iOS)"""
        try:
            import platform
            import os

            system = platform.system().lower()

            # Android detection via /proc/version
            if system == 'linux':
                try:
                    with open('/proc/version', 'r') as f:
                        if 'android' in f.read().lower():
                            return True
                except (IOError, OSError):
                    pass

                # Check for Android environment variables
                if os.environ.get('ANDROID_ROOT') or os.environ.get('ANDROID_DATA'):
                    return True

            # iOS detection
            if system == 'darwin':
                machine = platform.machine().lower()
                if 'iphone' in machine or 'ipad' in machine:
                    return True

            # Kivy/Buildozer environment (used for Android builds)
            if os.environ.get('ANDROID_APP_PATH') or os.environ.get('PYTHONOPTIMIZE'):
                if 'android' in os.environ.get('EXTRAPATH', '').lower():
                    return True

            # Not a mobile platform
            return False
        except Exception as e:
            logger.warning(f"Platform detection failed: {e}")
            return False

    @log_exception
    def _apply_settings(self) -> None:
        """Применить настройки аудио и дисплея"""
        pygame.mixer.music.set_volume(self.settings.get("music_volume", 0.5))
        for sound in self.audio.sounds.values():
            sound.set_volume(self.settings.get("sfx_volume", 0.7))

    @log_exception
    def _apply_theme(self) -> None:
        """Применить тему"""
        if hasattr(self, 'game_loop'):
            self.game_loop.theme = self.theme

    @log_exception
    def _apply_accessibility_settings(self) -> None:
        """Применить настройки доступности"""
        from PyPong.ui.accessibility import get_accessibility_manager, ColorBlindMode

        mgr = get_accessibility_manager()
        cb_mode = self.settings.get("colorblind_mode", "normal")
        mode_map = {
            "normal": ColorBlindMode.NORMAL,
            "protanopia": ColorBlindMode.PROTANOPIA,
            "deuteranopia": ColorBlindMode.DEUTERANOPIA,
            "tritanopia": ColorBlindMode.TRITANOPIA,
            "monochromacy": ColorBlindMode.MONOCHROMACY,
        }
        mgr.set_color_blind_mode(mode_map.get(cb_mode, ColorBlindMode.NORMAL))

        if self.settings.get("high_contrast", False):
            mgr.enable_high_contrast()
        else:
            mgr.disable_high_contrast()

        if self.settings.get("reduce_motion", False):
            mgr.enable_reduce_motion()
        else:
            mgr.disable_reduce_motion()

        if self.settings.get("audio_cues", True):
            mgr.enable_audio_cues()
        else:
            mgr.disable_audio_cues()

        if self.settings.get("large_ui", False):
            mgr.enable_large_ui()
        else:
            mgr.disable_large_ui()

        logger.info("Accessibility settings applied")

    @log_exception
    def handle_events(self) -> bool:
        """Обработать события pygame"""
        for event in pygame.event.get():
            if event.type == QUIT:
                return False

            # Handle window resize
            if event.type == pygame.VIDEORESIZE:
                if not self.is_mobile:
                    self.adaptive_screen.update_resolution(event.w, event.h)
                    self.screen = pygame.display.set_mode((event.w, event.h), pygame.RESIZABLE)
                    self.renderer.screen = self.screen
                    self.state_manager.on_resize(event.w, event.h)

                    # Update touch controls for new screen size
                    if self.settings.get("touch_controls", False):
                        self.touch.update_screen_size(event.w, event.h)

            # Handle touch/mouse events
            if event.type in (pygame.MOUSEBUTTONDOWN, pygame.MOUSEBUTTONUP):
                if self.settings.get("touch_controls", False) or self.is_mobile:
                    self.touch.handle_touch(event)

            # Handle native touch events (FINGERDOWN, FINGERUP)
            if hasattr(pygame, 'FINGERDOWN') and event.type == pygame.FINGERDOWN:
                if self.settings.get("touch_controls", False) or self.is_mobile:
                    self.touch.handle_touch(event)

            if hasattr(pygame, 'FINGERUP') and event.type == pygame.FINGERUP:
                if self.settings.get("touch_controls", False) or self.is_mobile:
                    self.touch.handle_touch(event)

            # Settings menu
            if self.state_manager.state == GameState.SETTINGS:
                result = self.settings_menu.handle_input(event)
                if result == "back":
                    self.state_manager.state = GameState.MENU
                    self._apply_settings()
                continue

            # Keyboard events
            if event.type == KEYDOWN:
                self._handle_keydown(event.key)
            elif event.type == KEYUP:
                self._handle_keyup(event.key)

        return True

    @log_exception
    def _handle_keydown(self, key: int) -> None:
        """Обработать нажатие клавиши"""
        if key == K_ESCAPE:
            self._handle_escape()
        elif key == K_RETURN:
            self._handle_enter()
        elif self.state_manager.state == GameState.ONBOARDING:
            self._handle_onboarding_keys(key)
        elif self.state_manager.state == GameState.MENU:
            self._handle_menu_keys(key)
        elif self.state_manager.state == GameState.MODE_SELECT:
            self._handle_mode_select_keys(key)
        else:
            self.input_handler.handle_keydown(key, self.state_manager.state)

    @log_exception
    def _handle_keyup(self, key: int) -> None:
        """Обработать отпускание клавиши"""
        self.input_handler.handle_keyup(key, self.state_manager.state)

    @log_exception
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
            GameState.GAME_OVER: GameState.MENU,
            GameState.CAMPAIGN_SELECT: GameState.MENU,
            GameState.CAMPAIGN_PLAYING: GameState.MENU,
            GameState.CAMPAIGN_COMPLETE: GameState.MENU,
            GameState.CHALLENGES: GameState.MENU,
            GameState.MINIGAME_SELECT: GameState.MENU,
            GameState.MINIGAME_PLAYING: GameState.MENU,
            GameState.MINIGAME_COMPLETE: GameState.MENU,
            GameState.GOAL_CELEBRATION: GameState.GAME_OVER,
            GameState.ONBOARDING: GameState.MENU,
        }

        new_state = transitions.get(state)
        if new_state:
            self.state_manager.state = new_state
            if new_state == GameState.MENU:
                if state == GameState.ONBOARDING:
                    self.settings.set("has_seen_onboarding", True)
                self.game_loop.cleanup_game_objects()
        else:
            logger.warning(f"No ESC transition defined for state: {state}")

    @log_exception
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
                # Очистить старые объекты перед новой игрой
                if state == GameState.MODE_SELECT:
                    self.game_loop.cleanup_game_objects()
                self.audio.play_music()
                self._game_start_time = pygame.time.get_ticks()

                # Публикуем событие начала игры
                self.event_bus.publish(GameEvent.GAME_START, {'mode': self.state_manager.game_mode})

            elif new_state == GameState.MENU:
                if state == GameState.GAME_OVER:
                    # Record game statistics before resetting
                    self.stats.record_game(
                        winner=self.state_manager.winner,
                        player1_score=self.state_manager.player1_score,
                        player2_score=self.state_manager.player2_score,
                    )
                    # Check achievements
                    duration = (pygame.time.get_ticks() - self._game_start_time) / 1000
                    winner = self.state_manager.winner
                    p1_score = self.state_manager.player1_score
                    p2_score = self.state_manager.player2_score
                    winner_score = p1_score if winner == 1 else p2_score
                    perfect = ((p1_score == 0 or p2_score == 0) and winner is not None) if winner else False
                    self.achievements.check_event(
                        EventType.GAME_END,
                        won=winner is not None,
                        perfect=perfect,
                        duration=duration,
                    )
                    # Add to leaderboard
                    if winner:
                        score = winner_score * 100
                        mode = self.state_manager.game_mode
                        diff = self.state_manager.difficulty
                        self.leaderboard.add_score(
                            name=f"Player {winner}",
                            score=score,
                            mode=mode,
                            difficulty=diff,
                            duration=int(duration),
                        )
                    self.game_loop.cleanup_game_objects()
                    self.state_manager.reset_scores()

                # Публикуем событие окончания игры
                self.event_bus.publish(GameEvent.GAME_OVER)

            elif state == GameState.TOURNAMENT_COMPLETE:
                self.tournament.reset()

    @log_exception
    def _handle_menu_keys(self, key: int) -> None:
        """Обработать клавиши меню"""
        if key == K_s:
            self.state_manager.state = GameState.STATS
        elif key == K_o:
            self.state_manager.state = GameState.SETTINGS
        elif key == K_F1:
            self.state_manager.state = GameState.HELP

    @log_exception
    def _handle_mode_select_keys(self, key: int) -> None:
        """Обработать клавиши выбора режима"""
        if self.state_manager.state != GameState.MODE_SELECT:
            return

        action_data = {}

        if key == K_1:
            action_data['game_mode'] = 'ai'
        elif key == K_2:
            action_data['game_mode'] = 'pvp'
        elif key == K_3:
            action_data['difficulty'] = 'Easy'
        elif key == K_4:
            action_data['difficulty'] = 'Medium'
        elif key == K_t:
            self.state_manager.tournament_mode = not self.state_manager.tournament_mode
            if self.state_manager.tournament_mode:
                self.tournament.reset()

        # Применить изменения
        if 'game_mode' in action_data:
            self.state_manager.game_mode = action_data['game_mode']
        if 'difficulty' in action_data:
            self.state_manager.set_difficulty(action_data['difficulty'])

    @log_exception
    def _handle_onboarding_keys(self, key: int) -> None:
        """Обработать клавиши на экране обучения"""
        sm = self.state_manager
        if key == K_RETURN:
            if sm.onboarding_slide < sm.onboarding_total_slides - 1:
                sm.onboarding_slide += 1
            else:
                self.settings.set("has_seen_onboarding", True)
                sm.state = GameState.MODE_SELECT

    @log_exception
    def update_game(self) -> None:
        """Обновить игру"""
        if self.state_manager.state == GameState.PLAYING:
            with self.profiler.profile_section('game_update'):
                if self.game_loop.all_sprites is None:
                    try:
                        logger.info("Initializing game objects...")
                        self.game_loop.init_game_objects()

                        # Проверка успешной инициализации
                        if self.game_loop.all_sprites is None:
                            logger.error("Failed to initialize game objects: all_sprites is still None")
                            self.state_manager.state = GameState.MENU
                            return

                        # Обновить sprite groups в renderer
                        self.renderer.set_sprite_groups(
                            self.game_loop.all_sprites,
                            self.game_loop.powerups,
                            self.particle_pool,
                            self.trails,
                        )
                        logger.info("Game objects initialized successfully")

                    except Exception as e:
                        logger.error(f"Error initializing game objects: {e}", exc_info=True)
                        self.state_manager.state = GameState.MENU
                        return
                else:
                    logger.debug("Game already initialized")

                try:
                    self.game_loop.update()
                except Exception as e:
                    logger.error(f"Error updating game loop: {e}", exc_info=True)
                    self.state_manager.state = GameState.MENU

                # Record tournament game win when a game ends
                if (self.state_manager.tournament_mode
                        and self.state_manager.state == GameState.GAME_OVER
                        and self.state_manager.winner is not None
                        and not self.tournament.is_complete()):
                    self.tournament.record_game_win(self.state_manager.winner)
                    if self.tournament.is_complete():
                        self.state_manager.state = GameState.TOURNAMENT_COMPLETE

                # Auto-transition from goal celebration to game over
                if self.state_manager.state == GameState.GOAL_CELEBRATION:
                    if self.goal_anim is None or not self.goal_anim.active:
                        self.state_manager.state = GameState.GAME_OVER

    @log_exception
    def draw(self) -> None:
        """Отрисовать кадр"""
        self.renderer.render(
            state=self.state_manager.state,
            state_manager=self.state_manager,
            shake=self.shake,
            clock=self.clock,
            settings_menu=self.settings_menu,
            stats_manager=self.stats,
            tournament=self.tournament,
            touch_controls=self.touch,
            powerup_indicator=self.powerup_indicator,
            goal_anim=self.goal_anim,
        )

    @log_exception
    def run(self) -> None:
        """Запустить игровой цикл"""
        running = True
        frame_count = 0

        # Show onboarding on first launch
        if not self.settings.get("has_seen_onboarding", False):
            self.state_manager.state = GameState.ONBOARDING
            self.state_manager.onboarding_slide = 0

        try:
            while running:
                running = self.handle_events()
                self.update_game()
                self.settings.update()
                self.draw()
                self.clock.tick(self.settings.get("target_fps", FPS))
                frame_count += 1

                # Логирование каждые 100 кадров
                if frame_count % 100 == 0:
                    fps = self.clock.get_fps()
                    logger.debug(f"Frame: {frame_count}, FPS: {fps:.1f}, State: {self.state_manager.state}")

        except Exception as e:
            logger.error(f"Game loop error: {e}", exc_info=True)
        finally:
            self.shutdown()

    @log_exception
    def shutdown(self) -> None:
        """Корректное завершение работы"""
        try:
            # Вывести статистику профилирования
            if self.profiler._enabled:
                self.profiler.print_timing_report()

            self.settings.force_save()
            self.audio.stop_music()
            self.game_loop.cleanup_game_objects()
        except Exception as e:
            logger.error(f"Error during shutdown: {e}")
        finally:
            try:
                if pygame.get_init():
                    pygame.quit()
            except Exception:
                pass

    def __del__(self) -> None:
        """Гарантировать очистку ресурсов"""
        try:
            if pygame.get_init():
                pygame.quit()
        except Exception:
            pass



if __name__ == "__main__":
    game = PongGame()
    game.run()
