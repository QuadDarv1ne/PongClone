"""
Base game mode class
"""
from enum import Enum
from abc import ABC, abstractmethod
import pygame
from pygame.event import Event
from typing import Optional, Dict, Any, List

from PyPong.core.entities import Paddle, Ball


class GameModeType(Enum):
    """Types of game modes available"""
    CLASSIC = "classic"
    ARCADE = "arcade"
    CAMPAIGN = "campaign"
    TOURNAMENT = "tournament"
    MINIGAME = "minigame"
    MULTIPLAYER = "multiplayer"


class GameMode(ABC):
    """
    Abstract base class for all game modes.
    Each mode implements specific gameplay rules.
    """
    
    def __init__(self, screen: pygame.Surface, settings: Optional[Dict[str, Any]] = None) -> None:
        self.screen: pygame.Surface = screen
        self.settings: Dict[str, Any] = settings or {}
        self.is_active: bool = False
        self.is_paused: bool = False
        self.game_over: bool = False
        self.winner: Optional[int] = None
        
        # Common game objects (to be set by subclasses)
        self.paddle1: Optional[Paddle] = None
        self.paddle2: Optional[Paddle] = None
        self.ball: Optional[Ball] = None
        self.all_sprites: Optional[pygame.sprite.Group] = None
        
        # Score
        self.player1_score: int = 0
        self.player2_score: int = 0
        self.winning_score: int = self.settings.get('winning_score', 5)
        
        # Input state
        self.input_state: Dict[str, bool] = {
            "up1": False,
            "down1": False,
            "up2": False,
            "down2": False,
        }
    
    @property
    @abstractmethod
    def mode_type(self) -> GameModeType:
        """Return the type of this game mode"""
        raise NotImplementedError

    @abstractmethod
    def init_game_objects(self) -> None:
        """Initialize game objects for this mode"""
        raise NotImplementedError

    @abstractmethod
    def handle_input(self, event: Event) -> bool:
        """
        Handle input events.
        Returns False if game should quit, True otherwise.
        """
        raise NotImplementedError

    @abstractmethod
    def update(self, dt: float) -> None:
        """Update game logic. dt is delta time in seconds."""
        raise NotImplementedError

    @abstractmethod
    def draw(self) -> None:
        """Draw the game state"""
        raise NotImplementedError
    
    def reset(self) -> None:
        """Reset the game mode to initial state"""
        self.player1_score = 0
        self.player2_score = 0
        self.game_over = False
        self.winner = None
        self.is_paused = False
        self.init_game_objects()
    
    def add_score(self, player: int) -> None:
        """Add score for player 1 or 2"""
        if player == 1:
            self.player1_score += 1
        elif player == 2:
            self.player2_score += 1
        
        # Check win condition
        if self.player1_score >= self.winning_score:
            self.game_over = True
            self.winner = 1
        elif self.player2_score >= self.winning_score:
            self.game_over = True
            self.winner = 2
    
    def pause(self) -> None:
        """Pause the game"""
        self.is_paused = True
    
    def resume(self) -> None:
        """Resume the game"""
        self.is_paused = False
    
    def get_score_display(self) -> str:
        """Get score as string for display"""
        return f"{self.player1_score}   {self.player2_score}"
    
    def get_winner_name(self) -> str:
        """Get winner name for display"""
        if self.winner == 1:
            return "Player 1 Wins"
        elif self.winner == 2:
            return "Player 2 Wins"
        return ""
