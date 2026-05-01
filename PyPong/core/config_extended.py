"""
Configuration system with external file support and environment variables
"""
import json
import os
from pathlib import Path
from typing import Any, Dict, Optional
from dataclasses import dataclass, field

from PyPong.core.env_config import get_env_config


# Default configuration values
DEFAULT_CONFIG = {
    # Window
    "window_width": 1024,
    "window_height": 720,
    "fps": 60,
    "fullscreen": False,
    
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
    "music_volume": 0.5,
    "sfx_volume": 0.7,
    "enable_music": True,
    
    # Font
    "font_name": "Helvetica",
    
    # Performance
    "max_particles": 50,
    "max_trails": 20,
    "enable_effects": True,
    
    # Debug
    "show_fps": False,
    "log_level": "INFO",
    "debug": False,
    
    # Mobile
    "touch_controls": False,
    "adaptive_resolution": True,
    
    # Localization
    "language": "ru",
}


@dataclass
class Config:
    """
    Game configuration with file loading support and environment variables.
    Priority: Environment variables > config.json > defaults
    Use: config.window_width, config.colors.white, etc.
    """
    _data: Dict[str, Any] = field(default_factory=lambda: DEFAULT_CONFIG.copy())
    _config_file: Optional[Path] = None
    
    def __post_init__(self):
        self._load_from_file()
        self._load_from_env()
    
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
                    # Config file not found or invalid, continue to next path
                    pass
    
    def _load_from_env(self):
        """Load configuration from environment variables (highest priority)"""
        try:
            env = get_env_config()
            
            # Map environment variables to config keys
            env_mappings = {
                'WINDOW_WIDTH': ('window_width', int),
                'WINDOW_HEIGHT': ('window_height', int),
                'FPS': ('fps', int),
                'FULLSCREEN': ('fullscreen', bool),
                'WINNING_SCORE': ('winning_score', int),
                'MUSIC_VOLUME': ('music_volume', float),
                'SFX_VOLUME': ('sfx_volume', float),
                'ENABLE_MUSIC': ('enable_music', bool),
                'MAX_PARTICLES': ('max_particles', int),
                'MAX_TRAILS': ('max_trails', int),
                'ENABLE_EFFECTS': ('enable_effects', bool),
                'DEBUG': ('debug', bool),
                'LOG_LEVEL': ('log_level', str),
                'SHOW_FPS': ('show_fps', bool),
                'TOUCH_CONTROLS': ('touch_controls', bool),
                'ADAPTIVE_RESOLUTION': ('adaptive_resolution', bool),
                'LANGUAGE': ('language', str),
                'DIFFICULTY': ('default_difficulty', str),
            }
            
            for env_key, (config_key, cast_type) in env_mappings.items():
                value = env.get(env_key, cast_type=cast_type)
                if value is not None:
                    self.set(config_key, value)
        except Exception as e:
            # If env config fails, just use file/defaults
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
    def fullscreen(self) -> bool:
        return self._data["fullscreen"]
    
    @property
    def winning_score(self) -> int:
        return self._data["winning_score"]
    
    @property
    def colors(self) -> Dict[str, tuple]:
        return self._data["colors"]
    
    @property
    def difficulty_levels(self) -> Dict[str, dict]:
        return self._data["difficulty_levels"]
    
    @property
    def music_volume(self) -> float:
        return self._data["music_volume"]
    
    @property
    def sfx_volume(self) -> float:
        return self._data["sfx_volume"]
    
    @property
    def max_particles(self) -> int:
        return self._data["max_particles"]
    
    @property
    def max_trails(self) -> int:
        return self._data["max_trails"]
    
    @property
    def debug(self) -> bool:
        return self._data["debug"]


# Global config instance
config = Config()
