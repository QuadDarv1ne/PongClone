"""
Configuration system with external file support
"""
import json
import os
from pathlib import Path
from typing import Any, Dict, Optional
from dataclasses import dataclass, field


# Default configuration values
DEFAULT_CONFIG = {
    # Window
    "window_width": 1024,
    "window_height": 720,
    "fps": 60,
    
    # Colors (RGB)
    "colors": {
        "white": (255, 255, 255),
        "black": (0, 0, 0),
        "gray": (80, 80, 80),
        "light_blue": (173, 216, 230),
        "red": (255, 0, 0),
        "green": (0, 255, 0),
        "yellow": (255, 255, 0),
    },
    
    # Paddle
    "paddle_width": 10,
    "paddle_height": 100,
    "paddle_speed": 10,
    "paddle_offset": 50,
    
    # Ball
    "ball_size": 10,
    "ball_initial_speed": 4,
    "ball_speed_increase": 1.1,
    "max_ball_speed": 20,
    
    # Game
    "winning_score": 5,
    "powerup_duration": 5000,
    "powerup_spawn_chance": 500,
    
    # AI
    "difficulty_levels": {
        "Easy": {"ai_speed": 4, "ball_increase": 1.05},
        "Medium": {"ai_speed": 6, "ball_increase": 1.1},
        "Hard": {"ai_speed": 8, "ball_increase": 1.2},
    },
    
    # Audio
    "music_file": "endofline.ogg",
    "beep_sound": "beep.wav",
    "score_sound": "score.wav",
    "powerup_sound": "powerup.wav",
    
    # Font
    "font_name": "Helvetica",
    
    # Debug
    "show_fps": False,
    "log_level": "INFO",
}


@dataclass
class Config:
    """
    Game configuration with file loading support.
    Use: config.window_width, config.colors.white, etc.
    """
    _data: Dict[str, Any] = field(default_factory=lambda: DEFAULT_CONFIG.copy())
    _config_file: Optional[Path] = None
    
    def __post_init__(self):
        self._load_from_file()
    
    def _load_from_file(self):
        """Load configuration from JSON file if exists"""
        # Check for config.json in project root
        possible_paths = [
            Path("config.json"),
            Path("PyPong/config.json"),
            Path(__file__).parent.parent / "config.json",
        ]
        
        for path in possible_paths:
            if path.exists():
                try:
                    with open(path, 'r') as f:
                        user_config = json.load(f)
                    self._merge_config(user_config)
                    self._config_file = path
                    break
                except (json.JSONDecodeError, IOError):
                    pass
    
    def _merge_config(self, user_config: Dict[str, Any]):
        """Merge user config with defaults"""
        def deep_merge(base: dict, update: dict) -> dict:
            result = base.copy()
            for key, value in update.items():
                if key in result and isinstance(result[key], dict) and isinstance(value, dict):
                    result[key] = deep_merge(result[key], value)
                else:
                    result[key] = value
            return result
        
        self._data = deep_merge(self._data, user_config)
    
    def save(self, path: Optional[Path] = None):
        """Save current configuration to file"""
        save_path = path or self._config_file or Path("config.json")
        
        with open(save_path, 'w') as f:
            json.dump(self._data, f, indent=2)
        
        self._config_file = save_path
    
    def get(self, key: str, default: Any = None) -> Any:
        """Get config value by key (supports dot notation)"""
        keys = key.split('.')
        value = self._data
        
        for k in keys:
            if isinstance(value, dict):
                value = value.get(k)
                if value is None:
                    return default
            else:
                return default
        
        return value
    
    def set(self, key: str, value: Any):
        """Set config value by key"""
        keys = key.split('.')
        data = self._data
        
        for k in keys[:-1]:
            if k not in data:
                data[k] = {}
            data = data[k]
        
        data[keys[-1]] = value
    
    # Property accessors for common values
    @property
    def window_width(self) -> int:
        return self._data["window_width"]
    
    @property
    def window_height(self) -> int:
        return self._data["window_height"]
    
    @property
    def fps(self) -> int:
        return self._data["fps"]
    
    @property
    def winning_score(self) -> int:
        return self._data["winning_score"]
    
    @property
    def colors(self) -> Dict[str, tuple]:
        return self._data["colors"]
    
    @property
    def difficulty_levels(self) -> Dict[str, dict]:
        return self._data["difficulty_levels"]


# Global config instance
config = Config()
