import math
import pygame
from random import randint, uniform
from config import *

class Particle(pygame.sprite.Sprite):
    def __init__(self, x, y, color=WHITE):
        super().__init__()
        self.size = randint(2, 5)
        self.image = pygame.Surface([self.size, self.size])
        self.image.fill(color)
        self.rect = self.image.get_rect(center=(x, y))
        
        angle = uniform(0, 360)
        speed = uniform(1, 4)
        import math
        rad = math.radians(angle)
        self.velocity_x = speed * math.cos(rad)
        self.velocity_y = speed * math.sin(rad)
        
        self.lifetime = randint(20, 40)
        self.age = 0

    def update(self):
        self.rect.x += self.velocity_x
        self.rect.y += self.velocity_y
        self.velocity_y += 0.2  # Gravity
        self.age += 1
        
        if self.age >= self.lifetime:
            self.kill()

class Trail(pygame.sprite.Sprite):
    def __init__(self, x, y, size=8):
        super().__init__()
        self.image = pygame.Surface([size, size])
        self.image.fill(WHITE)
        self.image.set_alpha(150)
        self.rect = self.image.get_rect(center=(x, y))
        self.lifetime = 10
        self.age = 0

    def update(self):
        self.age += 1
        alpha = int(150 * (1 - self.age / self.lifetime))
        self.image.set_alpha(max(0, alpha))
        
        if self.age >= self.lifetime:
            self.kill()

class ScreenShake:
    def __init__(self):
        self.offset_x = 0
        self.offset_y = 0
        self.intensity = 0
        self.duration = 0

    def start(self, intensity=10, duration=10):
        self.intensity = intensity
        self.duration = duration

    def update(self):
        if self.duration > 0:
            self.offset_x = randint(-self.intensity, self.intensity)
            self.offset_y = randint(-self.intensity, self.intensity)
            self.duration -= 1
            self.intensity = max(0, self.intensity - 1)
        else:
            self.offset_x = 0
            self.offset_y = 0

    def apply(self, surface, screen):
        screen.blit(surface, (self.offset_x, self.offset_y))

class GoalAnimation:
    def __init__(self):
        self.active = False
        self.timer = 0
        self.duration = 60
        self.player = None
        self.font = pygame.font.SysFont(FONT_NAME, 80)

    def start(self, player):
        self.active = True
        self.timer = 0
        self.player = player

    def update(self):
        if self.active:
            self.timer += 1
            if self.timer >= self.duration:
                self.active = False

    def draw(self, screen):
        if self.active:
            alpha = int(255 * (1 - self.timer / self.duration))
            text = self.font.render(f"GOAL! Player {self.player}", True, YELLOW)
            text.set_alpha(max(0, alpha))
            
            y_offset = -self.timer * 2
            rect = text.get_rect(center=(WINDOW_WIDTH // 2, WINDOW_HEIGHT // 2 + y_offset))
            screen.blit(text, rect)
