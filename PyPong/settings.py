import json
import os

class Settings:
    def __init__(self, filename="settings.json"):
        self.filename = filename
        self.data = self.load_settings()

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
            "theme": "classic"
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
        self.save_settings()
