"""UI components for the game"""
import json
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
    """Меню настроек с категориями и описаниями"""

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
        "sound_theme": "settings.sound_theme",
        "colorblind_mode": "settings.colorblind_mode",
        "high_contrast": "settings.high_contrast",
        "reduce_motion": "settings.reduce_motion",
        "audio_cues": "settings.audio_cues",
        "large_ui": "settings.large_ui",
        "window_mode": "settings.window_mode",
        "ball_speed": "settings.ball_speed",
        "paddle_size": "settings.paddle_size",
        "vsync": "settings.vsync",
        "powerup_spawn_chance": "settings.powerup_spawn_chance",
        "reset_defaults": "settings.reset_defaults",
        "export_settings": "settings.export_settings",
        "import_settings": "settings.import_settings",
        "controls_page": "settings.controls_page",
        "back": "settings.back",
    }

    THEMES = ["classic", "dark", "neon", "retro", "ocean"]
    DIFFICULTIES = ["Easy", "Medium", "Hard"]
    TARGET_FPS_OPTIONS = [30, 60, 120]
    PERFORMANCE_PROFILES = ["low", "medium", "high", "ultra"]
    SOUND_THEMES = ["classic", "retro", "futuristic", "minimal"]
    COLORBLIND_MODES = ["normal", "protanopia", "deuteranopia", "tritanopia", "monochromacy"]
    WINDOW_MODES = ["windowed", "borderless", "fullscreen"]
    BALL_SPEED_OPTIONS = [2, 3, 4, 5, 6, 7, 8]
    PADDLE_SIZE_OPTIONS = [60, 80, 100, 120, 140, 160]
    POWERUP_SPAWN_OPTIONS = [0, 250, 500, 750, 1000]  # per 1000 ticks

    # Categorized options with category headers
    CATEGORIZED_OPTIONS = [
        # Audio
        ("category_audio", True),
        ("music_volume", False),
        ("sfx_volume", False),
        ("sound_theme", False),
        ("audio_cues", False),
        # Video
        ("category_video", True),
        ("window_mode", False),
        ("theme", False),
        ("vsync", False),
        ("show_fps", False),
        # Gameplay
        ("category_gameplay", True),
        ("difficulty", False),
        ("winning_score", False),
        ("ball_speed", False),
        ("paddle_size", False),
        ("powerup_spawn_chance", False),
        ("touch_controls", False),
        # Appearance
        ("settings_category_appearance", True),
        ("language", False),
        ("large_ui", False),
        # Performance
        ("settings_category_performance", True),
        ("performance_profile", False),
        ("target_fps", False),
        ("enable_effects", False),
        ("enable_shake", False),
        ("reduce_motion", False),
        # Accessibility
        ("settings_category_accessibility", True),
        ("colorblind_mode", False),
        ("high_contrast", False),
        # Actions
        ("controls_page", False),
        ("export_settings", False),
        ("import_settings", False),
        ("reset_defaults", False),
        # Footer
        ("back", False),
    ]

    def __init__(self, screen: pygame.Surface, settings: Settings) -> None:
        self.screen = screen
        self.settings = settings
        self.font = pygame.font.SysFont(FONT_NAME, 36)
        self.small_font = pygame.font.SysFont(FONT_NAME, 28)
        self.title_font = pygame.font.SysFont(FONT_NAME, 40, bold=True)
        self.desc_font = pygame.font.SysFont(FONT_NAME, 22)
        self.search_font = pygame.font.SysFont(FONT_NAME, 24)
        self.selected = 0
        self._build_options()
        # Scroll offset for long menus
        self.scroll_offset = 0
        self.max_visible = 12
        # Controls page state
        self.showing_controls = False
        # Reset confirmation state
        self.awaiting_reset_confirm = False
        # Search
        self.search_query = ""
        self.search_active = False
        self.filtered_options = list(range(len(self.options)))
        # Presets
        self.showing_presets = False
        self.presets_selected = 0
        self._build_presets()

    def _build_options(self) -> None:
        """Build flat options list from categorized structure"""
        self.options: List[str] = []
        self.category_headers: List[int] = []  # indices of category header rows
        for key, is_header in self.CATEGORIZED_OPTIONS:
            self.options.append(key)
            if is_header:
                self.category_headers.append(len(self.options) - 1)

    def _build_presets(self) -> None:
        """Define setting presets"""
        self.presets = {
            "casual": {
                "name_key": "settings.preset_casual",
                "settings": {
                    "difficulty": "Easy",
                    "winning_score": 3,
                    "ball_speed": 3,
                    "paddle_size": 140,
                    "powerup_spawn_chance": 750,
                    "enable_effects": True,
                    "enable_shake": False,
                    "target_fps": 60,
                    "performance_profile": "medium",
                    "audio_cues": True,
                    "reduce_motion": False,
                }
            },
            "competitive": {
                "name_key": "settings.preset_competitive",
                "settings": {
                    "difficulty": "Hard",
                    "winning_score": 11,
                    "ball_speed": 6,
                    "paddle_size": 80,
                    "powerup_spawn_chance": 0,
                    "enable_effects": False,
                    "enable_shake": False,
                    "target_fps": 120,
                    "performance_profile": "high",
                    "audio_cues": False,
                    "reduce_motion": True,
                }
            },
            "streamer": {
                "name_key": "settings.preset_streamer",
                "settings": {
                    "difficulty": "Medium",
                    "winning_score": 5,
                    "ball_speed": 4,
                    "paddle_size": 100,
                    "powerup_spawn_chance": 500,
                    "enable_effects": True,
                    "enable_shake": True,
                    "target_fps": 60,
                    "performance_profile": "ultra",
                    "show_fps": False,
                    "audio_cues": True,
                }
            },
            "accessibility": {
                "name_key": "settings.preset_accessibility",
                "settings": {
                    "difficulty": "Easy",
                    "winning_score": 3,
                    "ball_speed": 2,
                    "paddle_size": 160,
                    "powerup_spawn_chance": 250,
                    "enable_effects": True,
                    "enable_shake": False,
                    "target_fps": 60,
                    "performance_profile": "medium",
                    "audio_cues": True,
                    "reduce_motion": True,
                    "high_contrast": True,
                    "large_ui": True,
                    "colorblind_mode": "normal",
                }
            },
        }
        self.preset_keys = list(self.presets.keys())

    def _apply_preset(self, preset_key: str) -> None:
        """Apply a preset configuration"""
        preset = self.presets.get(preset_key)
        if not preset:
            return

        for key, value in preset["settings"].items():
            self.settings.set(key, value)

        # Re-apply accessibility and performance settings
        self._apply_accessibility_changes()
        self._apply_vsync()

        # Apply performance profile if set
        profile = self.settings.get("performance_profile")
        if profile:
            self._apply_profile(profile)

        logger.info(f"Applied preset: {preset_key}")

    def draw(self) -> None:
        """Отрисовать меню настроек с категориями и описаниями"""
        if self.showing_controls:
            self._draw_controls_page()
            return

        if self.showing_presets:
            self._draw_presets()
            return

        self.screen.fill((15, 15, 25))

        # Title with underline
        title = self.title_font.render(t("settings.title"), True, (100, 200, 255))
        title_rect = title.get_rect(center=(WINDOW_WIDTH // 2, 30))
        self.screen.blit(title, title_rect)

        # Search bar
        self._draw_search_bar()

        # Presets button hint
        presets_btn = self.search_font.render(
            t("settings.presets_button"), True, (150, 200, 100)
        )
        self.screen.blit(presets_btn, (WINDOW_WIDTH - 200, 45))

        # Calculate scroll offset to keep selected item visible
        if self.selected < self.scroll_offset:
            self.scroll_offset = self.selected
        elif self.selected >= self.scroll_offset + self.max_visible:
            self.scroll_offset = self.selected - self.max_visible + 1

        # Draw options (filtered by search if active)
        start_y = 85
        line_height = 32

        options_to_draw = self.filtered_options if self.search_active else list(range(len(self.options)))

        visible_count = 0
        for i in options_to_draw:
            if visible_count >= self.max_visible:
                break

            visible_y = start_y + visible_count * line_height
            option = self.options[i]
            visible_count += 1

            # Category header
            if i in self.category_headers:
                header_text = t(self.OPTION_KEYS.get(option, option))
                header_surf = self.small_font.render(header_text, True, (80, 160, 200))
                self.screen.blit(header_surf, (WINDOW_WIDTH // 2 - header_surf.get_width() // 2, visible_y))
                # Separator line
                pygame.draw.line(
                    self.screen, (40, 60, 80),
                    (50, visible_y + line_height - 2),
                    (WINDOW_WIDTH - 50, visible_y + line_height - 2),
                    1,
                )
                continue

            # Selected highlight
            if i == self.selected:
                highlight_rect = pygame.Rect(40, visible_y - 2, WINDOW_WIDTH - 80, line_height)
                pygame.draw.rect(self.screen, (30, 40, 60), highlight_rect, border_radius=4)
                pygame.draw.rect(self.screen, (80, 160, 255), highlight_rect, 1, border_radius=4)

            color = (255, 220, 100) if i == self.selected else (200, 200, 210)

            if option != "back":
                display_name = t(self.OPTION_KEYS.get(option, option))
                value = self.settings.get(option)

                # Format value based on option type
                if value is None:
                    value = "N/A"
                elif option in ("music_volume", "sfx_volume"):
                    value = f"{value:.0%}"
                elif option in ("show_fps", "fullscreen", "touch_controls",
                                "enable_effects", "enable_shake", "audio_cues",
                                "high_contrast", "large_ui", "reduce_motion", "vsync"):
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
                elif option == "sound_theme":
                    value = t(f"settings.sound_{value}", value.title())
                elif option == "colorblind_mode":
                    value = t(f"settings.colorblind_{value}", value.title())
                elif option == "window_mode":
                    value = t(f"settings.{value}", value.title())
                elif option == "ball_speed":
                    value = str(value)
                elif option == "paddle_size":
                    value = f"{value}px"
                elif option == "powerup_spawn_chance":
                    pct = value / 10 if value > 0 else 0
                    value = f"{pct:.0f}%" if value > 0 else t("misc.off")
                elif option in ("reset_defaults", "controls_page", "export_settings", "import_settings"):
                    value = ""

                if value:
                    text = f"{display_name}: {value}"
                else:
                    text = display_name
            else:
                text = t(self.OPTION_KEYS[option])

            text_surface = self.small_font.render(text, True, color)
            self.screen.blit(text_surface, (60, visible_y))

        # Description for selected option
        self._draw_description_for_selected()

        # Reset confirmation overlay
        if self.awaiting_reset_confirm:
            self._draw_reset_confirmation()

        # Scroll indicators
        if len(options_to_draw) > self.max_visible:
            if self.scroll_offset > 0:
                up_arrow = self.small_font.render("▲", True, (100, 100, 120))
                self.screen.blit(up_arrow, (WINDOW_WIDTH - 30, start_y - 18))
            last_visible_idx = min(self.scroll_offset + self.max_visible, len(options_to_draw))
            if last_visible_idx < len(options_to_draw):
                down_arrow = self.small_font.render("▼", True, (100, 100, 120))
                last_y = start_y + (self.max_visible - 1) * line_height
                self.screen.blit(down_arrow, (WINDOW_WIDTH - 30, last_y + line_height))

    def _draw_description(self) -> None:
        """Draw description for the currently selected option"""
        option = self.options[self.selected]
        if option in self.category_headers:
            return

        desc_key = f"settings.desc_{option}"
        desc = t(desc_key)
        # If translation returns the key itself, no description exists
        if desc == desc_key:
            return

        desc_surf = self.desc_font.render(desc, True, (120, 140, 160))
        # Position below the selected item
        desc_y = 100 + (self.selected - self.scroll_offset) * 32 + 32
        # Keep within screen bounds
        if desc_y > WINDOW_HEIGHT - 40:
            desc_y = WINDOW_HEIGHT - 40

        self.screen.blit(desc_surf, (60, desc_y))

    def _draw_description_for_selected(self) -> None:
        """Draw description for the currently selected option (search-aware)"""
        options_to_draw = self.filtered_options if self.search_active else list(range(len(self.options)))
        if not options_to_draw:
            return

        # Find the visible position of selected item
        try:
            visible_idx = options_to_draw.index(self.selected)
        except ValueError:
            return

        option = self.options[self.selected]
        if self.selected in self.category_headers:
            return

        desc_key = f"settings.desc_{option}"
        desc = t(desc_key)
        if desc == desc_key:
            return

        desc_surf = self.desc_font.render(desc, True, (120, 140, 160))
        desc_y = 85 + visible_idx * 32 + 32
        if desc_y > WINDOW_HEIGHT - 40:
            desc_y = WINDOW_HEIGHT - 40

        self.screen.blit(desc_surf, (60, desc_y))

    def _draw_search_bar(self) -> None:
        """Draw search bar"""
        search_x, search_y = 50, 55
        search_w, search_h = WINDOW_WIDTH - 100, 30

        # Search background
        bg_color = (40, 50, 70) if self.search_active else (30, 30, 40)
        pygame.draw.rect(self.screen, bg_color, (search_x, search_y, search_w, search_h), border_radius=6)
        if self.search_active:
            pygame.draw.rect(self.screen, (100, 200, 255), (search_x, search_y, search_w, search_h), 2, border_radius=6)

        # Search icon
        icon = self.search_font.render("🔍" if self.search_active else "⌕", True, (150, 150, 150))
        self.screen.blit(icon, (search_x + 8, search_y + 2))

        # Search text
        if self.search_query:
            text = self.search_font.render(self.search_query, True, (255, 255, 255))
            self.screen.blit(text, (search_x + 35, search_y + 3))
        elif self.search_active:
            placeholder = self.search_font.render(t("settings.search_placeholder"), True, (100, 100, 120))
            self.screen.blit(placeholder, (search_x + 35, search_y + 3))
        else:
            hint = self.search_font.render(t("settings.search_hint"), True, (100, 100, 120))
            self.screen.blit(hint, (search_x + 35, search_y + 3))

        # Result count
        if self.search_active:
            count = len(self.filtered_options) - len([i for i in self.filtered_options if i in self.category_headers])
            count_text = self.search_font.render(f"{count} found", True, (150, 200, 100))
            self.screen.blit(count_text, (search_x + search_w - 100, search_y + 3))

    def _update_search(self) -> None:
        """Filter options based on search query"""
        if not self.search_query:
            self.search_active = False
            self.filtered_options = list(range(len(self.options)))
            return

        self.search_active = True
        query = self.search_query.lower()
        self.filtered_options = []

        for i, option in enumerate(self.options):
            # Search in display name
            display_name = t(self.OPTION_KEYS.get(option, option)).lower()
            # Search in description
            desc_key = f"settings.desc_{option}"
            desc = t(desc_key).lower()
            # Search in option key itself
            key_search = option.lower()

            if query in display_name or query in desc or query in key_search:
                self.filtered_options.append(i)

        # Reset selection if needed
        if self.selected not in self.filtered_options and self.filtered_options:
            # Find closest visible option
            for i in self.filtered_options:
                if i not in self.category_headers:
                    self.selected = i
                    break

    def _draw_presets(self) -> None:
        """Draw presets screen"""
        self.screen.fill((15, 15, 25))

        # Title
        title = self.title_font.render(t("settings.presets_title"), True, (150, 200, 100))
        title_rect = title.get_rect(center=(WINDOW_WIDTH // 2, 50))
        self.screen.blit(title, title_rect)

        # Preset cards
        card_width = 400
        card_height = 120
        start_x = (WINDOW_WIDTH - card_width) // 2
        start_y = 120
        spacing = 20

        for i, preset_key in enumerate(self.preset_keys):
            preset = self.presets[preset_key]
            y = start_y + i * (card_height + spacing)

            # Card background
            is_selected = (i == self.presets_selected)
            card_color = (40, 60, 40) if is_selected else (30, 30, 40)
            pygame.draw.rect(self.screen, card_color, (start_x, y, card_width, card_height), border_radius=8)
            if is_selected:
                pygame.draw.rect(self.screen, (150, 200, 100), (start_x, y, card_width, card_height), 2, border_radius=8)

            # Preset name
            preset_name = t(preset["name_key"])
            name_surf = self.font.render(preset_name, True, (255, 255, 255))
            self.screen.blit(name_surf, (start_x + 20, y + 10))

            # Description (list key settings)
            settings_desc = []
            s = preset["settings"]
            if "difficulty" in s:
                settings_desc.append(t(f"difficulty.{s['difficulty'].lower()}"))
            if "ball_speed" in s:
                settings_desc.append(f"Speed: {s['ball_speed']}")
            if "paddle_size" in s:
                settings_desc.append(f"Paddle: {s['paddle_size']}")
            if "winning_score" in s:
                settings_desc.append(f"Score: {s['winning_score']}")

            desc_text = " | ".join(settings_desc)
            desc_surf = self.desc_font.render(desc_text, True, (150, 150, 150))
            self.screen.blit(desc_surf, (start_x + 20, y + 50))

            # Apply hint
            if is_selected:
                apply_hint = self.desc_font.render(f"ENTER: {t('settings.preset_apply')}", True, (150, 200, 100))
                self.screen.blit(apply_hint, (start_x + 20, y + 80))

        # Bottom hint
        back_hint = self.search_font.render(f"ESC: {t('settings.preset_back')}", True, (100, 100, 100))
        self.screen.blit(back_hint, (WINDOW_WIDTH // 2 - 60, WINDOW_HEIGHT - 50))

    def _draw_controls_page(self) -> None:
        """Draw the controls/keybindings page"""
        self.screen.fill((15, 15, 25))

        title = self.title_font.render(t("settings.controls_page"), True, (100, 200, 255))
        title_rect = title.get_rect(center=(WINDOW_WIDTH // 2, 60))
        self.screen.blit(title, title_rect)
        pygame.draw.line(
            self.screen, (60, 120, 180),
            (title_rect.left, title_rect.bottom + 4),
            (title_rect.right, title_rect.bottom + 4),
            2,
        )

        controls = [
            (t("controls.p1_up"), "A / W"),
            (t("controls.p1_down"), "Z / S"),
            (t("controls.p2_up"), t("help.player2_up").replace(" - Движение вверх", "").replace(" - Move Up", "")),
            (t("controls.p2_down"), t("help.player2_down").replace(" - Движение вниз", "").replace(" - Move Down", "")),
            ("", ""),
            (t("controls.pause"), "ESC"),
            (t("controls.select"), "ENTER"),
            (t("controls.settings"), "O (from menu)"),
            (t("controls.stats"), "S (from menu)"),
            (t("controls.help"), "F1 (from menu)"),
            (t("controls.campaign"), "C (from menu)"),
            ("", ""),
            (t("settings.title"), "LEFT/RIGHT to change"),
            ("Navigation", "UP / DOWN"),
            ("", ""),
            (t("misc.back"), "ESC / ENTER on Back"),
        ]

        y = 130
        for label, key in controls:
            if not label:
                y += 10
                continue
            label_surf = self.small_font.render(label, True, (200, 200, 210))
            key_surf = self.small_font.render(key, True, (255, 220, 100))
            self.screen.blit(label_surf, (80, y))
            self.screen.blit(key_surf, (WINDOW_WIDTH - 80 - key_surf.get_width(), y))
            y += 34

    def _draw_reset_confirmation(self) -> None:
        """Draw reset confirmation overlay"""
        overlay = pygame.Surface((WINDOW_WIDTH, WINDOW_HEIGHT), pygame.SRCALPHA)
        overlay.fill((0, 0, 0, 180))
        self.screen.blit(overlay, (0, 0))

        box_w, box_h = 450, 160
        box_x = (WINDOW_WIDTH - box_w) // 2
        box_y = (WINDOW_HEIGHT - box_h) // 2

        # Box
        pygame.draw.rect(self.screen, (30, 30, 45), (box_x, box_y, box_w, box_h), border_radius=8)
        pygame.draw.rect(self.screen, (80, 160, 255), (box_x, box_y, box_w, box_h), 2, border_radius=8)

        # Message
        msg = t("settings.reset_confirm")
        msg_surf = self.small_font.render(msg, True, (220, 220, 220))
        self.screen.blit(msg_surf, (box_x + 30, box_y + 30))

        # Options
        yes_text = self.small_font.render(t("misc.yes"), True, (100, 255, 100))
        no_text = self.small_font.render(t("misc.no"), True, (255, 100, 100))
        self.screen.blit(yes_text, (box_x + 120, box_y + 90))
        self.screen.blit(no_text, (box_x + 280, box_y + 90))

        hint = self.desc_font.render(f"{t('misc.yes')}: ENTER  |  {t('misc.no')}: ESC", True, (150, 150, 150))
        self.screen.blit(hint, (box_x + 60, box_y + 125))

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

        # Handle presets screen
        if self.showing_presets:
            if event.key == pygame.K_ESCAPE:
                self.showing_presets = False
            elif event.key == pygame.K_UP:
                self.presets_selected = max(0, self.presets_selected - 1)
            elif event.key == pygame.K_DOWN:
                self.presets_selected = min(len(self.preset_keys) - 1, self.presets_selected + 1)
            elif event.key == pygame.K_RETURN:
                preset_key = self.preset_keys[self.presets_selected]
                self._apply_preset(preset_key)
                self.showing_presets = False
            return None

        # Handle reset confirmation
        if self.awaiting_reset_confirm:
            if event.key == pygame.K_RETURN:
                self._reset_to_defaults()
                self.awaiting_reset_confirm = False
            elif event.key == pygame.K_ESCAPE:
                self.awaiting_reset_confirm = False
            return None

        # Handle search mode
        if self.search_active:
            if event.key == pygame.K_ESCAPE:
                # Exit search
                self.search_query = ""
                self._update_search()
            elif event.key == pygame.K_BACKSPACE:
                # Delete last character
                self.search_query = self.search_query[:-1]
                self._update_search()
            elif event.key == pygame.K_RETURN:
                # Exit search
                self.search_query = ""
                self._update_search()
            elif event.key == pygame.K_f:
                # Exit search (toggle)
                self.search_active = False
                self.search_query = ""
                self.filtered_options = list(range(len(self.options)))
            elif event.unicode and event.unicode.isprintable():
                # Add character to search
                self.search_query += event.unicode
                self._update_search()
            return None

        # Controls page
        if self.showing_controls:
            if event.key in (pygame.K_ESCAPE, pygame.K_RETURN, pygame.K_BACKSPACE):
                self.showing_controls = False
            return None

        if event.key == pygame.K_ESCAPE:
            return "back"

        if event.key == pygame.K_f:
            # Enter search mode
            self.search_active = True
            self.search_query = ""
            self.filtered_options = list(range(len(self.options)))
            return None

        if event.key == pygame.K_p:
            # Open presets
            self.showing_presets = True
            self.presets_selected = 0
            return None

        if event.key == pygame.K_UP:
            self._move_selection(-1)
        elif event.key == pygame.K_DOWN:
            self._move_selection(1)
        elif event.key == pygame.K_LEFT:
            self._adjust_value(-1)
        elif event.key == pygame.K_RIGHT:
            self._adjust_value(1)
        elif event.key == pygame.K_RETURN:
            option = self.options[self.selected]
            if option == "back":
                return "back"
            elif option == "controls_page":
                self.showing_controls = True
            elif option == "reset_defaults":
                self.awaiting_reset_confirm = True
            elif option == "export_settings":
                self._export_settings()
            elif option == "import_settings":
                self._import_settings()

        return None

    def _move_selection(self, direction: int) -> None:
        """Move selection skipping category headers"""
        if not self.options:
            return
        old_selected = self.selected
        for _ in range(len(self.options)):
            self.selected = (self.selected + direction) % len(self.options)
            if self.selected not in self.category_headers:
                break

    def _adjust_value(self, direction: int) -> None:
        """Изменить значение выбранной настройки"""
        option = self.options[self.selected]

        if option == "back" or option in self.category_headers:
            return

        if option == "controls_page":
            self.showing_controls = True
            return

        if option == "reset_defaults":
            self.awaiting_reset_confirm = True
            return

        current = self.settings.get(option)

        if option in ("music_volume", "sfx_volume"):
            new_value = max(0.0, min(1.0, current + direction * 0.1))
            self.settings.set(option, round(new_value, 1))
        elif option in ("show_fps", "fullscreen", "touch_controls",
                        "enable_effects", "enable_shake", "audio_cues",
                        "high_contrast", "large_ui", "reduce_motion", "vsync"):
            self.settings.set(option, not current)
            self._apply_accessibility_changes()
            if option == "vsync":
                self._apply_vsync()
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
        elif option == "sound_theme":
            current_idx = self.SOUND_THEMES.index(current) if current in self.SOUND_THEMES else 0
            new_idx = (current_idx + direction) % len(self.SOUND_THEMES)
            self.settings.set(option, self.SOUND_THEMES[new_idx])
        elif option == "colorblind_mode":
            current_idx = self.COLORBLIND_MODES.index(current) if current in self.COLORBLIND_MODES else 0
            new_idx = (current_idx + direction) % len(self.COLORBLIND_MODES)
            new_mode = self.COLORBLIND_MODES[new_idx]
            self.settings.set(option, new_mode)
            self._apply_accessibility_changes()
        elif option == "window_mode":
            current_idx = self.WINDOW_MODES.index(current) if current in self.WINDOW_MODES else 0
            new_idx = (current_idx + direction) % len(self.WINDOW_MODES)
            new_mode = self.WINDOW_MODES[new_idx]
            self.settings.set(option, new_mode)
            self._apply_window_mode(new_mode)
        elif option == "ball_speed":
            current_idx = self.BALL_SPEED_OPTIONS.index(current) if current in self.BALL_SPEED_OPTIONS else 2
            new_idx = (current_idx + direction) % len(self.BALL_SPEED_OPTIONS)
            self.settings.set(option, self.BALL_SPEED_OPTIONS[new_idx])
        elif option == "paddle_size":
            current_idx = self.PADDLE_SIZE_OPTIONS.index(current) if current in self.PADDLE_SIZE_OPTIONS else 2
            new_idx = (current_idx + direction) % len(self.PADDLE_SIZE_OPTIONS)
            self.settings.set(option, self.PADDLE_SIZE_OPTIONS[new_idx])
        elif option == "powerup_spawn_chance":
            current_idx = self.POWERUP_SPAWN_OPTIONS.index(current) if current in self.POWERUP_SPAWN_OPTIONS else 2
            new_idx = (current_idx + direction) % len(self.POWERUP_SPAWN_OPTIONS)
            self.settings.set(option, self.POWERUP_SPAWN_OPTIONS[new_idx])

    def _reset_to_defaults(self) -> None:
        """Reset all settings to default values"""
        defaults = Settings().default_settings()
        for key, value in defaults.items():
            self.settings.set(key, value)
        # Re-apply everything
        self._apply_accessibility_changes()
        self._apply_vsync()
        logger.info("Settings reset to defaults")

    def _export_settings(self) -> None:
        """Export current settings to a JSON file"""
        import datetime
        from pathlib import Path

        try:
            # Create exports directory
            exports_dir = Path(__file__).parent.parent / 'data' / 'exports'
            exports_dir.mkdir(parents=True, exist_ok=True)

            # Generate filename with timestamp
            timestamp = datetime.datetime.now().strftime("%Y%m%d_%H%M%S")
            filename = exports_dir / f"settings_{timestamp}.json"

            # Export only user settings (not internal ones)
            export_data = {
                "version": "1.0",
                "exported_at": datetime.datetime.now().isoformat(),
                "settings": {}
            }

            # Filter out internal/auto-detected settings
            skip_keys = {"auto_detected", "window_width", "window_height"}
            for key, value in self.settings.data.items():
                if key not in skip_keys:
                    export_data["settings"][key] = value

            with open(filename, 'w', encoding='utf-8') as f:
                json.dump(export_data, f, indent=2)

            logger.info(f"Settings exported to: {filename}")
            # Show notification (could be enhanced later)
            print(f"Settings exported to: {filename}")

        except Exception as e:
            logger.error(f"Failed to export settings: {e}")
            print(f"Export failed: {e}")

    def _import_settings(self) -> None:
        """Import settings from the most recent export file"""
        from pathlib import Path

        try:
            exports_dir = Path(__file__).parent.parent / 'data' / 'exports'

            if not exports_dir.exists():
                logger.info("No exports directory found")
                return

            # Find the most recent export file
            export_files = list(exports_dir.glob("settings_*.json"))
            if not export_files:
                logger.info("No export files found")
                return

            # Sort by modification time, get most recent
            latest_file = max(export_files, key=lambda f: f.stat().st_mtime)

            with open(latest_file, 'r', encoding='utf-8') as f:
                import_data = json.load(f)

            # Validate format
            if "settings" not in import_data:
                raise ValueError("Invalid export file format")

            # Import settings
            for key, value in import_data["settings"].items():
                self.settings.set(key, value)

            # Re-apply everything
            self._apply_accessibility_changes()
            self._apply_vsync()

            logger.info(f"Settings imported from: {latest_file}")
            print(f"Settings imported from: {latest_file.name}")

        except Exception as e:
            logger.error(f"Failed to import settings: {e}")
            print(f"Import failed: {e}")

    def _apply_vsync(self) -> None:
        """Apply vsync setting"""
        # Note: vsync in pygame requires recreating the display,
        # so we just save the setting for now. The game loop would
        # need to use pygame.display.flip() with vsync consideration.
        pass

    def _apply_window_mode(self, mode: str) -> None:
        """Apply window mode change to pygame display"""
        try:
            width = self.settings.get("window_width", WINDOW_WIDTH) or WINDOW_WIDTH
            height = self.settings.get("window_height", WINDOW_HEIGHT) or WINDOW_HEIGHT

            if mode == "fullscreen":
                pygame.display.set_mode((width, height), pygame.FULLSCREEN)
                self.settings.set("fullscreen", True)
            elif mode == "borderless":
                pygame.display.set_mode((width, height), pygame.NOFRAME)
                self.settings.set("fullscreen", False)
            else:  # windowed
                pygame.display.set_mode((width, height), pygame.RESIZABLE)
                self.settings.set("fullscreen", False)
            logger.info(f"Window mode changed to: {mode}")
        except pygame.error as e:
            logger.error(f"Failed to change window mode: {e}")

    def _apply_accessibility_changes(self) -> None:
        """Apply accessibility settings to the global accessibility manager"""
        from PyPong.ui.accessibility import get_accessibility_manager, ColorBlindMode

        mgr = get_accessibility_manager()
        cb_mode = self.settings.get("colorblind_mode", "normal")
        mode_map = {
            "normal": ColorBlindMode.NORMAL,
            "protanopia": ColorBlindMode.PROTANOPIA,
            "deuteranopia": ColorBlindMode.DEUTERANOPIA,
            "tritanopia": ColorBlindMode.TRITANOPIA,
            "monochromacy": ColorBlindMode.MONOCHROMACY,
        }
        mgr.set_color_blind_mode(mode_map.get(cb_mode, ColorBlindMode.NORMAL))

        if self.settings.get("high_contrast", False):
            mgr.enable_high_contrast()
        else:
            mgr.disable_high_contrast()

        if self.settings.get("reduce_motion", False):
            mgr.enable_reduce_motion()
        else:
            mgr.disable_reduce_motion()

        if self.settings.get("audio_cues", True):
            mgr.enable_audio_cues()
        else:
            mgr.disable_audio_cues()

        if self.settings.get("large_ui", False):
            mgr.enable_large_ui()
        else:
            mgr.disable_large_ui()

    def _apply_profile(self, profile_name: str) -> None:
        """Apply performance profile settings"""
        from PyPong.core.config import PERFORMANCE_PROFILES

        profile = PERFORMANCE_PROFILES.get(profile_name, PERFORMANCE_PROFILES["medium"])
        self.settings.set("max_particles", profile["max_particles"])
        self.settings.set("max_trails", profile["max_trails"])
        self.settings.set("target_fps", profile["target_fps"])
        self.settings.set("enable_shake", profile["enable_shake"])
        self.settings.set("enable_effects", profile["enable_effects"])
