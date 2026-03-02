"""UI components for the game"""
import pygame
from typing import Any, Dict, List, Optional, Tuple, Union
from PyPong.core.config import (
    WHITE, BLACK, GRAY, LIGHT_BLUE, RED, GREEN, YELLOW,
    FONT_NAME, WINDOW_WIDTH, WINDOW_HEIGHT,
)
from PyPong.core.entities import Paddle, PowerUp
from PyPong.systems.settings import Settings


class PowerUpIndicator:
    """Индикатор активных power-up"""
    
    def __init__(self) -> None:
        self.font = pygame.font.SysFont(FONT_NAME, 24)
        self.small_font = pygame.font.SysFont(FONT_NAME, 18)
    
    def draw(
        self, 
        screen: pygame.Surface, 
        powerups: pygame.sprite.Group,
        paddle1: Paddle, 
        paddle2: Paddle
    ) -> None:
        """Отрисовать индикаторы power-up"""
        y_offset = 150
        
        name_map: Dict[str, str] = {
            "speed_boost": "Speed Boost",
            "large_paddle": "Large Paddle",
            "slow_ball": "Slow Ball",
            "multi_ball": "Multi Ball",
            "shrink_opponent": "Shrink Opponent"
        }
        
        for powerup in powerups:
            if powerup.active:
                paddle = paddle1 if powerup.affected_paddle == paddle1 else paddle2
                x_pos = 20 if paddle == paddle1 else WINDOW_WIDTH - 220
                
                # Background
                bg_rect = pygame.Rect(x_pos, y_offset, 200, 50)
                pygame.draw.rect(screen, (40, 40, 40), bg_rect)
                pygame.draw.rect(screen, WHITE, bg_rect, 2)
                
                # Power-up name
                name = self.font.render(
                    name_map.get(powerup.type, "Power-Up"), 
                    True, WHITE
                )
                screen.blit(name, (x_pos + 10, y_offset + 5))
                
                # Timer bar
                elapsed = pygame.time.get_ticks() - powerup.start_time
                duration = powerup.TYPES[powerup.type]["duration"]
                progress = 1.0 - (elapsed / duration)
                
                bar_width = 180
                bar_height = 10
                
                pygame.draw.rect(screen, (60, 60, 60), (x_pos + 10, y_offset + 32, bar_width, bar_height))
                pygame.draw.rect(screen, GREEN, (x_pos + 10, y_offset + 32, int(bar_width * progress), bar_height))
                
                y_offset += 60


class FPSCounter:
    """Счётчик FPS"""
    
    def __init__(self) -> None:
        self.font = pygame.font.SysFont(FONT_NAME, 20)
    
    def draw(self, screen: pygame.Surface, clock: pygame.time.Clock) -> None:
        """Отрисовать FPS"""
        fps = int(clock.get_fps())
        color = GREEN if fps >= 55 else YELLOW if fps >= 30 else RED
        fps_text = self.font.render(f"FPS: {fps}", True, color)
        screen.blit(fps_text, (WINDOW_WIDTH - 100, 10))


class SettingsMenu:
    """Меню настроек"""
    
    def __init__(self, screen: pygame.Surface, settings: Settings) -> None:
        self.screen = screen
        self.settings = settings
        self.font = pygame.font.SysFont(FONT_NAME, 36)
        self.small_font = pygame.font.SysFont(FONT_NAME, 28)
        self.selected = 0
        self.options: List[str] = [
            "music_volume",
            "sfx_volume",
            "show_fps",
            "fullscreen",
            "touch_controls",
            "theme",
            "back"
        ]
    
    def draw(self) -> None:
        """Отрисовать меню настроек"""
        self.screen.fill(GRAY)
        
        title = self.font.render("Settings", True, WHITE)
        self.screen.blit(title, title.get_rect(center=(WINDOW_WIDTH // 2, 100)))
        
        for i, option in enumerate(self.options):
            color = YELLOW if i == self.selected else WHITE
            display_name = option.replace("_", " ").title()
            
            # Get current value
            if option != "back":
                value = self.settings.get(option, "N/A")
                if isinstance(value, float):
                    value = f"{value:.2f}"
                text = f"{display_name}: {value}"
            else:
                text = display_name
            
            text_surface = self.small_font.render(text, True, color)
            self.screen.blit(
                text_surface, 
                text_surface.get_rect(center=(WINDOW_WIDTH // 2, 180 + i * 50))
            )
    
    def handle_input(self, event: pygame.event.Event) -> Optional[str]:
        """
        Обработать ввод в меню настроек.
        
        Args:
            event: Событие pygame
            
        Returns:
            str или None: "back" если нажат ESC, иначе None
        """
        if event.type != pygame.KEYDOWN:
            return None
        
        if event.key == pygame.K_ESCAPE:
            return "back"
        
        if event.key == pygame.K_UP:
            self.selected = (self.selected - 1) % len(self.options)
        elif event.key == pygame.K_DOWN:
            self.selected = (self.selected + 1) % len(self.options)
        elif event.key == pygame.K_LEFT:
            self._adjust_value(-1)
        elif event.key == pygame.K_RIGHT:
            self._adjust_value(1)
        elif event.key == pygame.K_RETURN and self.options[self.selected] == "back":
            return "back"
        
        return None
    
    def _adjust_value(self, direction: int) -> None:
        """Изменить значение выбранной настройки"""
        option = self.options[self.selected]
        
        if option == "back":
            return
        
        current = self.settings.get(option)
        
        if option in ["music_volume", "sfx_volume"]:
            new_value = max(0.0, min(1.0, current + direction * 0.1))
            self.settings.set(option, round(new_value, 1))
        elif option in ["show_fps", "fullscreen", "touch_controls"]:
            self.settings.set(option, not current)
        elif option == "theme":
            themes = ["classic", "dark", "neon", "retro", "ocean"]
            current_idx = themes.index(current) if current in themes else 0
            new_idx = (current_idx + direction) % len(themes)
            self.settings.set(option, themes[new_idx])
