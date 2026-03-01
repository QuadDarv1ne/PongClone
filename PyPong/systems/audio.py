import pygame
from PyPong.core.config import *
from pathlib import Path
from PyPong.core.logger import logger

class AudioManager:
    def __init__(self):
        pygame.mixer.init()
        self.sounds = {}
        self.music_loaded = False
        self._init_paths()
        self.load_audio()

    def _init_paths(self):
        """Инициализировать пути к аудиофайлам"""
        # Используем абсолютные пути относительно этого файла
        base_path = Path(__file__).parent.parent / 'assets'
        self.music_path = base_path / 'music' / MUSIC_FILE
        self.sounds_path = base_path / 'sounds'
        
    def load_audio(self):
        """Загрузить аудиофайлы с проверкой существования"""
        # Музыка
        if self.music_path.exists():
            try:
                pygame.mixer.music.load(str(self.music_path))
                self.music_loaded = True
            except Exception as e:
                print(f"Audio: Could not load music: {e}")

        # Звуки
        sound_files = {
            "beep": BEEP_SOUND,
            "score": SCORE_SOUND,
            "powerup": POWERUP_SOUND
        }

        for name, filename in sound_files.items():
            sound_path = self.sounds_path / filename
            if sound_path.exists():
                try:
                    self.sounds[name] = pygame.mixer.Sound(str(sound_path))
                except Exception as e:
                    print(f"Audio: Could not load {name}: {e}")

    def play_music(self, loops=-1):
        if self.music_loaded:
            try:
                pygame.mixer.music.play(loops)
            except pygame.error as e:
                logger.error(f"Failed to play music: {e}")

    def stop_music(self):
        pygame.mixer.music.stop()

    def play_sound(self, sound_name):
        if sound_name in self.sounds:
            try:
                self.sounds[sound_name].play()
            except pygame.error as e:
                logger.error(f"Failed to play sound {sound_name}: {e}")
