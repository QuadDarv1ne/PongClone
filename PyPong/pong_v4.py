import pygame
import sys
from pygame.locals import *
from random import randint

from config import *
from entities import Paddle, Ball, PowerUp
from game_state import GameState, GameStateManager
from audio import AudioManager
from effects import Particle, Trail, ScreenShake, GoalAnimation
from stats import StatsManager

class PongGame:
    def __init__(self):
        pygame.init()
        self.screen = pygame.display.set_mode((WINDOW_WIDTH, WINDOW_HEIGHT))
        self.game_surface = pygame.Surface((WINDOW_WIDTH, WINDOW_HEIGHT))
        pygame.display.set_caption("Enhanced Pong")
        self.clock = pygame.time.Clock()
        
        # Managers
        self.state_manager = GameStateManager(self.game_surface)
        self.audio = AudioManager()
        self.stats = StatsManager()
        
        # Effects
        self.particles = pygame.sprite.Group()
        self.trails = pygame.sprite.Group()
        self.shake = ScreenShake()
        self.goal_anim = GoalAnimation()
        
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
                    elif self.state_manager.state == GameState.STATS:
                        self.state_manager.state = GameState.MENU
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
                
                elif event.key == K_s and self.state_manager.state == GameState.MENU:
                    self.state_manager.state = GameState.STATS
                
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
        
        # Move ball and create trail
        self.ball.move()
        if randint(1, 2) == 1:
            trail = Trail(self.ball.rect.centerx, self.ball.rect.centery)
            self.trails.add(trail)
        
        self.ball.bounce_wall()
        
        # Check paddle collisions
        if pygame.sprite.collide_rect(self.ball, self.paddle1):
            if self.ball.velocity_x < 0:
                self.ball.bounce_paddle(self.paddle1)
                self.audio.play_sound("beep")
                self.create_particles(self.ball.rect.centerx, self.ball.rect.centery, GREEN)
                self.shake.start(5, 5)
        
        if pygame.sprite.collide_rect(self.ball, self.paddle2):
            if self.ball.velocity_x > 0:
                self.ball.bounce_paddle(self.paddle2)
                self.audio.play_sound("beep")
                self.create_particles(self.ball.rect.centerx, self.ball.rect.centery, YELLOW)
                self.shake.start(5, 5)
        
        # Check scoring
        if self.ball.is_out_left():
            self.state_manager.add_score(2)
            self.audio.play_sound("score")
            self.goal_anim.start(2)
            self.shake.start(15, 15)
            if self.state_manager.state == GameState.PLAYING:
                self.ball.reset_ball()
            elif self.state_manager.state == GameState.GAME_OVER:
                self.stats.record_game(
                    self.state_manager.winner,
                    self.state_manager.player1_score,
                    self.state_manager.player2_score
                )
        elif self.ball.is_out_right():
            self.state_manager.add_score(1)
            self.audio.play_sound("score")
            self.goal_anim.start(1)
            self.shake.start(15, 15)
            if self.state_manager.state == GameState.PLAYING:
                self.ball.reset_ball()
            elif self.state_manager.state == GameState.GAME_OVER:
                self.stats.record_game(
                    self.state_manager.winner,
                    self.state_manager.player1_score,
                    self.state_manager.player2_score
                )
        
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
                    self.create_particles(powerup.rect.centerx, powerup.rect.centery, LIGHT_BLUE)
                elif pygame.sprite.collide_rect(powerup, self.paddle2):
                    powerup.activate(self.paddle2)
                    self.audio.play_sound("powerup")
                    self.create_particles(powerup.rect.centerx, powerup.rect.centery, LIGHT_BLUE)
        
        # Update effects
        self.powerups.update()
        self.particles.update()
        self.trails.update()
        self.shake.update()
        self.goal_anim.update()

    def create_particles(self, x, y, color):
        for _ in range(10):
            particle = Particle(x, y, color)
            self.particles.add(particle)

    def draw(self):
        self.game_surface.fill(GRAY)
        
        if self.state_manager.state == GameState.MENU:
            self.state_manager.draw_menu()
        
        elif self.state_manager.state == GameState.STATS:
            self.state_manager.draw_stats(self.stats)
        
        elif self.state_manager.state == GameState.PLAYING:
            self.state_manager.draw_net()
            self.state_manager.draw_score()
            self.trails.draw(self.game_surface)
            self.all_sprites.draw(self.game_surface)
            self.powerups.draw(self.game_surface)
            self.particles.draw(self.game_surface)
            self.goal_anim.draw(self.game_surface)
        
        elif self.state_manager.state == GameState.PAUSED:
            self.state_manager.draw_net()
            self.state_manager.draw_score()
            self.trails.draw(self.game_surface)
            self.all_sprites.draw(self.game_surface)
            self.powerups.draw(self.game_surface)
            self.particles.draw(self.game_surface)
            self.state_manager.draw_pause()
        
        elif self.state_manager.state == GameState.GAME_OVER:
            self.state_manager.draw_game_over()
        
        # Apply screen shake
        self.shake.apply(self.game_surface, self.screen)
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
