"""
Audio manager with graceful degradation for missing assets
"""
from pathlib import Path
from typing import Dict, Optional

import pygame

from PyPong.core.config import (
    BEEP_SOUND,
    MUSIC_FILE,
    POWERUP_SOUND,
    SCORE_SOUND,
)
from PyPong.core.logger import log_exception, logger


class AudioManager:
    """
    Менеджер аудио с graceful degradation.
    Если файлы не найдены, создаются заглушки.
    """

    def __init__(self) -> None:
        try:
            pygame.mixer.init()
        except pygame.error as e:  # type: ignore[attr-defined]
            logger.warning(f"Audio system initialization failed: {e}")
            self._audio_available = False
            return

        self._audio_available = True
        self.sounds: Dict[str, pygame.mixer.Sound] = {}
        self.music_loaded: bool = False
        self._fallback_mode: bool = False

        self._init_paths()
        self.load_audio()

    def _init_paths(self) -> None:
        """Инициализировать пути к аудиофайлам"""
        base_path = Path(__file__).parent.parent / "assets"
        self.music_path = base_path / "music" / MUSIC_FILE
        self.sounds_path = base_path / "sounds"

    @log_exception
    def load_audio(self) -> None:
        """Загрузить аудиофайлы с graceful degradation"""
        if not self._audio_available:
            return

        # Музыка
        self._load_music()

        # Звуки
        self._load_sound("beep", BEEP_SOUND)
        self._load_sound("score", SCORE_SOUND)
        self._load_sound("powerup", POWERUP_SOUND)

        # Логирование результата
        if self._fallback_mode:
            logger.warning("Audio loaded in fallback mode (some files missing)")
        else:
            logger.info("Audio loaded successfully")

    def _load_music(self) -> None:
        """Загрузить музыку"""
        if self.music_path.exists():
            try:
                pygame.mixer.music.load(str(self.music_path))
                self.music_loaded = True
                logger.debug(f"Music loaded: {self.music_path}")
            except pygame.error as e:  # type: ignore[attr-defined]
                logger.error(f"Failed to load music: {e}")
                self._fallback_mode = True
        else:
            logger.warning(f"Music file not found: {self.music_path}")
            self._fallback_mode = True

    def _load_sound(self, name: str, filename: str) -> None:
        """Загрузить звук с заглушкой при отсутствии"""
        sound_path = self.sounds_path / filename

        if sound_path.exists():
            try:
                self.sounds[name] = pygame.mixer.Sound(str(sound_path))
                logger.debug(f"Sound loaded: {name}")
            except pygame.error as e:  # type: ignore[attr-defined]
                logger.error(f"Failed to load sound '{name}': {e}")
                self._create_fallback_sound(name)
        else:
            logger.warning(f"Sound file not found: {name} ({filename})")
            self._create_fallback_sound(name)

    def _create_fallback_sound(self, name: str) -> None:
        """Создать заглушку для звука"""
        try:
            # Пустой звук (тишина)
            self.sounds[name] = pygame.mixer.Sound(buffer=bytes(1024))
            self._fallback_mode = True
        except pygame.error as e:  # type: ignore[attr-defined]
            logger.error(f"Failed to create fallback sound '{name}': {e}")

    @log_exception
    def play_music(self, loops: int = -1) -> None:
        """Воспроизвести музыку"""
        if not self._audio_available:
            return

        if self.music_loaded:
            try:
                pygame.mixer.music.play(loops)
            except pygame.error as e:  # type: ignore[attr-defined]
                logger.error(f"Failed to play music: {e}")

    @log_exception
    def stop_music(self) -> None:
        """Остановить музыку"""
        if self._audio_available:
            pygame.mixer.music.stop()

    @log_exception
    def play_sound(self, sound_name: str) -> None:
        """Воспроизвести звук"""
        if not self._audio_available:
            return

        if sound_name in self.sounds:
            try:
                self.sounds[sound_name].play()
            except pygame.error as e:  # type: ignore[attr-defined]
                logger.error(f"Failed to play sound '{sound_name}': {e}")

    @log_exception
    def set_music_volume(self, volume: float) -> None:
        """Установить громкость музыки (0.0 - 1.0)"""
        if self._audio_available:
            pygame.mixer.music.set_volume(max(0.0, min(1.0, volume)))

    @log_exception
    def set_sound_volume(self, volume: float) -> None:
        """Установить громкость звуков (0.0 - 1.0)"""
        if self._audio_available:
            for sound in self.sounds.values():
                sound.set_volume(max(0.0, min(1.0, volume)))

    @property
    def is_available(self) -> bool:
        """Проверить доступность аудио системы"""
        return self._audio_available

    @property
    def is_fallback_mode(self) -> bool:
        """Проверить режим заглушек"""
        return self._fallback_mode
