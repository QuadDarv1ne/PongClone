import pygame
from random import randint, choice
from config import *

class Paddle(pygame.sprite.Sprite):
    def __init__(self, player_number, is_ai=False, color=WHITE):
        super().__init__()
        self.player_number = player_number
        self.is_ai = is_ai
        self.color = color
        self.width = PADDLE_WIDTH
        self.height = PADDLE_HEIGHT
        self.speed = PADDLE_SPEED if not is_ai else DIFFICULTY_LEVELS["Medium"]["ai_speed"]
        self.image = pygame.Surface([self.width, self.height])
        self.image.fill(color)
        self.rect = self.image.get_rect()
        self.reset_position()
        self.original_height = PADDLE_HEIGHT

    def reset_position(self):
        if self.player_number == 1:
            self.rect.centerx = PADDLE_OFFSET
        else:
            self.rect.centerx = WINDOW_WIDTH - PADDLE_OFFSET
        self.rect.centery = WINDOW_HEIGHT // 2

    def move(self, up, down, ball_y=None):
        if self.is_ai and ball_y is not None:
            # Improved AI with prediction
            target_y = ball_y
            if abs(self.rect.centery - target_y) > 5:
                if self.rect.centery < target_y:
                    self.rect.y += self.speed
                else:
                    self.rect.y -= self.speed
        else:
            if up and self.rect.top > 5:
                self.rect.y -= self.speed
            elif down and self.rect.bottom < WINDOW_HEIGHT - 5:
                self.rect.y += self.speed

        # Keep paddle in bounds
        self.rect.clamp_ip(pygame.Rect(0, 0, WINDOW_WIDTH, WINDOW_HEIGHT))

    def resize(self, new_height):
        center = self.rect.center
        self.height = new_height
        self.image = pygame.Surface([self.width, self.height])
        self.image.fill(self.color)
        self.rect = self.image.get_rect(center=center)

    def reset_size(self):
        self.resize(self.original_height)

    def set_speed(self, speed):
        self.speed = speed


class Ball(pygame.sprite.Sprite):
    def __init__(self):
        super().__init__()
        self.image = pygame.Surface([BALL_SIZE, BALL_SIZE])
        self.image.fill(WHITE)
        self.rect = self.image.get_rect()
        self.velocity_x = 0
        self.velocity_y = 0
        self.speed = BALL_INITIAL_SPEED
        self.reset_ball()

    def reset_ball(self):
        self.rect.center = (WINDOW_WIDTH // 2, WINDOW_HEIGHT // 2)
        self.speed = BALL_INITIAL_SPEED
        
        # Random direction
        angle = choice([45, 135, 225, 315])
        import math
        rad = math.radians(angle)
        self.velocity_x = self.speed * math.cos(rad)
        self.velocity_y = self.speed * math.sin(rad)

    def move(self):
        self.rect.x += self.velocity_x
        self.rect.y += self.velocity_y

    def bounce_wall(self):
        if self.rect.top <= 0 or self.rect.bottom >= WINDOW_HEIGHT:
            self.velocity_y *= -1
            self.rect.clamp_ip(pygame.Rect(0, 0, WINDOW_WIDTH, WINDOW_HEIGHT))

    def bounce_paddle(self, paddle):
        # Calculate hit position on paddle (-1 to 1)
        hit_pos = (self.rect.centery - paddle.rect.centery) / (paddle.height / 2)
        hit_pos = max(-1, min(1, hit_pos))
        
        # Adjust angle based on hit position
        import math
        max_angle = 60
        angle = hit_pos * max_angle
        
        # Determine direction
        direction = 1 if paddle.player_number == 1 else -1
        
        # Calculate new velocity
        rad = math.radians(angle)
        self.velocity_x = direction * self.speed * math.cos(rad)
        self.velocity_y = self.speed * math.sin(rad)
        
        # Increase speed
        self.increase_speed()

    def increase_speed(self):
        if self.speed < MAX_BALL_SPEED:
            self.speed = min(self.speed * BALL_SPEED_INCREASE, MAX_BALL_SPEED)
            # Update velocity magnitude
            import math
            current_angle = math.atan2(self.velocity_y, self.velocity_x)
            self.velocity_x = self.speed * math.cos(current_angle)
            self.velocity_y = self.speed * math.sin(current_angle)

    def is_out_left(self):
        return self.rect.right < 0

    def is_out_right(self):
        return self.rect.left > WINDOW_WIDTH


class PowerUp(pygame.sprite.Sprite):
    TYPES = {
        "speed_boost": {"color": GREEN, "duration": POWERUP_DURATION},
        "large_paddle": {"color": YELLOW, "duration": POWERUP_DURATION},
        "slow_ball": {"color": LIGHT_BLUE, "duration": POWERUP_DURATION},
        "multi_ball": {"color": RED, "duration": 0},
        "shrink_opponent": {"color": (255, 165, 0), "duration": POWERUP_DURATION},
    }

    def __init__(self):
        super().__init__()
        self.type = choice(list(self.TYPES.keys()))
        self.image = pygame.Surface([20, 20])
        self.image.fill(self.TYPES[self.type]["color"])
        self.rect = self.image.get_rect()
        self.rect.center = (
            randint(WINDOW_WIDTH // 4, 3 * WINDOW_WIDTH // 4),
            randint(50, WINDOW_HEIGHT - 50)
        )
        self.active = False
        self.start_time = 0
        self.affected_paddle = None

    def activate(self, paddle):
        self.active = True
        self.start_time = pygame.time.get_ticks()
        self.affected_paddle = paddle

        if self.type == "speed_boost":
            paddle.set_speed(paddle.speed * 1.5)
        elif self.type == "large_paddle":
            paddle.resize(150)
        elif self.type == "slow_ball":
            pass  # Handled in game logic
        elif self.type == "multi_ball":
            pass  # Handled in game logic
        elif self.type == "shrink_opponent":
            pass  # Handled in game logic

    def deactivate(self):
        if self.affected_paddle:
            if self.type == "speed_boost":
                self.affected_paddle.set_speed(PADDLE_SPEED)
            elif self.type == "large_paddle":
                self.affected_paddle.reset_size()
            elif self.type == "shrink_opponent":
                pass  # Handled in game logic
        self.kill()

    def update(self):
        if self.active:
            elapsed = pygame.time.get_ticks() - self.start_time
            if elapsed > self.TYPES[self.type]["duration"]:
                self.deactivate()
