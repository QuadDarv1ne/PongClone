"""Core game modules"""
from .config import *
from .constants import *
from .logger import logger

# Lazy imports для модулей, требующих pygame
# from .entities import Paddle, Ball, PowerUp
# from .game_state import GameState, GameStateManager

__all__ = [
    'logger',
]
