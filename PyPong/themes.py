from config import *

class Theme:
    def __init__(self, name, colors):
        self.name = name
        self.bg_color = colors["bg"]
        self.fg_color = colors["fg"]
        self.paddle1_color = colors["paddle1"]
        self.paddle2_color = colors["paddle2"]
        self.ball_color = colors["ball"]
        self.accent_color = colors["accent"]

THEMES = {
    "classic": Theme("Classic", {
        "bg": GRAY,
        "fg": WHITE,
        "paddle1": GREEN,
        "paddle2": YELLOW,
        "ball": WHITE,
        "accent": LIGHT_BLUE
    }),
    "neon": Theme("Neon", {
        "bg": (10, 10, 30),
        "fg": (0, 255, 255),
        "paddle1": (255, 0, 255),
        "paddle2": (0, 255, 0),
        "ball": (255, 255, 0),
        "accent": (255, 0, 255)
    }),
    "retro": Theme("Retro", {
        "bg": (20, 20, 20),
        "fg": (0, 255, 0),
        "paddle1": (0, 255, 0),
        "paddle2": (0, 255, 0),
        "ball": (0, 255, 0),
        "accent": (0, 200, 0)
    }),
    "ocean": Theme("Ocean", {
        "bg": (10, 30, 60),
        "fg": (200, 230, 255),
        "paddle1": (50, 150, 255),
        "paddle2": (0, 200, 200),
        "ball": (200, 230, 255),
        "accent": (100, 200, 255)
    })
}

def get_theme(name):
    return THEMES.get(name, THEMES["classic"])
