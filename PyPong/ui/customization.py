"""
Customization system for paddles, balls, and visual elements
"""
import pygame
import json
from pathlib import Path
from typing import Dict, List, Optional, Tuple
from dataclasses import dataclass, asdict
from PyPong.core.constants import Colors
from PyPong.core.logger import logger, log_exception


@dataclass
class PaddleSkin:
    """Paddle skin configuration"""
    id: str
    name: str
    color: Tuple[int, int, int]
    pattern: str = "solid"  # solid, gradient, striped, dotted
    unlocked: bool = True
    unlock_requirement: Optional[str] = None


@dataclass
class BallSkin:
    """Ball skin configuration"""
    id: str
    name: str
    color: Tuple[int, int, int]
    trail_color: Optional[Tuple[int, int, int]] = None
    glow: bool = False
    unlocked: bool = True
    unlock_requirement: Optional[str] = None


@dataclass
class CourtTheme:
    """Court visual theme"""
    id: str
    name: str
    background_color: Tuple[int, int, int]
    net_color: Tuple[int, int, int]
    line_color: Tuple[int, int, int]
    particle_color: Tuple[int, int, int]
    unlocked: bool = True


class CustomizationManager:
    """Manages visual customization"""
    
    def __init__(self, filename: str = "PyPong/data/customization.json"):
        self.filename = Path(filename)
        
        # Current selections
        self.player1_paddle_skin = "default"
        self.player2_paddle_skin = "default"
        self.ball_skin = "default"
        self.court_theme = "classic"
        
        # Available options
        self.paddle_skins: Dict[str, PaddleSkin] = {}
        self.ball_skins: Dict[str, BallSkin] = {}
        self.court_themes: Dict[str, CourtTheme] = {}
        
        self._create_default_options()
        self.load_customization()
        
        logger.info("Customization manager initialized")
    
    def _create_default_options(self) -> None:
        """Create default customization options"""
        # Paddle skins
        self.paddle_skins = {
            "default": PaddleSkin("default", "Default", Colors.WHITE.to_tuple()),
            "red": PaddleSkin("red", "Red", Colors.RED.to_tuple()),
            "green": PaddleSkin("green", "Green", Colors.GREEN.to_tuple()),
            "blue": PaddleSkin("blue", "Blue", (0, 100, 255)),
            "yellow": PaddleSkin("yellow", "Yellow", Colors.YELLOW.to_tuple()),
            "purple": PaddleSkin("purple", "Purple", Colors.PURPLE.to_tuple()),
            "cyan": PaddleSkin("cyan", "Cyan", Colors.CYAN.to_tuple()),
            "orange": PaddleSkin("orange", "Orange", Colors.ORANGE.to_tuple()),
            
            # Special skins (unlockable)
            "rainbow": PaddleSkin(
                "rainbow", "Rainbow", Colors.WHITE.to_tuple(),
                pattern="gradient", unlocked=False,
                unlock_requirement="Win 50 games"
            ),
            "neon": PaddleSkin(
                "neon", "Neon", (0, 255, 255),
                pattern="solid", unlocked=False,
                unlock_requirement="Complete campaign"
            ),
            "gold": PaddleSkin(
                "gold", "Gold", (255, 215, 0),
                pattern="solid", unlocked=False,
                unlock_requirement="Get all achievements"
            ),
        }
        
        # Ball skins
        self.ball_skins = {
            "default": BallSkin("default", "Default", Colors.WHITE.to_tuple()),
            "red": BallSkin("red", "Red Ball", Colors.RED.to_tuple()),
            "green": BallSkin("green", "Green Ball", Colors.GREEN.to_tuple()),
            "blue": BallSkin("blue", "Blue Ball", (0, 150, 255)),
            
            # Special skins
            "fire": BallSkin(
                "fire", "Fire Ball", (255, 100, 0),
                trail_color=(255, 50, 0), unlocked=False,
                unlock_requirement="Score 100 goals"
            ),
            "ice": BallSkin(
                "ice", "Ice Ball", (150, 200, 255),
                trail_color=(100, 150, 255), unlocked=False,
                unlock_requirement="Win 10 perfect games"
            ),
            "plasma": BallSkin(
                "plasma", "Plasma Ball", (255, 0, 255),
                trail_color=(200, 0, 200), glow=True, unlocked=False,
                unlock_requirement="Get 30 stars in campaign"
            ),
        }
        
        # Court themes
        self.court_themes = {
            "classic": CourtTheme(
                "classic", "Classic",
                Colors.GRAY.to_tuple(),
                Colors.WHITE.to_tuple(),
                Colors.WHITE.to_tuple(),
                Colors.WHITE.to_tuple()
            ),
            "dark": CourtTheme(
                "dark", "Dark Mode",
                (20, 20, 20),
                (100, 100, 100),
                (80, 80, 80),
                (150, 150, 150)
            ),
            "neon": CourtTheme(
                "neon", "Neon",
                (10, 10, 30),
                (0, 255, 255),
                (255, 0, 255),
                (0, 255, 255),
                unlocked=False
            ),
            "retro": CourtTheme(
                "retro", "Retro",
                (0, 50, 0),
                (0, 255, 0),
                (0, 200, 0),
                (0, 255, 0),
                unlocked=False
            ),
        }
    
    @log_exception
    def load_customization(self) -> None:
        """Load customization settings"""
        if not self.filename.exists():
            logger.debug("No customization file found")
            return
        
        try:
            with open(self.filename, 'r', encoding='utf-8') as f:
                data = json.load(f)
            
            self.player1_paddle_skin = data.get('player1_paddle', 'default')
            self.player2_paddle_skin = data.get('player2_paddle', 'default')
            self.ball_skin = data.get('ball', 'default')
            self.court_theme = data.get('court', 'classic')
            
            # Load unlocked items
            unlocked = data.get('unlocked', {})
            for skin_id in unlocked.get('paddles', []):
                if skin_id in self.paddle_skins:
                    self.paddle_skins[skin_id].unlocked = True
            
            for skin_id in unlocked.get('balls', []):
                if skin_id in self.ball_skins:
                    self.ball_skins[skin_id].unlocked = True
            
            for theme_id in unlocked.get('courts', []):
                if theme_id in self.court_themes:
                    self.court_themes[theme_id].unlocked = True
            
            logger.info("Customization loaded")
        
        except Exception as e:
            logger.error(f"Failed to load customization: {e}", exc_info=True)
    
    @log_exception
    def save_customization(self) -> None:
        """Save customization settings"""
        try:
            data = {
                'player1_paddle': self.player1_paddle_skin,
                'player2_paddle': self.player2_paddle_skin,
                'ball': self.ball_skin,
                'court': self.court_theme,
                'unlocked': {
                    'paddles': [
                        skin_id for skin_id, skin in self.paddle_skins.items()
                        if skin.unlocked
                    ],
                    'balls': [
                        skin_id for skin_id, skin in self.ball_skins.items()
                        if skin.unlocked
                    ],
                    'courts': [
                        theme_id for theme_id, theme in self.court_themes.items()
                        if theme.unlocked
                    ]
                }
            }
            
            with open(self.filename, 'w', encoding='utf-8') as f:
                json.dump(data, f, indent=2)
            
            logger.debug("Customization saved")
        
        except Exception as e:
            logger.error(f"Failed to save customization: {e}", exc_info=True)
    
    def set_paddle_skin(self, player: int, skin_id: str) -> bool:
        """Set paddle skin for player"""
        if skin_id not in self.paddle_skins:
            logger.warning(f"Unknown paddle skin: {skin_id}")
            return False
        
        skin = self.paddle_skins[skin_id]
        if not skin.unlocked:
            logger.warning(f"Paddle skin locked: {skin_id}")
            return False
        
        if player == 1:
            self.player1_paddle_skin = skin_id
        else:
            self.player2_paddle_skin = skin_id
        
        self.save_customization()
        logger.info(f"Player {player} paddle skin set to: {skin.name}")
        return True
    
    def set_ball_skin(self, skin_id: str) -> bool:
        """Set ball skin"""
        if skin_id not in self.ball_skins:
            logger.warning(f"Unknown ball skin: {skin_id}")
            return False
        
        skin = self.ball_skins[skin_id]
        if not skin.unlocked:
            logger.warning(f"Ball skin locked: {skin_id}")
            return False
        
        self.ball_skin = skin_id
        self.save_customization()
        logger.info(f"Ball skin set to: {skin.name}")
        return True
    
    def set_court_theme(self, theme_id: str) -> bool:
        """Set court theme"""
        if theme_id not in self.court_themes:
            logger.warning(f"Unknown court theme: {theme_id}")
            return False
        
        theme = self.court_themes[theme_id]
        if not theme.unlocked:
            logger.warning(f"Court theme locked: {theme_id}")
            return False
        
        self.court_theme = theme_id
        self.save_customization()
        logger.info(f"Court theme set to: {theme.name}")
        return True
    
    def unlock_item(self, category: str, item_id: str) -> bool:
        """Unlock customization item"""
        if category == "paddle":
            if item_id in self.paddle_skins:
                self.paddle_skins[item_id].unlocked = True
                self.save_customization()
                logger.info(f"Unlocked paddle skin: {item_id}")
                return True
        
        elif category == "ball":
            if item_id in self.ball_skins:
                self.ball_skins[item_id].unlocked = True
                self.save_customization()
                logger.info(f"Unlocked ball skin: {item_id}")
                return True
        
        elif category == "court":
            if item_id in self.court_themes:
                self.court_themes[item_id].unlocked = True
                self.save_customization()
                logger.info(f"Unlocked court theme: {item_id}")
                return True
        
        return False
    
    def get_paddle_skin(self, player: int) -> PaddleSkin:
        """Get current paddle skin for player"""
        skin_id = self.player1_paddle_skin if player == 1 else self.player2_paddle_skin
        return self.paddle_skins.get(skin_id, self.paddle_skins["default"])
    
    def get_ball_skin(self) -> BallSkin:
        """Get current ball skin"""
        return self.ball_skins.get(self.ball_skin, self.ball_skins["default"])
    
    def get_court_theme(self) -> CourtTheme:
        """Get current court theme"""
        return self.court_themes.get(self.court_theme, self.court_themes["classic"])
    
    def get_unlocked_paddle_skins(self) -> List[PaddleSkin]:
        """Get all unlocked paddle skins"""
        return [skin for skin in self.paddle_skins.values() if skin.unlocked]
    
    def get_unlocked_ball_skins(self) -> List[BallSkin]:
        """Get all unlocked ball skins"""
        return [skin for skin in self.ball_skins.values() if skin.unlocked]
    
    def get_unlocked_court_themes(self) -> List[CourtTheme]:
        """Get all unlocked court themes"""
        return [theme for theme in self.court_themes.values() if theme.unlocked]
