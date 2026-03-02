"""
Main game renderer
"""
import pygame
from typing import Optional, Any, Union

from PyPong.core.game_state import GameState
from PyPong.core.config import BLACK
from PyPong.ui.effects import ParticlePool


class Renderer:
    """
    Управляет отрисовкой игры.
    """

    def __init__(
        self,
        screen: pygame.Surface,
        game_surface: pygame.Surface,
        theme: Any,
        settings: Any,
        adaptive_screen: Any,
    ):
        self.screen = screen
        self.game_surface = game_surface
        self.theme = theme
        self.settings = settings
        self.adaptive_screen = adaptive_screen

        # Sprite groups
        self.all_sprites: Optional[pygame.sprite.Group] = None
        self.powerups: Optional[pygame.sprite.Group] = None
        self.particles: Optional[Union[pygame.sprite.Group, ParticlePool]] = None
        self.trails: Optional[pygame.sprite.Group] = None
    
    def set_sprite_groups(
        self,
        all_sprites: pygame.sprite.Group,
        powerups: pygame.sprite.Group,
        particles: Union[pygame.sprite.Group, ParticlePool],
        trails: pygame.sprite.Group,
    ) -> None:
        """Установить группы спрайтов"""
        self.all_sprites = all_sprites
        self.powerups = powerups
        self.particles = particles
        self.trails = trails
    
    def clear(self) -> None:
        """Очистить экран"""
        self.game_surface.fill(self.theme.bg_color)
    
    def render_game(self, state_manager: Any, shake: Any) -> None:
        """
        Отрисовать игровой экран.

        Args:
            state_manager: Менеджер состояния игры
            shake: ScreenShake эффект
        """
        self.clear()

        # Draw net and score
        state_manager.draw_net()
        state_manager.draw_score()

        # Debug: check if sprites are set
        if self.all_sprites is None:
            from PyPong.core.logger import logger
            logger.warning("render_game: all_sprites is None!")

        # Draw sprites
        if self.trails:
            self.trails.draw(self.game_surface)
        if self.all_sprites:
            self.all_sprites.draw(self.game_surface)
        if self.powerups:
            self.powerups.draw(self.game_surface)
        if self.particles:
            # Поддержка как sprite.Group, так и ParticlePool
            if isinstance(self.particles, ParticlePool):
                self.particles.draw(self.game_surface)
            else:
                self.particles.draw(self.game_surface)
        
        # Draw touch controls
        if self.settings.get("touch_controls", False):
            from PyPong.mobile import TouchControls
            # Touch controls already have draw method
        
        # Draw tournament status
        if state_manager.tournament_mode:
            state_manager.tournament.draw_status(self.game_surface)
        
        # Draw FPS
        if self.settings.get("show_fps", False):
            from PyPong.ui.ui import FPSCounter
            # FPS counter draw
    
    def render_menu(self, state_manager: Any) -> None:
        """Отрисовать меню"""
        self.game_surface.fill(BLACK)
        state_manager.draw_menu()
    
    def render_mode_select(self, state_manager: Any) -> None:
        """Отрисовать выбор режима"""
        self.game_surface.fill(BLACK)
        state_manager.draw_mode_select()
    
    def render_pause(self, state_manager: Any) -> None:
        """Отрисовать паузу"""
        # Сначала отрисовать игру
        self.render_game(state_manager, None)
        # Затем overlay паузы
        state_manager.draw_pause()
    
    def render_game_over(self, state_manager: Any) -> None:
        """Отрисовать конец игры"""
        self.game_surface.fill(BLACK)
        state_manager.draw_game_over()
    
    def render_stats(self, state_manager: Any, stats_manager: Any) -> None:
        """Отрисовать статистику"""
        self.game_surface.fill(BLACK)
        state_manager.draw_stats(stats_manager)
    
    def render_help(self, state_manager: Any) -> None:
        """Отрисовать справку"""
        self.game_surface.fill(BLACK)
        state_manager.draw_help()
    
    def render_settings(self, settings_menu: Any) -> None:
        """Отрисовать настройки"""
        settings_menu.draw()
    
    def render_tournament_complete(self, tournament: Any) -> None:
        """Отрисовать завершение турнира"""
        tournament.draw_winner_screen(self.game_surface)
    
    def apply_screen_effects(self, shake: Any) -> None:
        """
        Применить эффекты экрана и масштабировать.
        
        Args:
            shake: ScreenShake эффект
        """
        scaled_surface = self.adaptive_screen.get_scaled_surface(self.game_surface)
        self.screen.fill(BLACK)
        shake.apply(scaled_surface, self.screen)
        pygame.display.flip()
    
    def render(
        self,
        state: GameState,
        state_manager: Any,
        shake: Any,
        settings_menu: Any = None,
        stats_manager: Any = None,
        tournament: Any = None,
    ) -> None:
        """
        Основной метод отрисовки.
        
        Args:
            state: Текущее состояние игры
            state_manager: Менеджер состояния
            shake: ScreenShake эффект
            settings_menu: Меню настроек
            stats_manager: Менеджер статистики
            tournament: Турнирный менеджер
        """
        renderers = {
            GameState.MENU: lambda: self.render_menu(state_manager),
            GameState.MODE_SELECT: lambda: self.render_mode_select(state_manager),
            GameState.PLAYING: lambda: self.render_game(state_manager, shake),
            GameState.PAUSED: lambda: self.render_pause(state_manager),
            GameState.GAME_OVER: lambda: self.render_game_over(state_manager),
            GameState.STATS: lambda: self.render_stats(state_manager, stats_manager),
            GameState.SETTINGS: lambda: self.render_settings(settings_menu),
            GameState.HELP: lambda: self.render_help(state_manager),
            GameState.TOURNAMENT_COMPLETE: lambda: self.render_tournament_complete(tournament),
        }
        
        render_func = renderers.get(state)
        if render_func:
            render_func()
        
        self.apply_screen_effects(shake)
