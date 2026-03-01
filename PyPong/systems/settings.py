"""Settings manager for game configuration"""
import json
import os
import pygame
from pathlib import Path
from PyPong.core.logger import logger, log_exception


class Settings:
    def __init__(self, filename="settings.json"):
        # Use absolute path relative to this module
        self.filename = Path(__file__).parent.parent / 'data' / filename
        self.data = self.load_settings()
        self._pending_save = False
        self._save_timer = 0
        self._SAVE_DELAY = 1000  # Задержка сохранения в мс

    def load_settings(self):
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

    def default_settings(self):
        return {
            "music_volume": 0.5,
            "sfx_volume": 0.7,
            "difficulty": "Medium",
            "winning_score": 5,
            "show_fps": False,
            "fullscreen": False,
            "theme": "dark",
            "touch_controls": False
        }

    @log_exception
    def save_settings(self):
        try:
            # Ensure data directory exists
            self.filename.parent.mkdir(parents=True, exist_ok=True)
            with open(self.filename, 'w', encoding='utf-8') as f:
                json.dump(self.data, f, indent=2)
        except Exception as e:
            logger.error(f"Failed to save settings: {e}")

    def get(self, key, default=None):
        return self.data.get(key, default)

    def set(self, key, value):
        self.data[key] = value
        self._pending_save = True
        self._save_timer = pygame.time.get_ticks()

    def update(self):
        """Проверить и выполнить отложенное сохранение"""
        if self._pending_save:
            current_time = pygame.time.get_ticks()
            if current_time - self._save_timer >= self._SAVE_DELAY:
                self.save_settings()
                self._pending_save = False

    def force_save(self):
        """Принудительное сохранение (при выходе)"""
        if self._pending_save:
            self.save_settings()
            self._pending_save = False
