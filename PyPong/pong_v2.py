import pygame, sys, time
from pygame.locals import *
from random import randint, choice

# Initialize Pygame
pygame.init()

# Screen dimensions
WINDOW_WIDTH = 1024
WINDOW_HEIGHT = 720

# Colors
WHITE = (255, 255, 255)
BLACK = (0, 0, 0)
GRAY = (80, 80, 80)
LIGHT_BLUE = (173, 216, 230)
RED = (255, 0, 0)

# Game constants
PADDLE_SPEED = 10
AI_PADDLE_SPEED = 6
BALL_SPEED_INCREASE = 1.1
MAX_BALL_SPEED = 20
FONT_NAME = "Helvetica"
POWERUP_DURATION = 5000  # Duration of power-ups in milliseconds

# Set up the main surface
main_surface = pygame.display.set_mode((WINDOW_WIDTH, WINDOW_HEIGHT))
pygame.display.set_caption("Enhanced Pong Game")

# Load sounds
pygame.mixer.music.load("endofline.ogg")
sound_effect = pygame.mixer.Sound("beep.wav")
score_sound = pygame.mixer.Sound("score.wav")

# Fonts
basic_font = pygame.font.SysFont(FONT_NAME, 120)
game_over_font_big = pygame.font.SysFont(FONT_NAME, 72)
game_over_font_small = pygame.font.SysFont(FONT_NAME, 50)
menu_font = pygame.font.SysFont(FONT_NAME, 40)

# Clock
clock = pygame.time.Clock()

class Paddle(pygame.sprite.Sprite):
    def __init__(self, player_number, is_ai=False):
        super().__init__()
        self.player_number = player_number
        self.is_ai = is_ai
        self.image = pygame.Surface([10, 100])
        self.image.fill(WHITE)
        self.rect = self.image.get_rect()
        self.speed = PADDLE_SPEED if not is_ai else AI_PADDLE_SPEED
        self.reset_position()

    def reset_position(self):
        if self.player_number == 1:
            self.rect.centerx = 50
        else:
            self.rect.centerx = WINDOW_WIDTH - 50
        self.rect.centery = WINDOW_HEIGHT // 2

    def move(self, up, down):
        if self.is_ai:
            if self.rect.centery < ball.rect.y:
                self.rect.y += self.speed
            elif self.rect.centery > ball.rect.y:
                self.rect.y -= self.speed
        else:
            if up and self.rect.top > 5:
                self.rect.y -= self.speed
            elif down and self.rect.bottom < WINDOW_HEIGHT - 5:
                self.rect.y += self.speed

class Ball(pygame.sprite.Sprite):
    def __init__(self):
        super().__init__()
        self.image = pygame.Surface([10, 10])
        self.image.fill(WHITE)
        self.rect = self.image.get_rect()
        self.reset_ball()

    def reset_ball(self):
        self.rect.center = (WINDOW_WIDTH // 2, WINDOW_HEIGHT // 2)
        self.direction = choice([0, 1, 2, 3])
        self.speed = 4

    def move(self):
        if self.direction == 0:
            self.rect.x -= self.speed
            self.rect.y -= self.speed
        elif self.direction == 1:
            self.rect.x += self.speed
            self.rect.y -= self.speed
        elif self.direction == 2:
            self.rect.x -= self.speed
            self.rect.y += self.speed
        elif self.direction == 3:
            self.rect.x += self.speed
            self.rect.y += self.speed

    def change_direction(self):
        if self.rect.y < 0 or self.rect.y > WINDOW_HEIGHT:
            self.direction = (self.direction + 2) % 4

    def increase_speed(self):
        self.speed = min(self.speed * BALL_SPEED_INCREASE, MAX_BALL_SPEED)

class PowerUp(pygame.sprite.Sprite):
    def __init__(self):
        super().__init__()
        self.image = pygame.Surface([20, 20])
        self.image.fill(LIGHT_BLUE)
        self.rect = self.image.get_rect()
        self.rect.topleft = (randint(50, WINDOW_WIDTH - 50), randint(50, WINDOW_HEIGHT - 50))
        self.type = choice(["speed_boost", "large_paddle", "slow_ball", "confuse_controls"])
        self.active = False
        self.start_time = 0

    def activate(self, paddle):
        self.active = True
        self.start_time = pygame.time.get_ticks()
        if self.type == "speed_boost":
            paddle.speed *= 1.5
        elif self.type == "large_paddle":
            paddle.image = pygame.Surface([10, 150])
            paddle.image.fill(WHITE)
            paddle.rect = paddle.image.get_rect(center=paddle.rect.center)
        elif self.type == "slow_ball":
            ball.speed = max(ball.speed * 0.8, 2)
        elif self.type == "confuse_controls":
            global UP1, DOWN1, UP2, DOWN2
            UP1, DOWN1, UP2, DOWN2 = DOWN1, UP1, DOWN2, UP2

    def deactivate(self, paddle):
        self.active = False
        if self.type == "speed_boost":
            paddle.speed = PADDLE_SPEED if not paddle.is_ai else AI_PADDLE_SPEED
        elif self.type == "large_paddle":
            paddle.image = pygame.Surface([10, 100])
            paddle.image.fill(WHITE)
            paddle.rect = paddle.image.get_rect(center=paddle.rect.center)
        elif self.type == "slow_ball":
            ball.speed = 4
        elif self.type == "confuse_controls":
            global UP1, DOWN1, UP2, DOWN2
            UP1, DOWN1, UP2, DOWN2 = DOWN1, UP1, DOWN2, UP2

    def update(self):
        if self.active and pygame.time.get_ticks() - self.start_time > POWERUP_DURATION:
            self.deactivate(paddle1 if self.player_number == 1 else paddle2)
            self.kill()

def draw_net():
    for i in range(0, WINDOW_HEIGHT, 60):
        pygame.draw.rect(main_surface, WHITE, (WINDOW_WIDTH // 2 - 2, i, 4, 30))

def show_score(player1_score, player2_score):
    score_text = basic_font.render(f"{player1_score}   {player2_score}", True, WHITE, BLACK)
    score_rect = score_text.get_rect(centerx=WINDOW_WIDTH // 2, y=10)
    main_surface.blit(score_text, score_rect)

def show_game_over(winner):
    game_over_text = game_over_font_big.render("GAME OVER", True, WHITE, BLACK)
    winner_text = game_over_font_small.render(f"Player {winner} Wins", True, WHITE, BLACK)
    game_over_rect = game_over_text.get_rect(center=(WINDOW_WIDTH // 2, WINDOW_HEIGHT // 2 - 50))
    winner_rect = winner_text.get_rect(center=(WINDOW_WIDTH // 2, WINDOW_HEIGHT // 2 + 25))
    main_surface.blit(game_over_text, game_over_rect)
    main_surface.blit(winner_text, winner_rect)
    pygame.display.update()
    pygame.time.wait(3000)

def show_menu():
    main_surface.fill(GRAY)
    title_text = game_over_font_big.render("Enhanced Pong", True, WHITE, BLACK)
    start_text = menu_font.render("Press Enter to Start", True, WHITE, BLACK)
    title_rect = title_text.get_rect(center=(WINDOW_WIDTH // 2, WINDOW_HEIGHT // 2 - 50))
    start_rect = start_text.get_rect(center=(WINDOW_WIDTH // 2, WINDOW_HEIGHT // 2 + 50))
    main_surface.blit(title_text, title_rect)
    main_surface.blit(start_text, start_rect)
    pygame.display.update()

    waiting = True
    while waiting:
        for event in pygame.event.get():
            if event.type == QUIT:
                pygame.quit()
                sys.exit()
            elif event.type == KEYDOWN and event.key == K_RETURN:
                waiting = False

def show_pause_menu():
    main_surface.fill(GRAY)
    pause_text = game_over_font_big.render("PAUSED", True, WHITE, BLACK)
    resume_text = menu_font.render("Press Enter to Resume", True, WHITE, BLACK)
    quit_text = menu_font.render("Press Escape to Quit", True, WHITE, BLACK)
    pause_rect = pause_text.get_rect(center=(WINDOW_WIDTH // 2, WINDOW_HEIGHT // 2 - 50))
    resume_rect = resume_text.get_rect(center=(WINDOW_WIDTH // 2, WINDOW_HEIGHT // 2))
    quit_rect = quit_text.get_rect(center=(WINDOW_WIDTH // 2, WINDOW_HEIGHT // 2 + 50))
    main_surface.blit(pause_text, pause_rect)
    main_surface.blit(resume_text, resume_rect)
    main_surface.blit(quit_text, quit_rect)
    pygame.display.update()

    waiting = True
    while waiting:
        for event in pygame.event.get():
            if event.type == QUIT:
                pygame.quit()
                sys.exit()
            elif event.type == KEYDOWN:
                if event.key == K_RETURN:
                    waiting = False
                elif event.key == K_ESCAPE:
                    pygame.quit()
                    sys.exit()

def main():
    global paddle1, paddle2, ball
    global UP1, DOWN1, UP2, DOWN2
    paddle1 = Paddle(1)
    paddle2 = Paddle(2, is_ai=True)  # Set paddle2 as AI
    ball = Ball()
    all_sprites = pygame.sprite.Group(paddle1, paddle2, ball)
    powerups = pygame.sprite.Group()

    player1_score = 0
    player2_score = 0

    UP1, DOWN1, UP2, DOWN2 = False, False, False, False

    pygame.mixer.music.play(-1, 0.5)

    show_menu()

    while True:
        for event in pygame.event.get():
            if event.type == QUIT:
                pygame.quit()
                sys.exit()
            elif event.type == KEYDOWN:
                if event.key == K_ESCAPE:
                    show_pause_menu()
                elif event.key == K_a:
                    UP1 = True
                elif event.key == K_z:
                    DOWN1 = True
            elif event.type == KEYUP:
                if event.key == K_a:
                    UP1 = False
                elif event.key == K_z:
                    DOWN1 = False

        paddle1.move(UP1, DOWN1)
        paddle2.move(False, False)  # AI paddle moves automatically
        ball.move()
        ball.change_direction()

        if pygame.sprite.collide_rect(ball, paddle1) or pygame.sprite.collide_rect(ball, paddle2):
            ball.direction = (ball.direction + 1) % 4 if ball.direction % 2 else (ball.direction - 1) % 4
            ball.increase_speed()
            sound_effect.play()

        if ball.rect.x < 0:
            player2_score += 1
            score_sound.play()
            ball.reset_ball()
        elif ball.rect.x > WINDOW_WIDTH:
            player1_score += 1
            score_sound.play()
            ball.reset_ball()

        if player1_score == 5 or player2_score == 5:
            show_game_over(1 if player1_score == 5 else 2)
            return

        if randint(1, 500) == 1 and not powerups:
            powerup = PowerUp()
            powerup.player_number = choice([1, 2])
            powerups.add(powerup)

        for powerup in powerups:
            if pygame.sprite.collide_rect(powerup, paddle1) and powerup.player_number == 1:
                powerup.activate(paddle1)
            elif pygame.sprite.collide_rect(powerup, paddle2) and powerup.player_number == 2:
                powerup.activate(paddle2)
            powerup.update()

        main_surface.fill(GRAY)
        draw_net()
        show_score(player1_score, player2_score)
        all_sprites.draw(main_surface)
        powerups.draw(main_surface)
        pygame.display.update()
        clock.tick(60)

if __name__ == "__main__":
    main()
