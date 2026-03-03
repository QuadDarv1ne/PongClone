"""Test AI system"""
import sys

sys.path.insert(0, ".")

import pygame

pygame.init()
screen = pygame.display.set_mode((1, 1))

from PyPong.core.entities import Ball, Paddle
from PyPong.systems.ai import AdaptiveAI, PredictiveAI, SimpleAI, create_ai

# Create paddle and ball
paddle = Paddle(player_number=2, is_ai=True)
ball = Ball()

# Test each AI type
print("Testing AI types:")

# Simple AI
ai_simple = create_ai(paddle, "Medium", "simple")
target = ai_simple.get_target_y(500, 360, -5, 0)
print(f"  SimpleAI target: {target}")

# Predictive AI
ai_pred = create_ai(paddle, "Medium", "predictive")
target = ai_pred.get_target_y(500, 360, -5, 0)
print(f"  PredictiveAI target: {target}")

# Adaptive AI
ai_adapt = create_ai(paddle, "Hard", "adaptive")
target = ai_adapt.get_target_y(500, 360, -5, 0)
print(f"  AdaptiveAI target: {target}")

# Test update method
print("\nTesting update:")
result = ai_pred.update(ball)
print(f"  Update result: {result}")

print("\nAll AI tests passed!")
pygame.quit()
