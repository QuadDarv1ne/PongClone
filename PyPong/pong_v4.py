import pygame
import sys
from pygame.locals import *
from random import randint

from config import *
from entities import Paddle, Ball, PowerUp
from game_state import GameState, GameStateManager
from audio import AudioManager

class PongGame:
    def __init__(self):
        pygame.init()
        self.screen = pygame.display.set_mode((WINDOW_WIDTH, WINDOW_HEIGHT))
        pygame.display.set_caption("Enhanced Pong")
        self.clock = pygame.time.Clock()
        
        # Managers
        self.state_manager = GameStateManager(self.screen)
        self.audio = AudioManager()
        
        # Game objects
        self.paddle1 = None
        self.paddle2 = None
        self.ball = None
        self.all_sprites = None
        self.powerups = None
        
        # Input state
        self.input_state = {
            "up1": False,
            "down1": False,
        }
        
        self.init_game_objects()

    def init_game_objects(self):
        self.paddle1 = Paddle(1, is_ai=False, color=GREEN)
        self.paddle2 = Paddle(2, is_ai=True, color=YELLOW)
        self.ball = Ball()
        self.all_sprites = pygame.sprite.Group(self.paddle1, self.paddle2, self.ball)
        self.powerups = pygame.sprite.Group()
        
        # Set AI difficulty
        difficulty = self.state_manager.difficulty
        self.paddle2.set_speed(DIFFICULTY_LEVELS[difficulty]["ai_speed"])

    def reset_game(self):
        self.state_manager.reset_scores()
        self.init_game_objects()

    def handle_events(self):
        for event in pygame.event.get():
            if event.type == QUIT:
                return False
            
            if event.type == KEYDOWN:
                if event.key == K_ESCAPE:
                    if self.state_manager.state == GameState.PLAYING:
                        self.state_manager.state = GameState.PAUSED
                    elif self.state_manager.state == GameState.PAUSED:
                        return False
                    else:
                        return False
                
                elif event.key == K_RETURN:
                    if self.state_manager.state == GameState.MENU:
                        self.state_manager.state = GameState.PLAYING
                        self.audio.play_music()
                    elif self.state_manager.state == GameState.PAUSED:
                        self.state_manager.state = GameState.PLAYING
                    elif self.state_manager.state == GameState.GAME_OVER:
                        self.reset_game()
                        self.state_manager.state = GameState.MENU
                
                elif event.key == K_1:
                    self.state_manager.set_difficulty("Easy")
                elif event.key == K_2:
                    self.state_manager.set_difficulty("Medium")
                elif event.key == K_3:
                    self.state_manager.set_difficulty("Hard")
                
                elif event.key == K_a:
                    self.input_state["up1"] = True
                elif event.key == K_z:
                    self.input_state["down1"] = True
            
            elif event.type == KEYUP:
                if event.key == K_a:
                    self.input_state["up1"] = False
                elif event.key == K_z:
                    self.input_state["down1"] = False
        
        return True

    def update_game(self):
        if self.state_manager.state != GameState.PLAYING:
            return
        
        # Move paddles
        self.paddle1.move(self.input_state["up1"], self.input_state["down1"])
        self.paddle2.move(False, False, self.ball.rect.centery)
        
        # Move ball
        self.ball.move()
        self.ball.bounce_wall()
        
        # Check paddle collisions
        if pygame.sprite.collide_rect(self.ball, self.paddle1):
            if self.ball.velocity_x < 0:  # Ball moving left
                self.ball.bounce_paddle(self.paddle1)
                self.audio.play_sound("beep")
        
        if pygame.sprite.collide_rect(self.ball, self.paddle2):
            if self.ball.velocity_x > 0:  # Ball moving right
                self.ball.bounce_paddle(self.paddle2)
                self.audio.play_sound("beep")
        
        # Check scoring
        if self.ball.is_out_left():
            self.state_manager.add_score(2)
            self.audio.play_sound("score")
            if self.state_manager.state == GameState.PLAYING:
                self.ball.reset_ball()
        elif self.ball.is_out_right():
            self.state_manager.add_score(1)
            self.audio.play_sound("score")
            if self.state_manager.state == GameState.PLAYING:
                self.ball.reset_ball()
        
        # Spawn powerups
        if randint(1, POWERUP_SPAWN_CHANCE) == 1 and len(self.powerups) == 0:
            powerup = PowerUp()
            self.powerups.add(powerup)
        
        # Check powerup collisions
        for powerup in self.powerups:
            if not powerup.active:
                if pygame.sprite.collide_rect(powerup, self.paddle1):
                    powerup.activate(self.paddle1)
                    self.audio.play_sound("powerup")
                elif pygame.sprite.collide_rect(powerup, self.paddle2):
                    powerup.activate(self.paddle2)
                    self.audio.play_sound("powerup")
        
        # Update powerups
        self.powerups.update()

    def draw(self):
        self.screen.fill(GRAY)
        
        if self.state_manager.state == GameState.MENU:
            self.state_manager.draw_menu()
        
        elif self.state_manager.state == GameState.PLAYING:
            self.state_manager.draw_net()
            self.state_manager.draw_score()
            self.all_sprites.draw(self.screen)
            self.powerups.draw(self.screen)
        
        elif self.state_manager.state == GameState.PAUSED:
            self.state_manager.draw_net()
            self.state_manager.draw_score()
            self.all_sprites.draw(self.screen)
            self.powerups.draw(self.screen)
            self.state_manager.draw_pause()
        
        elif self.state_manager.state == GameState.GAME_OVER:
            self.state_manager.draw_game_over()
        
        pygame.display.flip()

    def run(self):
        running = True
        while running:
            running = self.handle_events()
            self.update_game()
            self.draw()
            self.clock.tick(FPS)
        
        pygame.quit()
        sys.exit()

if __name__ == "__main__":
    game = PongGame()
    game.run()
