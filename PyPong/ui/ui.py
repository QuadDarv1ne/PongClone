"""UI components for the game"""
import pygame
from typing import Any, Dict, List, Optional, Tuple
from PyPong.core.config import (
    WHITE, BLACK, GRAY, LIGHT_BLUE, RED, GREEN, YELLOW,
    FONT_NAME, WINDOW_WIDTH, WINDOW_HEIGHT,
)
from PyPong.core.entities import Paddle, PowerUp
from PyPong.systems.settings import Settings
from PyPong.ui.localization import t, get_current_language, cycle_language
from PyPong.core.logger import logger


class PowerUpIndicator:
    """Индикатор активных power-up"""

    def __init__(self) -> None:
        self.font = pygame.font.SysFont(FONT_NAME, 24)
        self.small_font = pygame.font.SysFont(FONT_NAME, 18)

    def draw(
        self,
        screen: pygame.Surface,
        powerups: pygame.sprite.Group,
        paddle1: Paddle,
        paddle2: Paddle
    ) -> None:
        """Отрисовать индикаторы power-up"""
        # Map powerup types to translation keys and colors
        name_map: Dict[str, str] = {
            "speed_boost": t("powerup.speed_boost"),
            "large_paddle": t("powerup.large_paddle"),
            "slow_ball": t("powerup.slow_ball"),
            "multi_ball": t("powerup.multi_ball"),
            "shrink_opponent": t("powerup.shrink_opponent")
        }
        color_map: Dict[str, Tuple[int, int, int]] = {
            "speed_boost": GREEN,
            "large_paddle": YELLOW,
            "slow_ball": LIGHT_BLUE,
            "multi_ball": RED,
            "shrink_opponent": (255, 165, 0),
        }

        from PyPong.core.entities import PowerUp
        duration_map = PowerUp.TYPES

        self._draw_paddle_effects(screen, paddle1, 20, name_map, color_map, duration_map)
        self._draw_paddle_effects(screen, paddle2, WINDOW_WIDTH - 220, name_map, color_map, duration_map)

    def _draw_paddle_effects(
        self,
        screen: pygame.Surface,
        paddle: Paddle,
        x_pos: int,
        name_map: Dict[str, str],
        color_map: Dict[str, Tuple[int, int, int]],
        duration_map: Dict[str, Dict[str, Any]]
    ) -> None:
        """Draw active power-up effects for a single paddle."""
        y_offset = 150
        now = pygame.time.get_ticks()

        # Clean up expired effects
        for expired in paddle.get_expired_effects(duration_map):
            paddle.remove_effect(expired)

        for effect_type, start_time in paddle.active_effects.items():
            duration = duration_map.get(effect_type, {}).get("duration", 0)
            elapsed = now - start_time

            # Skip expired timed effects (instant effects like multi_ball always show briefly)
            if duration > 0 and elapsed > duration:
                continue

            # Background
            bg_rect = pygame.Rect(x_pos, y_offset, 200, 50)
            pygame.draw.rect(screen, (40, 40, 40), bg_rect)
            effect_color = color_map.get(effect_type, WHITE)
            pygame.draw.rect(screen, effect_color, bg_rect, 2)

            # Power-up name
            name = self.font.render(
                name_map.get(effect_type, "Power-Up"),
                True, WHITE
            )
            screen.blit(name, (x_pos + 10, y_offset + 5))

            # Timer bar
            if duration > 0:
                progress = 1.0 - (elapsed / duration)
                bar_width, bar_height = 180, 10
                pygame.draw.rect(screen, (60, 60, 60), (x_pos + 10, y_offset + 32, bar_width, bar_height))
                pygame.draw.rect(screen, effect_color, (x_pos + 10, y_offset + 32, int(bar_width * max(0, progress)), bar_height))

            y_offset += 60


class FPSCounter:
    """Счётчик FPS"""
    
    def __init__(self) -> None:
        self.font = pygame.font.SysFont(FONT_NAME, 20)
    
    def draw(self, screen: pygame.Surface, clock: pygame.time.Clock) -> None:
        """Отрисовать FPS"""
        fps = int(clock.get_fps())
        color = GREEN if fps >= 55 else YELLOW if fps >= 30 else RED
        fps_text = self.font.render(f"FPS: {fps}", True, color)
        screen.blit(fps_text, (WINDOW_WIDTH - 100, 10))


class SettingsMenu:
    """Меню настроек"""

    # Native language display names
    LANGUAGE_NAMES = {
        "en": "English",
        "ru": "Русский",
        "es": "Español",
        "de": "Deutsch",
        "fr": "Français",
        "zh": "中文",
        "ja": "日本語",
    }

    # Translation keys for settings options
    OPTION_KEYS = {
        "music_volume": "settings.music_volume",
        "sfx_volume": "settings.sfx_volume",
        "show_fps": "settings.show_fps",
        "fullscreen": "settings.fullscreen",
        "touch_controls": "settings.touch_controls",
        "difficulty": "settings.difficulty",
        "winning_score": "settings.winning_score",
        "theme": "settings.theme",
        "target_fps": "settings.target_fps",
        "enable_effects": "settings.enable_effects",
        "enable_shake": "settings.enable_shake",
        "performance_profile": "settings.performance_profile",
        "language": "settings.language",
        "back": "settings.back",
    }

    THEMES = ["classic", "dark", "neon", "retro", "ocean"]
    DIFFICULTIES = ["Easy", "Medium", "Hard"]
    TARGET_FPS_OPTIONS = [30, 60, 120]
    PERFORMANCE_PROFILES = ["low", "medium", "high", "ultra"]

    def __init__(self, screen: pygame.Surface, settings: Settings) -> None:
        self.screen = screen
        self.settings = settings
        self.font = pygame.font.SysFont(FONT_NAME, 36)
        self.small_font = pygame.font.SysFont(FONT_NAME, 28)
        self.selected = 0
        self.options: List[str] = [
            "music_volume",
            "sfx_volume",
            "show_fps",
            "fullscreen",
            "touch_controls",
            "difficulty",
            "winning_score",
            "theme",
            "target_fps",
            "enable_effects",
            "enable_shake",
            "performance_profile",
            "language",
            "back",
        ]

    def draw(self) -> None:
        """Отрисовать меню настроек"""
        self.screen.fill(GRAY)

        title = self.font.render(t("settings.title"), True, WHITE)
        self.screen.blit(title, title.get_rect(center=(WINDOW_WIDTH // 2, 100)))

        for i, option in enumerate(self.options):
            color = YELLOW if i == self.selected else WHITE

            if option != "back":
                display_name = t(self.OPTION_KEYS.get(option, option))
                value = self.settings.get(option)
                if value is None:
                    value = "N/A"

                # Format value based on option type
                if option in ("music_volume", "sfx_volume"):
                    value = f"{value:.0%}"
                elif option in ("show_fps", "fullscreen", "touch_controls",
                                "enable_effects", "enable_shake"):
                    value = t("misc.on") if value else t("misc.off")
                elif option == "difficulty":
                    value = t(f"difficulty.{value.lower()}", value)
                elif option == "theme":
                    value = t(f"settings.theme_{value}", value.title())
                elif option == "language":
                    lang_code = get_current_language()
                    value = self.LANGUAGE_NAMES.get(lang_code, lang_code.upper())
                elif option == "target_fps":
                    value = f"{value} FPS"
                elif option == "performance_profile":
                    value = t(f"settings.profile_{value}", value.title())
                elif option == "winning_score":
                    value = str(value)

                text = f"{display_name}: {value}"
            else:
                text = t(self.OPTION_KEYS[option])

            text_surface = self.small_font.render(text, True, color)
            self.screen.blit(
                text_surface,
                text_surface.get_rect(center=(WINDOW_WIDTH // 2, 160 + i * 42)),
            )

    def handle_input(self, event: pygame.event.Event) -> Optional[str]:
        """
        Обработать ввод в меню настроек.

        Args:
            event: Событие pygame

        Returns:
            str или None: "back" если нажат ESC, иначе None
        """
        if event.type != pygame.KEYDOWN:
            return None

        if event.key == pygame.K_ESCAPE:
            return "back"

        if event.key == pygame.K_UP:
            self.selected = (self.selected - 1) % len(self.options)
        elif event.key == pygame.K_DOWN:
            self.selected = (self.selected + 1) % len(self.options)
        elif event.key == pygame.K_LEFT:
            self._adjust_value(-1)
        elif event.key == pygame.K_RIGHT:
            self._adjust_value(1)
        elif event.key == pygame.K_RETURN and self.options[self.selected] == "back":
            return "back"

        return None

    def _adjust_value(self, direction: int) -> None:
        """Изменить значение выбранной настройки"""
        option = self.options[self.selected]

        if option == "back":
            return

        current = self.settings.get(option)

        if option in ("music_volume", "sfx_volume"):
            new_value = max(0.0, min(1.0, current + direction * 0.1))
            self.settings.set(option, round(new_value, 1))
        elif option in ("show_fps", "fullscreen", "touch_controls",
                        "enable_effects", "enable_shake"):
            self.settings.set(option, not current)
        elif option == "theme":
            current_idx = self.THEMES.index(current) if current in self.THEMES else 0
            new_idx = (current_idx + direction) % len(self.THEMES)
            self.settings.set(option, self.THEMES[new_idx])
        elif option == "difficulty":
            current_idx = self.DIFFICULTIES.index(current) if current in self.DIFFICULTIES else 1
            new_idx = (current_idx + direction) % len(self.DIFFICULTIES)
            self.settings.set(option, self.DIFFICULTIES[new_idx])
        elif option == "winning_score":
            new_value = max(3, min(15, current + direction))
            self.settings.set(option, new_value)
        elif option == "target_fps":
            current_idx = self.TARGET_FPS_OPTIONS.index(current) if current in self.TARGET_FPS_OPTIONS else 1
            new_idx = (current_idx + direction) % len(self.TARGET_FPS_OPTIONS)
            self.settings.set(option, self.TARGET_FPS_OPTIONS[new_idx])
        elif option == "performance_profile":
            current_idx = self.PERFORMANCE_PROFILES.index(current) if current in self.PERFORMANCE_PROFILES else 1
            new_idx = (current_idx + direction) % len(self.PERFORMANCE_PROFILES)
            new_profile = self.PERFORMANCE_PROFILES[new_idx]
            self.settings.set(option, new_profile)
            self._apply_profile(new_profile)
        elif option == "language":
            new_lang = cycle_language()
            self.settings.set("language", new_lang)
            logger.info(f"Language changed to: {new_lang}")

    def _apply_profile(self, profile_name: str) -> None:
        """Apply performance profile settings"""
        from PyPong.core.config import PERFORMANCE_PROFILES

        profile = PERFORMANCE_PROFILES.get(profile_name, PERFORMANCE_PROFILES["medium"])
        self.settings.set("max_particles", profile["max_particles"])
        self.settings.set("max_trails", profile["max_trails"])
        self.settings.set("target_fps", profile["target_fps"])
        self.settings.set("enable_shake", profile["enable_shake"])
        self.settings.set("enable_effects", profile["enable_effects"])
