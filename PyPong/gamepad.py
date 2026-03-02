"""
Gamepad manager with visual indicators
"""
import pygame
from typing import Dict, List, Optional
from PyPong.core.logger import logger


class GamepadManager:
    """
    Менеджер геймпадов с визуальными индикаторами.
    """
    
    def __init__(self) -> None:
        pygame.joystick.init()
        self.joysticks: List[pygame.joystick.Joystick] = []
        self._connected_players: Dict[int, int] = {}  # player -> joystick_id
        self.detect_joysticks()
    
    def detect_joysticks(self) -> None:
        """Обнаружить подключенные геймпады"""
        self.joysticks = []
        self._connected_players = {}
        
        for i in range(pygame.joystick.get_count()):
            try:
                joystick = pygame.joystick.Joystick(i)
                joystick.init()
                self.joysticks.append(joystick)
                self._connected_players[i + 1] = i
                logger.info(f"Gamepad connected: {joystick.get_name()} (ID={i})")
            except pygame.error as e:
                logger.warning(f"Failed to initialize gamepad {i}: {e}")
        
        logger.info(f"Total gamepads detected: {len(self.joysticks)}")
    
    def get_input(self, player: int) -> Dict[str, bool]:
        """
        Получить ввод с геймпада игрока.
        
        Args:
            player: Номер игрока (1 или 2)
            
        Returns:
            dict: Состояние кнопок {'up': bool, 'down': bool}
        """
        if player == 1 and len(self.joysticks) > 0:
            return self._get_joystick_input(self.joysticks[0])
        elif player == 2 and len(self.joysticks) > 1:
            return self._get_joystick_input(self.joysticks[1])
        return {"up": False, "down": False}
    
    def _get_joystick_input(self, joystick: pygame.joystick.Joystick) -> Dict[str, bool]:
        """Получить ввод с конкретного геймпада"""
        try:
            axis_y = joystick.get_axis(1)
            deadzone = 0.3
            
            # Левый стик (ось Y) или крестовина (кнопки 11, 12)
            up = axis_y < -deadzone or joystick.get_button(11)
            down = axis_y > deadzone or joystick.get_button(12)
            
            return {"up": up, "down": down}
        except pygame.error as e:
            logger.error(f"Error reading gamepad input: {e}")
            return {"up": False, "down": False}
    
    def has_gamepad(self, player: int) -> bool:
        """
        Проверить наличие геймпада у игрока.
        
        Args:
            player: Номер игрока (1 или 2)
            
        Returns:
            bool: True если геймпад подключен
        """
        if player == 1:
            return len(self.joysticks) > 0
        elif player == 2:
            return len(self.joysticks) > 1
        return False
    
    def get_gamepad_count(self) -> int:
        """Получить количество подключенных геймпадов"""
        return len(self.joysticks)
    
    def get_gamepad_name(self, player: int) -> Optional[str]:
        """
        Получить название геймпада игрока.
        
        Args:
            player: Номер игрока
            
        Returns:
            str или None: Название геймпада
        """
        if player == 1 and len(self.joysticks) > 0:
            return self.joysticks[0].get_name()
        elif player == 2 and len(self.joysticks) > 1:
            return self.joysticks[1].get_name()
        return None
    
    def draw_indicators(
        self, 
        surface: pygame.Surface, 
        font: pygame.font.Font
    ) -> None:
        """
        Отрисовать индикаторы подключенных геймпадов.
        
        Args:
            surface: Поверхность для отрисовки
            font: Шрифт для текста
        """
        if not self.joysticks:
            return
        
        y_offset = 10
        for i, joystick in enumerate(self.joysticks):
            player_num = i + 1
            name = joystick.get_name()[:20]  # Обрезать длинные названия
            
            # Текст индикатора
            text = f"P{player_num}: {name}"
            color = (0, 255, 0) if self.has_gamepad(player_num) else (255, 0, 0)
            
            text_surface = font.render(text, True, color)
            surface.blit(text_surface, (10, y_offset))
            y_offset += 20
    
    def draw_button_prompts(
        self,
        surface: pygame.Surface,
        font: pygame.font.Font,
        position: tuple = (100, 100)
    ) -> None:
        """
        Отрисовать подсказки кнопок для геймпада.
        
        Args:
            surface: Поверхность для отрисовки
            font: Шрифт для текста
            position: Позиция на экране
        """
        if not self.joysticks:
            return
        
        x, y = position
        
        # Подсказки кнопок
        prompts = [
            ("L-Stick Up/Down", "Move"),
            ("D-Pad Up/Down", "Move"),
        ]
        
        for i, (button, action) in enumerate(prompts):
            text = f"{button}: {action}"
            text_surface = font.render(text, True, (200, 200, 200))
            surface.blit(text_surface, (x, y + i * 25))
