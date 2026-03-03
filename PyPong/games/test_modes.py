"""Quick test of new game modes"""
import sys
from pathlib import Path

# Add current directory (PongClone root) to path
root = Path(__file__).parent.parent.parent
if str(root) not in sys.path:
    sys.path.insert(0, str(root))

import pygame

from PyPong.games import ArcadeMode, ClassicMode, GameModeType
from PyPong.games.engine import GameEngine

pygame.init()
screen = pygame.display.set_mode((1024, 720))

# Test ClassicMode
classic = ClassicMode(screen, {"ai_enabled": True, "ai_difficulty": "Medium"})
print(f"Classic mode type: {classic.mode_type}")
print(f"Classic winning score: {classic.winning_score}")

# Test ArcadeMode
arcade = ArcadeMode(screen, {"ai_enabled": True})
print(f"Arcade mode type: {arcade.mode_type}")
print(f'Arcade has powerups: {hasattr(arcade, "powerups")}')

# Test GameEngine
engine = GameEngine()
print(f"Engine has modes: {len(engine.available_modes)}")
print(f"Current mode: {engine.current_mode_type}")

print("\nAll tests passed!")
pygame.quit()
