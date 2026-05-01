"""
Accessibility features for PyPong
"""
import pygame
from typing import Optional, Dict, Tuple, List
from enum import Enum, auto
from PyPong.core.logger import logger


class ColorBlindMode(Enum):
    """Color blindness types"""
    NORMAL = auto()
    PROTANOPIA = auto()  # Red-blind
    DEUTERANOPIA = auto()  # Green-blind
    TRITANOPIA = auto()  # Blue-blind
    MONOCHROMACY = auto()  # Total color blindness


class AccessibilityManager:
    """
    Manages accessibility features:
    - Color blind modes
    - High contrast mode
    - Screen reader support
    - Larger UI elements
    - Audio cues
    """
    
    def __init__(self):
        self.color_blind_mode = ColorBlindMode.NORMAL
        self.high_contrast = False
        self.large_ui = False
        self.audio_cues = True
        self.screen_reader = False
        self.reduce_motion = False
        
        # Color palettes for different modes
        self._color_palettes = self._init_color_palettes()
    
    def _init_color_palettes(self) -> Dict[ColorBlindMode, Dict[str, Tuple[int, int, int]]]:
        """Initialize color palettes for different color blind modes"""
        return {
            ColorBlindMode.NORMAL: {
                'player1': (0, 255, 0),      # Green
                'player2': (255, 255, 0),    # Yellow
                'ball': (255, 255, 255),     # White
                'powerup': (255, 0, 255),    # Magenta
                'danger': (255, 0, 0),       # Red
                'safe': (0, 255, 0),         # Green
            },
            ColorBlindMode.PROTANOPIA: {
                'player1': (0, 150, 255),    # Blue
                'player2': (255, 200, 0),    # Orange
                'ball': (255, 255, 255),     # White
                'powerup': (200, 0, 255),    # Purple
                'danger': (255, 150, 0),     # Orange
                'safe': (0, 150, 255),       # Blue
            },
            ColorBlindMode.DEUTERANOPIA: {
                'player1': (0, 100, 255),    # Blue
                'player2': (255, 180, 0),    # Orange
                'ball': (255, 255, 255),     # White
                'powerup': (180, 0, 255),    # Purple
                'danger': (255, 150, 0),     # Orange
                'safe': (0, 100, 255),       # Blue
            },
            ColorBlindMode.TRITANOPIA: {
                'player1': (255, 0, 100),    # Pink
                'player2': (0, 255, 200),    # Cyan
                'ball': (255, 255, 255),     # White
                'powerup': (255, 100, 200),  # Light pink
                'danger': (255, 0, 100),     # Pink
                'safe': (0, 255, 200),       # Cyan
            },
            ColorBlindMode.MONOCHROMACY: {
                'player1': (200, 200, 200),  # Light gray
                'player2': (100, 100, 100),  # Dark gray
                'ball': (255, 255, 255),     # White
                'powerup': (150, 150, 150),  # Medium gray
                'danger': (50, 50, 50),      # Very dark gray
                'safe': (200, 200, 200),     # Light gray
            },
        }
    
    def set_color_blind_mode(self, mode: ColorBlindMode) -> None:
        """Set color blind mode"""
        self.color_blind_mode = mode
        logger.info(f"Color blind mode set to: {mode.name}")
    
    def get_color(self, color_name: str) -> Tuple[int, int, int]:
        """
        Get color adjusted for current accessibility mode.
        
        Args:
            color_name: Name of color (player1, player2, ball, etc.)
        
        Returns:
            RGB color tuple
        """
        palette = self._color_palettes.get(self.color_blind_mode, {})
        color = palette.get(color_name, (255, 255, 255))
        
        # Apply high contrast if enabled
        if self.high_contrast:
            color = self._apply_high_contrast(color)
        
        return color
    
    def _apply_high_contrast(self, color: Tuple[int, int, int]) -> Tuple[int, int, int]:
        """Apply high contrast adjustment to color"""
        # Increase contrast by pushing colors toward extremes
        r, g, b = color
        
        def adjust_channel(c: int) -> int:
            if c < 128:
                return max(0, c - 50)
            else:
                return min(255, c + 50)
        
        return (adjust_channel(r), adjust_channel(g), adjust_channel(b))
    
    def enable_high_contrast(self) -> None:
        """Enable high contrast mode"""
        self.high_contrast = True
        logger.info("High contrast mode enabled")
    
    def disable_high_contrast(self) -> None:
        """Disable high contrast mode"""
        self.high_contrast = False
        logger.info("High contrast mode disabled")
    
    def enable_large_ui(self) -> None:
        """Enable larger UI elements"""
        self.large_ui = True
        logger.info("Large UI mode enabled")
    
    def disable_large_ui(self) -> None:
        """Disable larger UI elements"""
        self.large_ui = False
        logger.info("Large UI mode disabled")
    
    def get_ui_scale(self) -> float:
        """Get UI scale factor based on accessibility settings"""
        return 1.5 if self.large_ui else 1.0
    
    def enable_audio_cues(self) -> None:
        """Enable audio cues for important events"""
        self.audio_cues = True
        logger.info("Audio cues enabled")
    
    def disable_audio_cues(self) -> None:
        """Disable audio cues"""
        self.audio_cues = False
        logger.info("Audio cues disabled")
    
    def enable_reduce_motion(self) -> None:
        """Enable reduced motion (less animations)"""
        self.reduce_motion = True
        logger.info("Reduced motion enabled")
    
    def disable_reduce_motion(self) -> None:
        """Disable reduced motion"""
        self.reduce_motion = False
        logger.info("Reduced motion disabled")
    
    def should_play_animation(self) -> bool:
        """Check if animations should be played"""
        return not self.reduce_motion
    
    def get_animation_speed(self) -> float:
        """Get animation speed multiplier"""
        return 0.5 if self.reduce_motion else 1.0
    
    def announce(self, text: str) -> None:
        """
        Announce text for screen readers.
        
        Args:
            text: Text to announce
        """
        if not self.screen_reader:
            return
        
        # Log for screen reader integration
        logger.info(f"[SCREEN_READER] {text}")
        
        # In a real implementation, this would interface with
        # platform-specific screen reader APIs
    
    def get_settings(self) -> Dict[str, any]:
        """Get current accessibility settings"""
        return {
            'color_blind_mode': self.color_blind_mode.name,
            'high_contrast': self.high_contrast,
            'large_ui': self.large_ui,
            'audio_cues': self.audio_cues,
            'screen_reader': self.screen_reader,
            'reduce_motion': self.reduce_motion,
        }
    
    def load_settings(self, settings: Dict[str, any]) -> None:
        """Load accessibility settings"""
        try:
            mode_name = settings.get('color_blind_mode', 'NORMAL')
            self.color_blind_mode = ColorBlindMode[mode_name]
            
            self.high_contrast = settings.get('high_contrast', False)
            self.large_ui = settings.get('large_ui', False)
            self.audio_cues = settings.get('audio_cues', True)
            self.screen_reader = settings.get('screen_reader', False)
            self.reduce_motion = settings.get('reduce_motion', False)
            
            logger.info("Accessibility settings loaded")
        except Exception as e:
            logger.error(f"Failed to load accessibility settings: {e}")


class VisualIndicator:
    """Visual indicator for audio events (for deaf/hard of hearing)"""
    
    def __init__(self, screen_width: int, screen_height: int):
        self.screen_width = screen_width
        self.screen_height = screen_height
        self.indicators: List[Dict] = []
        self.max_indicators = 5
    
    def add_indicator(
        self,
        text: str,
        position: Tuple[int, int],
        color: Tuple[int, int, int] = (255, 255, 0),
        duration: int = 60,
    ) -> None:
        """
        Add a visual indicator.
        
        Args:
            text: Text to display
            position: Screen position
            color: Indicator color
            duration: Duration in frames
        """
        if len(self.indicators) >= self.max_indicators:
            self.indicators.pop(0)
        
        self.indicators.append({
            'text': text,
            'position': position,
            'color': color,
            'duration': duration,
            'age': 0,
        })
    
    def update(self) -> None:
        """Update indicators"""
        # Age indicators and remove expired ones
        self.indicators = [
            {**ind, 'age': ind['age'] + 1}
            for ind in self.indicators
            if ind['age'] < ind['duration']
        ]
    
    def draw(self, surface: pygame.Surface, font: pygame.font.Font) -> None:
        """Draw all indicators"""
        for ind in self.indicators:
            # Fade out based on age
            alpha = int(255 * (1 - ind['age'] / ind['duration']))
            color = tuple(min(255, max(0, c * alpha // 255)) for c in ind['color'])
            
            text_surface = font.render(ind['text'], True, color)
            surface.blit(text_surface, ind['position'])


class KeyboardNavigator:
    """Keyboard navigation for menus (accessibility)"""
    
    def __init__(self):
        self.items: List[str] = []
        self.selected_index = 0
    
    def set_items(self, items: List[str]) -> None:
        """Set navigable items"""
        self.items = items
        self.selected_index = 0
    
    def navigate_up(self) -> None:
        """Navigate to previous item"""
        if self.items:
            self.selected_index = (self.selected_index - 1) % len(self.items)
    
    def navigate_down(self) -> None:
        """Navigate to next item"""
        if self.items:
            self.selected_index = (self.selected_index + 1) % len(self.items)
    
    def get_selected(self) -> Optional[str]:
        """Get currently selected item"""
        if self.items and 0 <= self.selected_index < len(self.items):
            return self.items[self.selected_index]
        return None
    
    def get_selected_index(self) -> int:
        """Get selected index"""
        return self.selected_index


# Global accessibility manager
_accessibility_manager: Optional[AccessibilityManager] = None


def get_accessibility_manager() -> AccessibilityManager:
    """Get global accessibility manager instance"""
    global _accessibility_manager
    if _accessibility_manager is None:
        _accessibility_manager = AccessibilityManager()
    return _accessibility_manager
