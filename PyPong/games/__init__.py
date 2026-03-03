"""
Game modes for PyPong
"""
from .arcade import ArcadeMode
from .base import GameMode, GameModeType
from .classic import ClassicMode

__all__ = [
    "GameMode",
    "GameModeType",
    "ClassicMode",
    "ArcadeMode",
]
