"""Settings manager for game configuration"""
import json
import pygame
from pathlib import Path
from typing import Any, Optional, Dict
from PyPong.core.logger import logger, log_exception


class Settings:
    """
    Менеджер настроек игры с автосохранением.
    """
    
    def __init__(self, filename: str = "settings.json") -> None:
        self.filename = Path(__file__).parent.parent / 'data' / filename
        self.data: Dict[str, Any] = self.load_settings()
        self._pending_save: bool = False
        self._save_timer: int = 0
        self._SAVE_DELAY: int = 1000  # Задержка сохранения в мс
    
    def load_settings(self) -> Dict[str, Any]:
        """Загрузить настройки из файла"""
        if self.filename.exists():
            try:
                with open(self.filename, 'r', encoding='utf-8') as f:
                    return json.load(f)
            except json.JSONDecodeError as e:
                logger.error(f"Failed to parse settings file: {e}")
                return self.default_settings()
            except Exception as e:
                logger.error(f"Failed to load settings: {e}")
                return self.default_settings()
        return self.default_settings()
    
    def default_settings(self) -> Dict[str, Any]:
        """Настройки по умолчанию"""
        return {
            "music_volume": 0.5,
            "sfx_volume": 0.7,
            "difficulty": "Medium",
            "winning_score": 5,
            "show_fps": False,
            "fullscreen": False,
            "theme": "dark",
            "touch_controls": False,
            "has_seen_onboarding": False,
            "language": "en",
            # Auto-detect placeholders (filled on first launch)
            "auto_detected": False,
            "window_width": None,
            "window_height": None,
            "performance_profile": "medium",
            "max_particles": 50,
            "max_trails": 20,
            "target_fps": 60,
            "enable_shake": True,
            "enable_effects": True,
            # Sound theme
            "sound_theme": "classic",
            # Accessibility
            "colorblind_mode": "normal",
            "high_contrast": False,
            "reduce_motion": False,
            "audio_cues": True,
            "large_ui": False,
            # Window mode
            "window_mode": "windowed",
            # Ball and paddle
            "ball_speed": 4,
            "paddle_size": 100,
            # Display
            "vsync": False,
            # Gameplay
            "powerup_spawn_chance": 500,
        }

    def is_first_launch(self) -> bool:
        """Проверить, первый ли это запуск (файл настроек не существует)"""
        return not self.filename.exists()
    
    @log_exception
    def save_settings(self) -> None:
        """Сохранить настройки в файл"""
        try:
            self.filename.parent.mkdir(parents=True, exist_ok=True)
            with open(self.filename, 'w', encoding='utf-8') as f:
                json.dump(self.data, f, indent=2)
        except Exception as e:
            logger.error(f"Failed to save settings: {e}")
    
    def get(self, key: str, default: Any = None) -> Any:
        """Получить значение настройки с автоматическим fallback на значения по умолчанию"""
        if key in self.data:
            return self.data[key]
        # Fall back to defaults for missing keys
        defaults = self.default_settings()
        return defaults.get(key, default)
    
    def set(self, key: str, value: Any) -> None:
        """Установить значение настройки"""
        self.data[key] = value
        self._pending_save = True
        self._save_timer = pygame.time.get_ticks()
    
    def update(self) -> None:
        """Проверить и выполнить отложенное сохранение"""
        if self._pending_save:
            current_time = pygame.time.get_ticks()
            if current_time - self._save_timer >= self._SAVE_DELAY:
                self.save_settings()
                self._pending_save = False
    
    def force_save(self) -> None:
        """Принудительное сохранение (при выходе)"""
        if self._pending_save:
            self.save_settings()
            self._pending_save = False
