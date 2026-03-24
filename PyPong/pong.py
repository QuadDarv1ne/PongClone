"""
Enhanced Pong v4 - Main game module with modular architecture
"""
# pylint: disable=undefined-variable
from typing import Any, Dict, Optional

import pygame

from PyPong import mobile as mobile_module
from PyPong.content.tournament import Tournament
from PyPong.core.config import (
    BLACK,
    DIFFICULTY_LEVELS,
    FONT_NAME,
    FPS,
    WINDOW_HEIGHT,
    WINDOW_WIDTH,
)
from PyPong.core.config_extended import config
from PyPong.core.env_config import get_env_config, init_env_config
from PyPong.core.event_bus import GameEvent, get_event_bus
from PyPong.core.game_state import GameState, GameStateManager
from PyPong.core.logger import log_exception, logger
from PyPong.core.profiler import get_profiler
from PyPong.game.collision_manager import CollisionManager
from PyPong.game.game_loop import GameLoop
from PyPong.game.input_handler import InputHandler
from PyPong.gamepad import GamepadManager
from PyPong.rendering.renderer import Renderer
from PyPong.systems.audio import AudioManager
from PyPong.systems.settings import Settings
from PyPong.systems.stats import StatsManager
from PyPong.ui.accessibility import get_accessibility_manager
from PyPong.ui.localization import get_localization, init_localization
from PyPong.ui.themes import get_theme
from PyPong.ui.ui import FPSCounter, PowerUpIndicator, SettingsMenu

# pygame constants
K_ESCAPE = pygame.K_ESCAPE
K_RETURN = pygame.K_RETURN
K_s = pygame.K_s
K_o = pygame.K_o
K_F1 = pygame.K_F1
K_1 = pygame.K_1
K_2 = pygame.K_2
K_3 = pygame.K_3
K_4 = pygame.K_4
K_t = pygame.K_t
KEYDOWN = pygame.KEYDOWN
KEYUP = pygame.KEYUP
QUIT = pygame.QUIT


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
        if self.env.get_bool("DEBUG", False):
            self.profiler.enable()

        try:
            pygame.init()  # type: ignore[attr-defined]
        except pygame.error as e:  # type: ignore[attr-defined]
            logger.error(f"Failed to initialize pygame: {e}")
            raise

        # Инициализация локализации (из .env или русский по умолчанию)
        language = self.env.get("LANGUAGE", "ru")
        init_localization(language)

        self._init_settings()
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

    def _init_display(self) -> None:
        """Инициализация дисплея"""
        try:
            if self.is_mobile:
                self.settings.set("fullscreen", True)
                self.settings.set("touch_controls", True)
                flags = pygame.FULLSCREEN  # type: ignore[attr-defined]
            else:
                flags = pygame.RESIZABLE if self.settings.get("fullscreen", False) else 0  # type: ignore[attr-defined]

            self.screen = pygame.display.set_mode((WINDOW_WIDTH, WINDOW_HEIGHT), flags)
            self.game_surface = pygame.Surface((WINDOW_WIDTH, WINDOW_HEIGHT))
            pygame.display.set_caption("Enhanced Pong")
            self.clock = pygame.time.Clock()
            self.adaptive_screen = mobile_module.AdaptiveScreen()
            self.theme = get_theme(self.settings.get("theme", "classic"))
            self.theme.apply_accessibility()
        except pygame.error as e:  # type: ignore[attr-defined]
            logger.error(f"Failed to initialize display: {e}")
            raise

    def _init_managers(self) -> None:
        """Инициализация менеджеров"""
        try:
            self.state_manager = GameStateManager(self.screen, self.game_surface)
            self.audio = AudioManager()
            self.stats = StatsManager()
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

        # Используем оптимизированный рендерер если включён в настройках
        use_optimized = self.settings.get("use_dirty_rects", True)
        if use_optimized:
            from PyPong.rendering.optimized_renderer import OptimizedRenderer
            self.renderer = OptimizedRenderer(
                screen=self.screen,
                game_surface=self.game_surface,
                theme=self.theme,
                settings=self.settings,
                adaptive_screen=self.adaptive_screen,
            )
            logger.info("Using OptimizedRenderer with dirty rect support")
        else:
            self.renderer = Renderer(
                screen=self.screen,
                game_surface=self.game_surface,
                theme=self.theme,
                settings=self.settings,
                adaptive_screen=self.adaptive_screen,
            )
            logger.info("Using standard Renderer")

    def _init_ui(self) -> None:
        """Инициализация UI"""
        self.settings_menu = SettingsMenu(self.game_surface, self.settings)
        self.powerup_indicator = PowerUpIndicator()
        self.fps_counter = FPSCounter()

    def _init_effects(self) -> None:
        """Инициализация эффектов"""
        from PyPong.ui.effects_optimized import OptimizedParticlePool, TrailPool

        # Используем оптимизированный пул частиц
        max_particles = config.get("max_particles", 50)
        self.particle_pool = OptimizedParticlePool(max_size=max_particles)

        max_trails = config.get("max_trails", 20)
        self.trails = TrailPool(max_size=max_trails)

        self.shake = ScreenShake()
        self.goal_anim = GoalAnimation()

        # Передать эффекты в game_loop и renderer
        self.game_loop.set_effects(self.particle_pool, self.trails, self.shake, self.goal_anim)
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
        except Exception as e:
            logger.error(f"Failed to apply settings: {e}")

    @log_exception
    def _detect_mobile(self) -> bool:
        """Detect if running on mobile platform"""
        try:
            import os
            import platform

            system = platform.system().lower()

            # Android detection
            if system == "linux":
                try:
                    with open("/proc/version", "r") as f:
                        if "android" in f.read().lower():
                            return True
                except (IOError, OSError):
                    pass
                if os.environ.get("ANDROID_ROOT") or os.environ.get("ANDROID_DATA"):
                    return True
            # iOS detection
            elif system == "darwin":
                machine = platform.machine().lower()
                if "iphone" in machine or "ipad" in machine:
                    return True

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
        self._apply_accessibility_settings()

    @log_exception
    def _apply_accessibility_settings(self) -> None:
        """Применить accessibility настройки"""
        if hasattr(self, "accessibility"):
            self.accessibility.high_contrast = self.settings.get("high_contrast", False)
            self.accessibility.large_ui = self.settings.get("large_ui", False)

    @log_exception
    def _apply_theme(self) -> None:
        """Применить тему"""
        if hasattr(self, "game_loop"):
            self.game_loop.theme = self.theme

    @log_exception
    def handle_events(self) -> bool:
        """Обработать события pygame"""
        for event in pygame.event.get():
            if event.type == QUIT:  # type: ignore[attr-defined]
                return False

            # Handle window resize
            if event.type == pygame.VIDEORESIZE:  # type: ignore[attr-defined]
                if not self.is_mobile:
                    self.adaptive_screen.update_resolution(event.w, event.h)
                    self.screen = pygame.display.set_mode((event.w, event.h), pygame.RESIZABLE)  # type: ignore[attr-defined]
                    self.renderer.screen = self.screen
                    # Update touch controls for new screen size
                    if self.settings.get("touch_controls", False):
                        self.touch.update_screen_size(event.w, event.h)

            # Handle touch/mouse events
            if event.type in (pygame.MOUSEBUTTONDOWN, pygame.MOUSEBUTTONUP):  # type: ignore[attr-defined]
                if self.settings.get("touch_controls", False) or self.is_mobile:
                    self.touch.handle_touch(event)

            # Handle native touch events (FINGERDOWN, FINGERUP)
            if hasattr(pygame, "FINGERDOWN") and event.type == pygame.FINGERDOWN:  # type: ignore[attr-defined]
                if self.settings.get("touch_controls", False) or self.is_mobile:
                    self.touch.handle_touch(event)

            if hasattr(pygame, "FINGERUP") and event.type == pygame.FINGERUP:  # type: ignore[attr-defined]
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
            if event.type == KEYDOWN:  # type: ignore[attr-defined]
                self._handle_keydown(event.key)
            elif event.type == KEYUP:  # type: ignore[attr-defined]
                self._handle_keyup(event.key)

        return True

    @log_exception
    def _handle_keydown(self, key: int) -> None:
        """Обработать нажатие клавиши"""
        if key == K_ESCAPE:  # type: ignore[attr-defined]
            self._handle_escape()
        elif key == K_RETURN:  # type: ignore[attr-defined]
            self._handle_enter()
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
        }

        new_state = transitions.get(state)
        if new_state:
            self.state_manager.state = new_state
            if new_state == GameState.MENU:
                self.game_loop.cleanup_game_objects()
        elif state == GameState.MENU:
            logger.info("ESC pressed in MENU, exiting game")
            raise SystemExit()

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
                # Публикуем событие начала игры
                self.event_bus.publish(GameEvent.GAME_START, {"mode": self.state_manager.game_mode})
            elif new_state == GameState.MENU:
                if state == GameState.GAME_OVER:
                    self.game_loop.cleanup_game_objects()
                    self.state_manager.reset_scores()
                    # Публикуем событие окончания игры
                    self.event_bus.publish(GameEvent.GAME_OVER)
                elif state == GameState.TOURNAMENT_COMPLETE:
                    self.tournament.reset()

    @log_exception
    def _handle_menu_keys(self, key: int) -> None:
        """Обработать клавиши меню"""
        if key == K_s:  # type: ignore[attr-defined]
            self.state_manager.state = GameState.STATS
        elif key == K_o:  # type: ignore[attr-defined]
            self.state_manager.state = GameState.SETTINGS
        elif key == K_F1:  # type: ignore[attr-defined]
            self.state_manager.state = GameState.HELP

    @log_exception
    def _handle_mode_select_keys(self, key: int) -> None:
        """Обработать клавиши выбора режима"""
        if self.state_manager.state != GameState.MODE_SELECT:
            return

        action_data = {}
        if key == K_1:  # type: ignore[attr-defined]
            action_data["game_mode"] = "ai"
        elif key == K_2:  # type: ignore[attr-defined]
            action_data["game_mode"] = "pvp"
        elif key == K_3:  # type: ignore[attr-defined]
            action_data["difficulty"] = "Easy"
        elif key == K_4:  # type: ignore[attr-defined]
            action_data["difficulty"] = "Medium"
        elif key == K_t:  # type: ignore[attr-defined]
            self.state_manager.tournament_mode = not self.state_manager.tournament_mode
            if self.state_manager.tournament_mode:
                self.tournament.reset()
                action_data["difficulty"] = "Hard"

        # Применить изменения
        if "game_mode" in action_data:
            self.state_manager.game_mode = action_data["game_mode"]
        if "difficulty" in action_data:
            self.state_manager.set_difficulty(action_data["difficulty"])

    @log_exception
    def update_game(self) -> None:
        """Обновить игру"""
        if self.state_manager.state == GameState.PLAYING:
            with self.profiler.profile_section("game_update"):
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

    @log_exception
    def draw(self) -> None:
        """Отрисовать кадр"""
        # Проверяем тип рендерера и используем соответствующий метод
        from PyPong.rendering.optimized_renderer import OptimizedRenderer

        if isinstance(self.renderer, OptimizedRenderer):
            # Оптимизированный рендеринг - рисуем в зависимости от состояния
            state = self.state_manager.state

            if state == GameState.PLAYING or state == GameState.PAUSED:
                # Игра - используем оптимизированный рендеринг
                self.renderer.render_game_optimized(self.state_manager, self.shake)
                # Отрисовка визуальных индикаторов
                if hasattr(self.game_loop, 'visual_indicators') and self.game_loop.visual_indicators:
                    self.game_loop.visual_indicators.draw(self.renderer.game_surface)
            elif state == GameState.MENU:
                self.renderer.clear()
                self.state_manager.draw_menu()
            elif state == GameState.MODE_SELECT:
                self.renderer.clear()
                self.state_manager.draw_mode_select()
            elif state == GameState.GAME_OVER:
                self.renderer.clear()
                self.state_manager.draw_game_over()
            elif state == GameState.STATS:
                self.renderer.clear()
                self.state_manager.draw_stats(self.stats)
            elif state == GameState.HELP:
                self.renderer.clear()
                self.state_manager.draw_help()
            elif state == GameState.SETTINGS:
                self.renderer.clear()
                self.settings_menu.draw()
            elif state == GameState.TOURNAMENT_COMPLETE:
                self.renderer.clear()
                self.tournament.draw_complete()

            # Blit game_surface to screen и обновляем дисплей
            self.screen.blit(self.renderer.game_surface, (0, 0))
            self.renderer.dirty_renderer.update_display_optimized()
        else:
            # Стандартный рендеринг
            self.renderer.render(
                state=self.state_manager.state,
                state_manager=self.state_manager,
                shake=self.shake,
                settings_menu=self.settings_menu,
                stats_manager=self.stats,
                tournament=self.tournament,
                visual_indicators=self.game_loop.visual_indicators if hasattr(self.game_loop, 'visual_indicators') else None,
            )

    @log_exception
    def run(self) -> None:
        """Запустить игровой цикл"""
        running = True
        frame_count = 0
        logger.info(f"Starting game loop, state: {self.state_manager.state}")
        try:
            while running:
                running = self.handle_events()
                self.update_game()
                self.settings.update()
                self.draw()
                self.clock.tick(FPS)
                frame_count += 1

                if frame_count % 100 == 0:
                    fps = self.clock.get_fps()
                    logger.debug(f"Frame: {frame_count}, FPS: {fps:.1f}, State: {self.state_manager.state}")

                    # Вывод статистики OptimizedRenderer если используется
                    if hasattr(self.renderer, 'get_performance_stats'):
                        stats = self.renderer.get_performance_stats()
                        if stats:
                            logger.debug(f"Render avg: {stats.get('avg_render_time_ms', 0):.2f}ms, FPS: {stats.get('fps_estimate', 0):.1f}")
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
                if pygame.get_init():  # type: ignore[attr-defined]
                    pygame.quit()  # type: ignore[attr-defined]
            except Exception:
                pass

    def __del__(self) -> None:
        """Гарантировать очистку ресурсов"""
        try:
            if pygame.get_init():  # type: ignore[attr-defined]
                pygame.quit()  # type: ignore[attr-defined]
        except Exception:
            pass


# Import effects at the end to avoid circular imports
from PyPong.ui.effects import GoalAnimation, ScreenShake

if __name__ == "__main__":
    game = PongGame()
    game.run()
