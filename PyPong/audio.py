import pygame
from config import *
import os

class AudioManager:
    def __init__(self):
        pygame.mixer.init()
        self.sounds = {}
        self.music_loaded = False
        self.load_audio()

    def load_audio(self):
        try:
            if os.path.exists(MUSIC_FILE):
                pygame.mixer.music.load(MUSIC_FILE)
                self.music_loaded = True
        except:
            print(f"Warning: Could not load music file {MUSIC_FILE}")

        sound_files = {
            "beep": BEEP_SOUND,
            "score": SCORE_SOUND,
            "powerup": POWERUP_SOUND
        }

        for name, file in sound_files.items():
            try:
                if os.path.exists(file):
                    self.sounds[name] = pygame.mixer.Sound(file)
            except:
                print(f"Warning: Could not load sound file {file}")

    def play_music(self, loops=-1):
        if self.music_loaded:
            try:
                pygame.mixer.music.play(loops)
            except:
                pass

    def stop_music(self):
        pygame.mixer.music.stop()

    def play_sound(self, sound_name):
        if sound_name in self.sounds:
            try:
                self.sounds[sound_name].play()
            except:
                pass
