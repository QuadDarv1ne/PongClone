"""UI themes for game visualization"""
from typing import Dict, Optional, Tuple

from PyPong.core.config import (
    BLACK,
    GRAY,
    GREEN,
    LIGHT_BLUE,
    RED,
    WHITE,
    YELLOW,
)
from PyPong.ui.accessibility import get_accessibility_manager


class Theme:
    """
    Тема оформления игры.
    """

    def __init__(self, name: str, colors: Dict[str, Tuple[int, int, int]]) -> None:
        self.name = name
        self.bg_color: Tuple[int, int, int] = colors["bg"]
        self.fg_color: Tuple[int, int, int] = colors["fg"]
        self.paddle1_color: Tuple[int, int, int] = colors["paddle1"]
        self.paddle2_color: Tuple[int, int, int] = colors["paddle2"]
        self.ball_color: Tuple[int, int, int] = colors["ball"]
        self.accent_color: Tuple[int, int, int] = colors["accent"]

    def apply_accessibility(self) -> None:
        """Apply accessibility color adjustments"""
        accessibility = get_accessibility_manager()

        # Apply color blind mode
        self.paddle1_color = accessibility.get_color("player1")
        self.paddle2_color = accessibility.get_color("player2")
        self.ball_color = accessibility.get_color("ball")

        # Apply high contrast
        if accessibility.high_contrast:
            self.bg_color = accessibility._apply_high_contrast(self.bg_color)
            self.fg_color = accessibility._apply_high_contrast(self.fg_color)


# Предопределённые темы
THEMES: Dict[str, Theme] = {
    "classic": Theme(
        "Classic", {"bg": GRAY, "fg": WHITE, "paddle1": GREEN, "paddle2": YELLOW, "ball": WHITE, "accent": LIGHT_BLUE}
    ),
    "neon": Theme(
        "Neon",
        {
            "bg": (10, 10, 30),
            "fg": (0, 255, 255),
            "paddle1": (255, 0, 255),
            "paddle2": (0, 255, 0),
            "ball": (255, 255, 0),
            "accent": (255, 0, 255),
        },
    ),
    "retro": Theme(
        "Retro",
        {
            "bg": (20, 20, 20),
            "fg": (0, 255, 0),
            "paddle1": (0, 255, 0),
            "paddle2": (0, 255, 0),
            "ball": (0, 255, 0),
            "accent": (0, 200, 0),
        },
    ),
    "ocean": Theme(
        "Ocean",
        {
            "bg": (10, 30, 60),
            "fg": (200, 230, 255),
            "paddle1": (50, 150, 255),
            "paddle2": (0, 200, 200),
            "ball": (200, 230, 255),
            "accent": (100, 200, 255),
        },
    ),
    "dark": Theme(
        "Dark",
        {
            "bg": (15, 15, 20),
            "fg": (220, 220, 220),
            "paddle1": (255, 100, 100),
            "paddle2": (100, 150, 255),
            "ball": (240, 240, 240),
            "accent": (255, 200, 100),
        },
    ),
}


def get_theme(name: str) -> Theme:
    """
    Получить тему по названию.

    Args:
        name: Название темы

    Returns:
        Theme: Объект темы (classic по умолчанию)
    """
    return THEMES.get(name, THEMES["classic"])


def get_available_themes() -> list:
    """Получить список доступных тем"""
    return list(THEMES.keys())
