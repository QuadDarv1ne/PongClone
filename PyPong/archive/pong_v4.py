"""
Enhanced Pong v4 - Main game module with modular architecture
"""
import pygame
from pygame.locals import *
from typing import Optional, Dict, Any

from PyPong.core.config import (
    WINDOW_WIDTH, WINDOW_HEIGHT, FPS, BLACK,
    DIFFICULTY_LEVELS, FONT_NAME,
)
from PyPong.core.game_state import GameState, GameStateManager
from PyPong.game.input_handler import InputHandler
from PyPong.game.collision_manager import CollisionManager
from PyPong.game.game_loop import GameLoop
from PyPong.rendering.renderer import Renderer
from PyPong.systems.audio import AudioManager
from PyPong.systems.stats import StatsManager
from PyPong.systems.settings import Settings
from PyPong.ui.ui import PowerUpIndicator, FPSCounter, SettingsMenu
from PyPong.content.tournament import Tournament
from PyPong.ui.themes import get_theme
from PyPong.gamepad import GamepadManager
from PyPong.mobile import TouchControls, AdaptiveScreen
from PyPong.core.logger import logger, log_exception
from PyPong.ui.localization import init_localization, get_localization


class PongGame:
    """Main game class with modular architecture"""

    def __init__(self) -> None:
        try:
            pygame.init()
        except pygame.error as e:
            logger.error(f"Failed to initialize pygame: {e}")
            raise

        # Инициализация локализации (русский по умолчанию)
        init_localization('ru')
        
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
                flags = pygame.FULLSCREEN
            else:
                flags = pygame.FULLSCREEN if self.settings.get("fullscreen", False) else pygame.RESIZABLE
            
            self.screen = pygame.display.set_mode(
                (WINDOW_WIDTH, WINDOW_HEIGHT), 
                flags
            )
            self.game_surface = pygame.Surface((WINDOW_WIDTH, WINDOW_HEIGHT))
            pygame.display.set_caption("Enhanced Pong")
            self.clock = pygame.time.Clock()
            self.adaptive_screen = AdaptiveScreen()
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
            self.tournament = Tournament()
            self.gamepad = GamepadManager()
            self.touch = TouchControls(WINDOW_WIDTH, WINDOW_HEIGHT)
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
        from PyPong.ui.effects import ParticlePool
        
        # Используем ParticlePool для оптимизации
        self.particle_pool = ParticlePool()
        self.trails = pygame.sprite.Group()
        self.shake = ScreenShake()
        self.goal_anim = GoalAnimation()

        # Передать эффекты в game_loop и renderer
        self.game_loop.set_effects(
            self.particle_pool,
            self.trails,
            self.shake,
            self.goal_anim
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
        except Exception as e:
            logger.error(f"Failed to apply settings: {e}")
    
    @log_exception
    def _detect_mobile(self) -> bool:
        """Detect if running on mobile platform"""
        try:
            import platform
            system = platform.system().lower()
            if system == 'linux':
                try:
                    with open('/proc/version', 'r') as f:
                        if 'android' in f.read().lower():
                            return True
                except (IOError, OSError):
                    pass
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
    def handle_events(self) -> bool:
        """Обработать события pygame"""
        for event in pygame.event.get():
            if event.type == QUIT:
                return False
            
            if event.type == pygame.VIDEORESIZE:
                if not self.is_mobile:
                    self.adaptive_screen.update_resolution(event.w, event.h)
                    self.screen = pygame.display.set_mode(
                        (event.w, event.h), 
                        pygame.RESIZABLE
                    )
                    self.renderer.screen = self.screen
            
            if event.type in (pygame.MOUSEBUTTONDOWN, pygame.MOUSEBUTTONUP):
                if self.settings.get("touch_controls", False):
                    self.touch.handle_touch(event)
            
            if self.state_manager.state == GameState.SETTINGS:
                result = self.settings_menu.handle_input(event)
                if result == "back":
                    self.state_manager.state = GameState.MENU
                    self._apply_settings()
                continue
            
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
        else:
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
            elif new_state == GameState.MENU:
                if state == GameState.GAME_OVER:
                    self.game_loop.cleanup_game_objects()
                    self.state_manager.reset_scores()
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
                action_data['difficulty'] = 'Hard'
        
        # Применить изменения
        if 'game_mode' in action_data:
            self.state_manager.game_mode = action_data['game_mode']
        if 'difficulty' in action_data:
            self.state_manager.set_difficulty(action_data['difficulty'])
    
    @log_exception
    def update_game(self) -> None:
        """Обновить игру"""
        if self.state_manager.state == GameState.PLAYING:
            if self.game_loop.all_sprites is None:
                logger.info("Initializing game objects...")
                self.game_loop.init_game_objects()
                # Обновить sprite groups в renderer
                self.renderer.set_sprite_groups(
                    self.game_loop.all_sprites,
                    self.game_loop.powerups,
                    self.particle_pool,
                    self.trails,
                )
                logger.info(f"Game objects initialized: all_sprites={self.game_loop.all_sprites is not None}")
            else:
                logger.debug(f"Game already initialized: all_sprites={self.game_loop.all_sprites is not None}")

            self.game_loop.update()
    
    @log_exception
    def draw(self) -> None:
        """Отрисовать кадр"""
        self.renderer.render(
            state=self.state_manager.state,
            state_manager=self.state_manager,
            shake=self.shake,
            settings_menu=self.settings_menu,
            stats_manager=self.stats,
            tournament=self.tournament,
        )
    
    @log_exception
    def run(self) -> None:
        """Запустить игровой цикл"""
        running = True
        frame_count = 0
        try:
            while running:
                running = self.handle_events()
                self.update_game()
                self.settings.update()
                self.draw()
                self.clock.tick(FPS)
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


# Import effects at the end to avoid circular imports
from PyPong.ui.effects import ScreenShake, GoalAnimation


if __name__ == "__main__":
    game = PongGame()
    game.run()
