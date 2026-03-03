"""
Game constants using Enums for better type safety
"""
from enum import Enum, IntEnum
from typing import NamedTuple


class PowerUpType(Enum):
    """Power-up types"""

    SPEED_BOOST = "speed_boost"
    LARGE_PADDLE = "large_paddle"
    SLOW_BALL = "slow_ball"
    MULTI_BALL = "multi_ball"
    SHRINK_OPPONENT = "shrink_opponent"
    INVISIBLE_BALL = "invisible_ball"
    REVERSE_CONTROLS = "reverse_controls"
    SHIELD = "shield"
    FREEZE = "freeze"
    MAGNET = "magnet"


class Difficulty(Enum):
    """AI difficulty levels"""

    EASY = "Easy"
    MEDIUM = "Medium"
    HARD = "Hard"
    EXPERT = "Expert"
    INSANE = "Insane"


class GameMode(Enum):
    """Game modes"""

    AI = "ai"
    PVP = "pvp"
    CAMPAIGN = "campaign"
    MINIGAME = "minigame"
    TOURNAMENT = "tournament"


class ChallengeType(Enum):
    """Challenge types"""

    DAILY = "daily"
    WEEKLY = "weekly"
    SPECIAL = "special"


class ModifierType(Enum):
    """Modifier types"""

    GRAVITY = "gravity"
    WIND = "wind"
    INVISIBLE_BALL = "invisible_ball"
    SIZE = "size"
    SPEED = "speed"
    CURVE = "curve"
    MULTIBALL = "multiball"
    REVERSE_CONTROLS = "reverse_controls"
    BOUNCY_WALLS = "bouncy_walls"
    SLIPPERY_PADDLE = "slippery_paddle"


class AchievementType(Enum):
    """Achievement types"""

    FIRST_WIN = "first_win"
    WIN_STREAK = "win_streak"
    PERFECT_GAME = "perfect_game"
    SPEED_DEMON = "speed_demon"
    POWER_COLLECTOR = "power_collector"
    CAMPAIGN_COMPLETE = "campaign_complete"
    ALL_STARS = "all_stars"
    CHALLENGE_MASTER = "challenge_master"
    MINIGAME_EXPERT = "minigame_expert"


class ArenaType(Enum):
    """Arena types with obstacles"""

    CLASSIC = "classic"
    OBSTACLES = "obstacles"
    MOVING_WALLS = "moving_walls"
    PORTALS = "portals"
    SHRINKING = "shrinking"


class SoundTheme(Enum):
    """Sound themes"""

    CLASSIC = "classic"
    RETRO = "retro"
    FUTURISTIC = "futuristic"
    MINIMAL = "minimal"


class Color(NamedTuple):
    """RGB Color tuple"""

    r: int
    g: int
    b: int

    def to_tuple(self) -> tuple[int, int, int]:
        return (self.r, self.g, self.b)


class Colors:
    """Predefined colors"""

    WHITE = Color(255, 255, 255)
    BLACK = Color(0, 0, 0)
    GRAY = Color(80, 80, 80)
    LIGHT_BLUE = Color(173, 216, 230)
    RED = Color(255, 0, 0)
    GREEN = Color(0, 255, 0)
    YELLOW = Color(255, 255, 0)
    ORANGE = Color(255, 165, 0)
    PURPLE = Color(128, 0, 128)
    CYAN = Color(0, 255, 255)


class EventType(Enum):
    """Game event types for logging and achievements"""

    GAME_START = "game_start"
    GAME_END = "game_end"
    SCORE = "score"
    POWERUP_COLLECTED = "powerup_collected"
    POWERUP_ACTIVATED = "powerup_activated"
    LEVEL_COMPLETE = "level_complete"
    CHALLENGE_COMPLETE = "challenge_complete"
    ACHIEVEMENT_UNLOCKED = "achievement_unlocked"
    PERFECT_HIT = "perfect_hit"
    COMBO = "combo"


class LogLevel(IntEnum):
    """Logging levels"""

    DEBUG = 10
    INFO = 20
    WARNING = 30
    ERROR = 40
    CRITICAL = 50


# Game balance constants
class Balance:
    """Game balance constants"""

    COMBO_TIMEOUT_MS = 3000
    COMBO_MULTIPLIER = 1.5
    ACHIEVEMENT_POINTS = {
        AchievementType.FIRST_WIN: 100,
        AchievementType.WIN_STREAK: 500,
        AchievementType.PERFECT_GAME: 1000,
        AchievementType.SPEED_DEMON: 750,
        AchievementType.POWER_COLLECTOR: 300,
        AchievementType.CAMPAIGN_COMPLETE: 2000,
        AchievementType.ALL_STARS: 5000,
        AchievementType.CHALLENGE_MASTER: 1500,
        AchievementType.MINIGAME_EXPERT: 1000,
    }

    POWERUP_DURATIONS = {
        PowerUpType.SPEED_BOOST: 5000,
        PowerUpType.LARGE_PADDLE: 5000,
        PowerUpType.SLOW_BALL: 5000,
        PowerUpType.SHIELD: 10000,
        PowerUpType.FREEZE: 3000,
        PowerUpType.MAGNET: 7000,
    }

    AI_REACTION_DELAYS = {
        Difficulty.EASY: 200,
        Difficulty.MEDIUM: 100,
        Difficulty.HARD: 50,
        Difficulty.EXPERT: 20,
        Difficulty.INSANE: 0,
    }
