"""
Sound theme system with different audio sets
"""
import pygame
from pathlib import Path
from typing import Dict, Optional
from dataclasses import dataclass
from PyPong.core.constants import SoundTheme
from PyPong.core.logger import logger, log_exception


@dataclass
class SoundConfig:
    """Sound configuration"""
    name: str
    file: str
    volume: float = 1.0


class AudioTheme:
    """Audio theme with sound effects"""
    
    def __init__(self, name: str, theme_type: SoundTheme):
        self.name = name
        self.type = theme_type
        self.sounds: Dict[str, pygame.mixer.Sound] = {}
        self.music_file: Optional[str] = None
        
    def add_sound(self, sound_id: str, config: SoundConfig) -> None:
        """Add sound to theme"""
        self.sounds[sound_id] = config
    
    def load_sounds(self, base_path: Path) -> bool:
        """Load all sounds"""
        success = True
        
        for sound_id, config in self.sounds.items():
            sound_path = base_path / config.file
            
            if not sound_path.exists():
                logger.warning(f"Sound file not found: {sound_path}")
                success = False
                continue
            
            try:
                sound = pygame.mixer.Sound(str(sound_path))
                sound.set_volume(config.volume)
                self.sounds[sound_id] = sound
                logger.debug(f"Loaded sound: {sound_id}")
            except Exception as e:
                logger.error(f"Failed to load sound {sound_id}: {e}")
                success = False
        
        return success


class SoundThemeManager:
    """Manages sound themes"""
    
    def __init__(self):
        self.themes: Dict[SoundTheme, AudioTheme] = {}
        self.current_theme: Optional[AudioTheme] = None
        self.master_volume = 1.0
        self.sfx_volume = 0.7
        self.music_volume = 0.5
        
        self._create_themes()
        logger.info("Sound theme manager initialized")
    
    def _create_themes(self) -> None:
        """Create all sound themes"""
        # Classic theme
        classic = AudioTheme("Classic", SoundTheme.CLASSIC)
        classic.add_sound("paddle_hit", SoundConfig("Paddle Hit", "beep.wav", 0.7))
        classic.add_sound("wall_hit", SoundConfig("Wall Hit", "beep.wav", 0.5))
        classic.add_sound("score", SoundConfig("Score", "score.wav", 0.8))
        classic.add_sound("powerup", SoundConfig("Power-up", "powerup.wav", 0.6))
        classic.music_file = "endofline.ogg"
        self.themes[SoundTheme.CLASSIC] = classic
        
        # Retro theme (8-bit style)
        retro = AudioTheme("Retro", SoundTheme.RETRO)
        retro.add_sound("paddle_hit", SoundConfig("Paddle Hit", "retro_beep.wav", 0.7))
        retro.add_sound("wall_hit", SoundConfig("Wall Hit", "retro_beep.wav", 0.5))
        retro.add_sound("score", SoundConfig("Score", "retro_score.wav", 0.8))
        retro.add_sound("powerup", SoundConfig("Power-up", "retro_powerup.wav", 0.6))
        retro.music_file = "retro_music.ogg"
        self.themes[SoundTheme.RETRO] = retro
        
        # Futuristic theme
        futuristic = AudioTheme("Futuristic", SoundTheme.FUTURISTIC)
        futuristic.add_sound("paddle_hit", SoundConfig("Paddle Hit", "future_hit.wav", 0.7))
        futuristic.add_sound("wall_hit", SoundConfig("Wall Hit", "future_wall.wav", 0.5))
        futuristic.add_sound("score", SoundConfig("Score", "future_score.wav", 0.8))
        futuristic.add_sound("powerup", SoundConfig("Power-up", "future_powerup.wav", 0.6))
        futuristic.music_file = "future_music.ogg"
        self.themes[SoundTheme.FUTURISTIC] = futuristic
        
        # Minimal theme (subtle sounds)
        minimal = AudioTheme("Minimal", SoundTheme.MINIMAL)
        minimal.add_sound("paddle_hit", SoundConfig("Paddle Hit", "minimal_hit.wav", 0.4))
        minimal.add_sound("wall_hit", SoundConfig("Wall Hit", "minimal_wall.wav", 0.3))
        minimal.add_sound("score", SoundConfig("Score", "minimal_score.wav", 0.5))
        minimal.add_sound("powerup", SoundConfig("Power-up", "minimal_powerup.wav", 0.4))
        minimal.music_file = "minimal_music.ogg"
        self.themes[SoundTheme.MINIMAL] = minimal
    
    @log_exception
    def set_theme(self, theme_type: SoundTheme) -> bool:
        """Set current sound theme"""
        if theme_type not in self.themes:
            logger.warning(f"Unknown theme: {theme_type}")
            return False
        
        theme = self.themes[theme_type]
        
        # Load sounds if not loaded
        if not isinstance(list(theme.sounds.values())[0], pygame.mixer.Sound):
            base_path = Path(__file__).parent.parent / 'assets' / 'sounds'
            if not theme.load_sounds(base_path):
                logger.warning(f"Some sounds failed to load for theme: {theme.name}")
        
        self.current_theme = theme
        logger.info(f"Sound theme changed to: {theme.name}")
        
        # Load music
        if theme.music_file:
            self._load_music(theme.music_file)
        
        return True
    
    def _load_music(self, music_file: str) -> None:
        """Load background music"""
        music_path = Path(__file__).parent.parent / 'assets' / 'music' / music_file
        
        if not music_path.exists():
            logger.warning(f"Music file not found: {music_path}")
            return
        
        try:
            pygame.mixer.music.load(str(music_path))
            pygame.mixer.music.set_volume(self.music_volume)
            logger.debug(f"Loaded music: {music_file}")
        except Exception as e:
            logger.error(f"Failed to load music: {e}")
    
    def play_sound(self, sound_id: str) -> None:
        """Play sound effect"""
        if not self.current_theme:
            return
        
        if sound_id not in self.current_theme.sounds:
            logger.warning(f"Sound not found: {sound_id}")
            return
        
        sound = self.current_theme.sounds[sound_id]
        
        if isinstance(sound, pygame.mixer.Sound):
            try:
                sound.set_volume(self.sfx_volume * self.master_volume)
                sound.play()
            except Exception as e:
                logger.error(f"Failed to play sound {sound_id}: {e}")
    
    def play_music(self, loops: int = -1) -> None:
        """Play background music"""
        try:
            pygame.mixer.music.play(loops)
        except Exception as e:
            logger.error(f"Failed to play music: {e}")
    
    def stop_music(self) -> None:
        """Stop background music"""
        pygame.mixer.music.stop()
    
    def set_master_volume(self, volume: float) -> None:
        """Set master volume (0-1)"""
        self.master_volume = max(0, min(1, volume))
    
    def set_sfx_volume(self, volume: float) -> None:
        """Set SFX volume (0-1)"""
        self.sfx_volume = max(0, min(1, volume))
    
    def set_music_volume(self, volume: float) -> None:
        """Set music volume (0-1)"""
        self.music_volume = max(0, min(1, volume))
        pygame.mixer.music.set_volume(self.music_volume)
    
    def get_available_themes(self) -> Dict[SoundTheme, str]:
        """Get available themes"""
        return {theme_type: theme.name for theme_type, theme in self.themes.items()}


# Global sound theme manager
_sound_manager: Optional[SoundThemeManager] = None


def get_sound_manager() -> SoundThemeManager:
    """Get global sound manager"""
    global _sound_manager
    if _sound_manager is None:
        _sound_manager = SoundThemeManager()
    return _sound_manager
