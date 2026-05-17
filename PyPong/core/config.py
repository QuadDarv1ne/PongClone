# Game Configuration
WINDOW_WIDTH = 1024
WINDOW_HEIGHT = 720
FPS = 60

# Colors
WHITE = (255, 255, 255)
BLACK = (0, 0, 0)
GRAY = (80, 80, 80)
DARK_GRAY = (40, 40, 40)
LIGHT_BLUE = (173, 216, 230)
RED = (255, 0, 0)
GREEN = (0, 255, 0)
YELLOW = (255, 255, 0)

# Paddle settings
PADDLE_WIDTH = 10
PADDLE_HEIGHT = 100
PADDLE_SPEED = 10
PADDLE_OFFSET = 50

# Ball settings
BALL_SIZE = 10
BALL_INITIAL_SPEED = 4
BALL_SPEED_INCREASE = 1.1
MAX_BALL_SPEED = 20

# Game settings
WINNING_SCORE = 5
POWERUP_DURATION = 5000
POWERUP_SPAWN_CHANCE = 500

# Game modes
GAME_MODE_AI = "ai"
GAME_MODE_PVP = "pvp"

# AI settings
DIFFICULTY_LEVELS = {
    "Easy": {"ai_speed": 4, "ball_increase": 1.05},
    "Medium": {"ai_speed": 6, "ball_increase": 1.1},
    "Hard": {"ai_speed": 8, "ball_increase": 1.2},
}

# Audio files
MUSIC_FILE = "endofline.ogg"
BEEP_SOUND = "beep.wav"
SCORE_SOUND = "score.wav"
POWERUP_SOUND = "powerup.wav"

# Font
FONT_NAME = "Helvetica"

# Effects limits (performance optimization)
MAX_PARTICLES = 50
MAX_TRAILS = 20
PARTICLES_PER_HIT = 8
TRAIL_SPAWN_CHANCE = 4  # 1 in 4 chance

# Screen shake settings
SHAKE_INTENSITY_NORMAL = (5, 5)
SHAKE_INTENSITY_GOAL = (15, 15)

# Power-up settings
POWERUP_TYPES = [
    "speed_boost",
    "large_paddle",
    "slow_ball",
    "multi_ball",
    "shrink_opponent",
]

# Performance profiles
PERFORMANCE_PROFILES = {
    "low": {
        "max_particles": 20,
        "max_trails": 10,
        "target_fps": 30,
        "enable_shake": False,
        "enable_effects": False,
    },
    "medium": {
        "max_particles": 30,
        "max_trails": 15,
        "target_fps": 60,
        "enable_shake": True,
        "enable_effects": True,
    },
    "high": {
        "max_particles": 50,
        "max_trails": 20,
        "target_fps": 60,
        "enable_shake": True,
        "enable_effects": True,
    },
    "ultra": {
        "max_particles": 100,
        "max_trails": 30,
        "target_fps": 120,
        "enable_shake": True,
        "enable_effects": True,
    },
}
