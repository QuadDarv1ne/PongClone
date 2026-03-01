"""
Enhanced Pong with Campaign, Challenges, Mini-games and Modifiers
This is a demonstration of how to integrate the new content systems
"""
import pygame
import sys
from PyPong.core.config import *
from PyPong.core.game_state import GameState, GameStateManager
from PyPong.core.entities import Paddle, Ball, PowerUp
from PyPong.systems.audio import AudioManager
from PyPong.systems.stats import StatsManager
from PyPong.systems.settings import Settings
from PyPong.ui.themes import get_theme
from PyPong.ui.ui import PowerUpIndicator, FPSCounter, SettingsMenu

# New imports
from PyPong.content.campaign import CampaignManager
from PyPong.content.challenges import ChallengeManager
from PyPong.content.minigames import MiniGameManager
from PyPong.content.modifiers import (ModifierManager, GravityModifier, WindModifier, 
                       InvisibleBallModifier, SpeedModifier)
from PyPong.ui.content_ui import CampaignUI, ChallengesUI, MiniGameUI


class EnhancedPongGame:
    def __init__(self):
        pygame.init()
        self.screen = pygame.display.set_mode((WINDOW_WIDTH, WINDOW_HEIGHT))
        pygame.display.set_caption("Enhanced Pong - Campaign Edition")
        self.clock = pygame.time.Clock()
        
        # Core systems
        self.state_manager = GameStateManager(self.screen)
        self.audio = AudioManager()
        self.stats = StatsManager()
        self.settings = Settings()
        
        # New content systems
        self.campaign = CampaignManager()
        self.challenges = ChallengeManager()
        self.minigames = MiniGameManager()
        self.modifiers = ModifierManager()
        
        # UI systems
        self.campaign_ui = CampaignUI(self.screen, self.campaign)
        self.challenges_ui = ChallengesUI(self.screen, self.challenges)
        self.minigame_ui = MiniGameUI(self.screen, self.minigames)
        self.powerup_indicator = PowerUpIndicator()
        self.fps_counter = FPSCounter()
        self.settings_menu = SettingsMenu(self.screen, self.settings)
        
        # Game objects
        self.paddle1 = None
        self.paddle2 = None
        self.ball = None
        self.balls = []
        self.powerups = pygame.sprite.Group()
        
        # Campaign state
        self.current_level = None
        self.level_start_time = None
        self.level_objectives_completed = []
        
        self.apply_settings()
        self.init_game_objects()

    def apply_settings(self):
        """Apply game settings"""
        music_vol = self.settings.get("music_volume", 0.5)
        pygame.mixer.music.set_volume(music_vol)
        
        theme_name = self.settings.get("theme", "classic")
        self.theme = get_theme(theme_name)

    def init_game_objects(self):
        """Initialize game objects"""
        self.paddle1 = Paddle(1, is_ai=False, color=self.theme.paddle1_color)
        self.paddle2 = Paddle(2, is_ai=True, color=self.theme.paddle2_color)
        self.ball = Ball()
        self.balls = [self.ball]
        self.powerups.empty()

    def apply_level_modifiers(self, level):
        """Apply modifiers from campaign level"""
        self.modifiers.clear_modifiers()
        
        mods = level.modifiers
        
        if 'gravity' in mods:
            self.modifiers.add_modifier(GravityModifier(mods['gravity']))
        
        if 'wind' in mods:
            self.modifiers.add_modifier(WindModifier(mods['wind']))
        
        if 'invisible_ball' in mods and mods['invisible_ball']:
            interval = mods.get('invisible_interval', 3000)
            self.modifiers.add_modifier(InvisibleBallModifier(interval))
        
        if 'ball_speed' in mods:
            self.ball.speed = mods['ball_speed']
        
        if 'ai_speed' in mods:
            self.paddle2.speed = mods['ai_speed']

    def handle_menu_input(self, event):
        """Handle menu input"""
        if event.type == pygame.KEYDOWN:
            if event.key == pygame.K_RETURN:
                self.state_manager.state = GameState.MODE_SELECT
            elif event.key == pygame.K_c:
                self.state_manager.state = GameState.CAMPAIGN_SELECT
            elif event.key == pygame.K_h:
                self.state_manager.state = GameState.CHALLENGES
                self.challenges.refresh_challenges()
            elif event.key == pygame.K_m:
                self.state_manager.state = GameState.MINIGAME_SELECT
            elif event.key == pygame.K_s:
                self.state_manager.state = GameState.STATS
            elif event.key == pygame.K_o:
                self.state_manager.state = GameState.SETTINGS

    def handle_campaign_input(self, event):
        """Handle campaign mode input"""
        result = self.campaign_ui.handle_input(event)
        
        if result == "back":
            self.state_manager.state = GameState.MENU
        elif result:  # Selected a level
            self.current_level = result
            self.level_start_time = pygame.time.get_ticks()
            self.level_objectives_completed = []
            self.apply_level_modifiers(result)
            self.init_game_objects()
            self.state_manager.reset_scores()
            self.state_manager.state = GameState.CAMPAIGN_PLAYING

    def handle_minigame_input(self, event):
        """Handle mini-game input"""
        result = self.minigame_ui.handle_input(event)
        
        if result == "back":
            self.state_manager.state = GameState.MENU
        elif result:  # Selected a mini-game
            self.minigames.start_minigame(result)
            self.init_game_objects()
            self.state_manager.state = GameState.MINIGAME_PLAYING

    def update_campaign(self):
        """Update campaign mode"""
        # Apply modifiers
        for ball in self.balls:
            self.modifiers.apply_to_ball(ball)
        
        self.modifiers.apply_to_paddle(self.paddle1)
        self.modifiers.apply_to_paddle(self.paddle2)
        self.modifiers.update()
        
        # Check level completion
        if self.state_manager.winner:
            elapsed_time = (pygame.time.get_ticks() - self.level_start_time) / 1000
            
            # Calculate stars (simple example)
            stars = 1
            if elapsed_time < 120:  # Under 2 minutes
                stars = 2
            if elapsed_time < 60:  # Under 1 minute
                stars = 3
            
            self.campaign.complete_level(self.current_level.id, stars, elapsed_time)
            self.state_manager.state = GameState.CAMPAIGN_COMPLETE

    def update_minigame(self):
        """Update mini-game mode"""
        current = self.minigames.get_current_minigame()
        
        if current:
            # Update based on mini-game type
            if current.name == "Target Practice":
                current.update(self.ball)
            elif current.name == "Breakout":
                current.update(self.ball)
            elif current.name == "Survival":
                current.update(self.ball)
            elif current.name == "Keep Up":
                current.update(self.ball, self.paddle1)
                if current.check_fail(self.ball):
                    self.state_manager.state = GameState.MINIGAME_COMPLETE
            elif current.name == "Precision":
                if self.ball.rect.colliderect(self.paddle1.rect):
                    quality = current.check_hit_quality(self.ball, self.paddle1)
            
            # Check completion
            if current.is_complete():
                self.state_manager.state = GameState.MINIGAME_COMPLETE

    def draw(self):
        """Main draw method"""
        self.screen.fill(self.theme.bg_color)
        
        if self.state_manager.state == GameState.MENU:
            self.state_manager.draw_menu()
        
        elif self.state_manager.state == GameState.CAMPAIGN_SELECT:
            self.campaign_ui.draw_level_select()
        
        elif self.state_manager.state == GameState.CAMPAIGN_PLAYING:
            # Draw game
            self.state_manager.draw_net()
            self.screen.blit(self.paddle1.image, self.paddle1.rect)
            self.screen.blit(self.paddle2.image, self.paddle2.rect)
            
            for ball in self.balls:
                self.screen.blit(ball.image, ball.rect)
            
            self.powerups.draw(self.screen)
            self.state_manager.draw_score()
            
            # Draw active modifiers
            y = 100
            font = pygame.font.SysFont(FONT_NAME, 20)
            for mod_name in self.modifiers.get_active_modifiers():
                text = font.render(f"• {mod_name}", True, YELLOW)
                self.screen.blit(text, (10, y))
                y += 25
        
        elif self.state_manager.state == GameState.CAMPAIGN_COMPLETE:
            if self.current_level:
                elapsed = (pygame.time.get_ticks() - self.level_start_time) / 1000
                stars = min(3, max(1, int(180 / elapsed)))  # Simple calculation
                self.campaign_ui.draw_level_complete(self.current_level, stars, elapsed)
        
        elif self.state_manager.state == GameState.CHALLENGES:
            self.challenges_ui.draw()
        
        elif self.state_manager.state == GameState.MINIGAME_SELECT:
            self.minigame_ui.draw_select()
        
        elif self.state_manager.state == GameState.MINIGAME_PLAYING:
            # Draw game
            self.screen.blit(self.paddle1.image, self.paddle1.rect)
            
            for ball in self.balls:
                self.screen.blit(ball.image, ball.rect)
            
            # Draw mini-game specific elements
            current = self.minigames.get_current_minigame()
            if current:
                current.draw(self.screen)
                self.minigame_ui.draw_playing(current)
        
        elif self.state_manager.state == GameState.MINIGAME_COMPLETE:
            current = self.minigames.get_current_minigame()
            if current:
                self.minigame_ui.draw_complete(current)
        
        elif self.state_manager.state == GameState.STATS:
            self.state_manager.draw_stats(self.stats)
        
        elif self.state_manager.state == GameState.SETTINGS:
            self.settings_menu.draw()
        
        # FPS counter
        if self.settings.get("show_fps", False):
            self.fps_counter.draw(self.screen, self.clock)
        
        pygame.display.flip()

    def run(self):
        """Main game loop"""
        running = True
        
        while running:
            for event in pygame.event.get():
                if event.type == pygame.QUIT:
                    running = False
                
                # State-specific input handling
                if self.state_manager.state == GameState.MENU:
                    self.handle_menu_input(event)
                
                elif self.state_manager.state == GameState.CAMPAIGN_SELECT:
                    self.handle_campaign_input(event)
                
                elif self.state_manager.state == GameState.CAMPAIGN_PLAYING:
                    if event.type == pygame.KEYDOWN:
                        if event.key == pygame.K_ESCAPE:
                            self.state_manager.state = GameState.MENU
                
                elif self.state_manager.state == GameState.CAMPAIGN_COMPLETE:
                    if event.type == pygame.KEYDOWN and event.key == pygame.K_RETURN:
                        self.state_manager.state = GameState.CAMPAIGN_SELECT
                
                elif self.state_manager.state == GameState.CHALLENGES:
                    if event.type == pygame.KEYDOWN and event.key == pygame.K_ESCAPE:
                        self.state_manager.state = GameState.MENU
                
                elif self.state_manager.state == GameState.MINIGAME_SELECT:
                    self.handle_minigame_input(event)
                
                elif self.state_manager.state == GameState.MINIGAME_PLAYING:
                    if event.type == pygame.KEYDOWN and event.key == pygame.K_ESCAPE:
                        self.minigames.stop_minigame()
                        self.state_manager.state = GameState.MINIGAME_SELECT
                
                elif self.state_manager.state == GameState.MINIGAME_COMPLETE:
                    if event.type == pygame.KEYDOWN and event.key == pygame.K_RETURN:
                        self.minigames.stop_minigame()
                        self.state_manager.state = GameState.MINIGAME_SELECT
                
                elif self.state_manager.state == GameState.STATS:
                    if event.type == pygame.KEYDOWN and event.key == pygame.K_ESCAPE:
                        self.state_manager.state = GameState.MENU
                
                elif self.state_manager.state == GameState.SETTINGS:
                    result = self.settings_menu.handle_input(event)
                    if result == "back":
                        self.apply_settings()
                        self.state_manager.state = GameState.MENU
            
            # Update game state
            if self.state_manager.state == GameState.CAMPAIGN_PLAYING:
                self.update_campaign()
            
            elif self.state_manager.state == GameState.MINIGAME_PLAYING:
                self.update_minigame()
            
            self.draw()
            self.clock.tick(FPS)
        
        pygame.quit()
        sys.exit()


if __name__ == "__main__":
    game = EnhancedPongGame()
    game.run()
