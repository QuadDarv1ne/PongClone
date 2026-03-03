"""
Environment configuration loader
Loads settings from .env file or environment variables
"""
import os
from pathlib import Path
from typing import Any, Optional


class EnvConfig:
    """Load configuration from environment variables"""

    def __init__(self, env_file: Optional[str] = None):
        """
        Initialize environment configuration

        Args:
            env_file: Path to .env file (optional)
        """
        self._config = {}
        if env_file:
            self._load_env_file(env_file)

    def _load_env_file(self, env_file: str) -> None:
        """Load variables from .env file"""
        env_path = Path(env_file)
        if not env_path.exists():
            return

        try:
            with open(env_path, "r", encoding="utf-8") as f:
                for line in f:
                    line = line.strip()
                    if not line or line.startswith("#"):
                        continue

                    if "=" in line:
                        key, value = line.split("=", 1)
                        self._config[key.strip()] = value.strip()
        except Exception as e:
            print(f"Warning: Failed to load .env file: {e}")

    def get(self, key: str, default: Any = None, cast_type: type = str) -> Any:
        """
        Get configuration value

        Args:
            key: Configuration key
            default: Default value if not found
            cast_type: Type to cast the value to

        Returns:
            Configuration value
        """
        # Priority: OS environment > .env file > default
        value = os.environ.get(key) or self._config.get(key)

        if value is None:
            return default

        # Type casting
        try:
            if cast_type == bool:
                return value.lower() in ("true", "1", "yes", "on")
            elif cast_type == int:
                return int(value)
            elif cast_type == float:
                return float(value)
            else:
                return value
        except (ValueError, AttributeError):
            return default

    def get_int(self, key: str, default: int = 0) -> int:
        """Get integer configuration value"""
        return self.get(key, default, int)

    def get_float(self, key: str, default: float = 0.0) -> float:
        """Get float configuration value"""
        return self.get(key, default, float)

    def get_bool(self, key: str, default: bool = False) -> bool:
        """Get boolean configuration value"""
        return self.get(key, default, bool)


# Global instance
_env_config: Optional[EnvConfig] = None


def init_env_config(env_file: str = ".env") -> EnvConfig:
    """Initialize global environment configuration"""
    global _env_config
    _env_config = EnvConfig(env_file)
    return _env_config


def get_env_config() -> EnvConfig:
    """Get global environment configuration instance"""
    global _env_config
    if _env_config is None:
        _env_config = EnvConfig()
    return _env_config
