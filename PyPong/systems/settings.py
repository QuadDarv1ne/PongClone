import json
import os
import pygame

class Settings:
    def __init__(self, filename="PyPong/data/settings.json"):
        self.filename = filename
        self.data = self.load_settings()
        self._pending_save = False
        self._save_timer = 0
        self._SAVE_DELAY = 1000  # Задержка сохранения в мс

    def load_settings(self):
        if os.path.exists(self.filename):
            try:
                with open(self.filename, 'r') as f:
                    return json.load(f)
            except:
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
            "theme": "dark",  # Dark theme by default
            "touch_controls": False
        }

    def save_settings(self):
        try:
            with open(self.filename, 'w') as f:
                json.dump(self.data, f, indent=2)
        except:
            pass

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
