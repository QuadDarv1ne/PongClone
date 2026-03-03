"""
Centralized logging system for the game
"""
import logging
import sys
from datetime import datetime
from pathlib import Path
from typing import Optional

from PyPong.core.constants import LogLevel


class GameLogger:
    """Centralized logger for the game"""

    _instance: Optional["GameLogger"] = None

    def __new__(cls) -> "GameLogger":
        if cls._instance is None:
            cls._instance = super().__new__(cls)
        return cls._instance

    def __init__(self) -> None:
        if hasattr(self, "_initialized"):
            return

        self._initialized = True
        self.logger = logging.getLogger("PyPong")
        self.logger.setLevel(logging.DEBUG)

        # Create logs directory
        log_dir = Path("logs")
        log_dir.mkdir(exist_ok=True)

        # File handler with rotation
        log_file = log_dir / f'pong_{datetime.now().strftime("%Y%m%d")}.log'
        file_handler = logging.FileHandler(log_file, encoding="utf-8")
        file_handler.setLevel(logging.DEBUG)

        # Console handler
        console_handler = logging.StreamHandler(sys.stdout)
        console_handler.setLevel(logging.INFO)

        # Formatter
        formatter = logging.Formatter(
            "%(asctime)s - %(name)s - %(levelname)s - %(message)s", datefmt="%Y-%m-%d %H:%M:%S"
        )
        file_handler.setFormatter(formatter)
        console_handler.setFormatter(formatter)

        # Add handlers
        self.logger.addHandler(file_handler)
        self.logger.addHandler(console_handler)

    def debug(self, message: str, **kwargs) -> None:
        """Log debug message"""
        self.logger.debug(message, extra=kwargs)

    def info(self, message: str, **kwargs) -> None:
        """Log info message"""
        self.logger.info(message, extra=kwargs)

    def warning(self, message: str, **kwargs) -> None:
        """Log warning message"""
        self.logger.warning(message, extra=kwargs)

    def error(self, message: str, exc_info: bool = False, **kwargs) -> None:
        """Log error message"""
        self.logger.error(message, exc_info=exc_info, extra=kwargs)

    def critical(self, message: str, exc_info: bool = True, **kwargs) -> None:
        """Log critical message"""
        self.logger.critical(message, exc_info=exc_info, extra=kwargs)

    def log_event(self, event_type: str, details: dict) -> None:
        """Log game event"""
        self.info(f"Event: {event_type}", extra=details)

    def log_performance(self, operation: str, duration_ms: float) -> None:
        """Log performance metrics"""
        if duration_ms > 16.67:  # Slower than 60 FPS
            self.warning(f"Performance: {operation} took {duration_ms:.2f}ms")
        else:
            self.debug(f"Performance: {operation} took {duration_ms:.2f}ms")


# Global logger instance
logger = GameLogger()


def log_exception(func):
    """Decorator to log exceptions"""

    def wrapper(*args, **kwargs):
        try:
            return func(*args, **kwargs)
        except Exception as e:
            logger.error(f"Exception in {func.__name__}: {str(e)}", exc_info=True)
            raise

    return wrapper


def log_performance(func):
    """Decorator to log function performance"""
    import time

    def wrapper(*args, **kwargs):
        start = time.perf_counter()
        result = func(*args, **kwargs)
        duration = (time.perf_counter() - start) * 1000
        logger.log_performance(func.__name__, duration)
        return result

    return wrapper
