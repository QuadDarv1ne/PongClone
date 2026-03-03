"""Core game modules"""
from .config import (
    BALL_INITIAL_SPEED,
    BALL_SIZE,
    DIFFICULTY_LEVELS,
    FONT_NAME,
    PADDLE_HEIGHT,
    PADDLE_OFFSET,
    PADDLE_SPEED,
    PADDLE_WIDTH,
    WHITE,
    WINDOW_HEIGHT,
    WINDOW_WIDTH,
)
from .constants import (
    AchievementType,
    ArenaType,
    ChallengeType,
    Difficulty,
    EventType,
    GameMode,
    LogLevel,
    ModifierType,
    PowerUpType,
    SoundTheme,
)
from .logger import logger

# Lazy imports для модулей, требующих pygame
# from .entities import Paddle, Ball, PowerUp
# from .game_state import GameState, GameStateManager

__all__ = [
    "BALL_INITIAL_SPEED",
    "BALL_SIZE",
    "DIFFICULTY_LEVELS",
    "FONT_NAME",
    "PADDLE_HEIGHT",
    "PADDLE_OFFSET",
    "PADDLE_SPEED",
    "PADDLE_WIDTH",
    "WHITE",
    "WINDOW_HEIGHT",
    "WINDOW_WIDTH",
    "AchievementType",
    "ArenaType",
    "ChallengeType",
    "Difficulty",
    "EventType",
    "GameMode",
    "LogLevel",
    "ModifierType",
    "PowerUpType",
    "SoundTheme",
    "logger",
]
