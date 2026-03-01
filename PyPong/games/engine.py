"""
Unified game engine that manages all game modes
"""
import pygame
from pygame.event import Event
from typing import Optional, Dict, Any, Type

from PyPong.core.config import *
from PyPong.games.base import GameMode, GameModeType
from PyPong.games.classic import ClassicMode
from PyPong.games.arcade import ArcadeMode
from PyPong.games.multiplayer import MultiplayerMode


class GameEngine:
    """
    Main game engine that handles game modes and main loop
    """
    
    def __init__(self) -> None:
        pygame.init()
        
        # Setup display
        self.screen: pygame.Surface = pygame.display.set_mode((WINDOW_WIDTH, WINDOW_HEIGHT))
        pygame.display.set_caption("PyPong")
        self.clock: pygame.time.Clock = pygame.time.Clock()
        
        # Settings
        self.settings: Dict[str, Any] = {
            'winning_score': WINNING_SCORE,
            'ai_enabled': True,
            'ai_difficulty': 'Medium',
            'show_fps': False,
            # Multiplayer settings
            'connection_type': 'local',  # local, host, client
            'host': 'localhost',
            'port': 9999,
        }
        
        # Game mode management
        self.current_mode: Optional[GameMode] = None
        self.available_modes: Dict[GameModeType, Type[GameMode]] = {
            GameModeType.CLASSIC: ClassicMode,
            GameModeType.ARCADE: ArcadeMode,
            GameModeType.MULTIPLAYER: MultiplayerMode,
        }
        
        # Game state
        self.running: bool = True
        self.current_mode_type: GameModeType = GameModeType.CLASSIC
    
    def set_mode(self, mode_type: GameModeType) -> None:
        """Switch to a different game mode"""
        if mode_type in self.available_modes:
            self.current_mode_type = mode_type
            mode_class = self.available_modes[mode_type]
            self.current_mode = mode_class(self.screen, self.settings)
    
    def set_multiplayer(self, connection_type: str, host: str = 'localhost', port: int = 9999) -> None:
        """Configure multiplayer and switch to multiplayer mode"""
        self.settings['connection_type'] = connection_type
        self.settings['host'] = host
        self.settings['port'] = port
        self.set_mode(GameModeType.MULTIPLAYER)
    
    def update_settings(self, key: str, value: Any) -> None:
        """Update a setting and apply it"""
        self.settings[key] = value
        
        # If game is running, update mode settings too
        if self.current_mode:
            self.current_mode.settings[key] = value
    
    def handle_events(self) -> bool:
        """Handle all events. Returns False to quit."""
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                return False
            
            if event.type == pygame.KEYDOWN:
                # Mode selection
                if event.key == pygame.K_1:
                    self.set_mode(GameModeType.CLASSIC)
                    return True
                elif event.key == pygame.K_2:
                    self.set_mode(GameModeType.ARCADE)
                    return True
                elif event.key == pygame.K_3:
                    # Local PVP
                    self.settings['connection_type'] = 'local'
                    self.set_mode(GameModeType.MULTIPLAYER)
                    return True
                elif event.key == pygame.K_4:
                    # Host network game
                    self.settings['connection_type'] = 'host'
                    self.set_mode(GameModeType.MULTIPLAYER)
                    return True
                elif event.key == pygame.K_5:
                    # Join network game (uses default host)
                    self.settings['connection_type'] = 'client'
                    self.set_mode(GameModeType.MULTIPLAYER)
                    return True
                
                # Start game with Enter
                elif event.key == pygame.K_RETURN:
                    if self.current_mode and not self.current_mode.is_active:
                        self.current_mode.start()
                
                # Toggle FPS
                elif event.key == pygame.K_F3:
                    self.update_settings('show_fps', not self.settings['show_fps'])
                
                # Difficulty selection (when not playing)
                elif event.key in (pygame.K_3, pygame.K_4, pygame.K_5):
                    if self.current_mode and not self.current_mode.is_active:
                        if event.key == pygame.K_3:
                            self.update_settings('ai_difficulty', 'Easy')
                        elif event.key == pygame.K_4:
                            self.update_settings('ai_difficulty', 'Medium')
                        elif event.key == pygame.K_5:
                            self.update_settings('ai_difficulty', 'Hard')
            
            # Pass events to current mode
            if self.current_mode:
                if not self.current_mode.handle_input(event):
                    return False
        
        return True
    
    def update(self) -> None:
        """Update current game mode"""
        if self.current_mode:
            dt = self.clock.tick(FPS) / 1000.0  # Delta time in seconds
            self.current_mode.update(dt)
    
    def draw(self) -> None:
        """Draw current game mode"""
        if self.current_mode:
            self.current_mode.draw()
        
        # FPS counter
        if self.settings.get('show_fps', False):
            font = pygame.font.SysFont(FONT_NAME, 20)
            fps = int(self.clock.get_fps())
            fps_text = font.render(f"FPS: {fps}", True, WHITE)
            self.screen.blit(fps_text, (10, 10))
        
        # Mode indicator
        font = pygame.font.SysFont(FONT_NAME, 16)
        mode_name = self.current_mode_type.value.upper() if self.current_mode_type else "NONE"
        mode_text = font.render(f"Mode: {mode_name}", True, WHITE)
        self.screen.blit(mode_text, (10, WINDOW_HEIGHT - 25))
        
        pygame.display.flip()
    
    def run(self) -> None:
        """Main game loop"""
        # Initialize with classic mode
        self.set_mode(GameModeType.CLASSIC)
        
        while self.running:
            self.running = self.handle_events()
            self.update()
            self.draw()
        
        pygame.quit()


def main() -> None:
    """Entry point"""
    engine = GameEngine()
    engine.run()


if __name__ == "__main__":
    main()
