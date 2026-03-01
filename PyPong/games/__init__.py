"""
Game modes for PyPong
"""
from .base import GameMode, GameModeType
from .classic import ClassicMode
from .arcade import ArcadeMode

__all__ = [
    'GameMode',
    'GameModeType', 
    'ClassicMode',
    'ArcadeMode',
]
