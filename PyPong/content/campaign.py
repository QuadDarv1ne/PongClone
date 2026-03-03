"""Campaign mode with progressive difficulty levels"""
import json
from datetime import datetime
from pathlib import Path
from typing import Any, Dict, List, Optional

from PyPong.core.config import WINNING_SCORE
from PyPong.core.logger import log_exception, logger


class Level:
    """Campaign level"""

    def __init__(
        self,
        level_id: int,
        name: str,
        description: str,
        difficulty: str,
        modifiers: Dict[str, Any],
        objectives: List[str],
        unlocked: bool = False,
    ) -> None:
        self.id = level_id
        self.name = name
        self.description = description
        self.difficulty = difficulty
        self.modifiers = modifiers
        self.objectives = objectives
        self.unlocked = unlocked
        self.completed = False
        self.stars = 0
        self.best_time: Optional[float] = None

    def to_dict(self) -> Dict[str, Any]:
        """Serialize to dictionary"""
        return {
            "id": self.id,
            "unlocked": self.unlocked,
            "completed": self.completed,
            "stars": self.stars,
            "best_time": self.best_time,
        }

    def from_dict(self, data: Dict[str, Any]) -> None:
        """Deserialize from dictionary"""
        self.unlocked = data.get("unlocked", False)
        self.completed = data.get("completed", False)
        self.stars = data.get("stars", 0)
        self.best_time = data.get("best_time")


class CampaignManager:
    """Manages campaign mode progress"""

    def __init__(self, filename: str = "campaign-progress.json") -> None:
        self.filename = Path(__file__).parent.parent / "data" / filename
        self.levels: List[Level] = self._create_levels()
        self.current_level: Optional[Level] = None
        self.load_progress()

    def _create_levels(self) -> List[Level]:
        """Create all campaign levels"""
        levels: List[Level] = [
            Level(
                1,
                "First Contact",
                "Learn the basics",
                "Tutorial",
                {"ai_speed": 3, "ball_speed": 3},
                ["Score 3 points", "Don't miss more than 2 times"],
                unlocked=True,
            ),
            Level(
                2,
                "Speed Up",
                "The game gets faster",
                "Easy",
                {"ai_speed": 4, "ball_speed": 4, "speed_increase": 1.05},
                ["Score 5 points", "Win the match"],
                unlocked=False,
            ),
        ]
        return levels

    def load_progress(self) -> None:
        """Load campaign progress from file"""
        if self.filename.exists():
            try:
                with open(self.filename, "r", encoding="utf-8") as f:
                    data = json.load(f)
                    for level_data in data.get("levels", []):
                        level_id = level_data.get("id")
                        for level in self.levels:
                            if level.id == level_id:
                                level.from_dict(level_data)
                                break
                logger.info("Campaign progress loaded")
            except Exception as e:
                logger.error(f"Failed to load campaign progress: {e}")

    def save_progress(self) -> None:
        """Save campaign progress to file"""
        try:
            self.filename.parent.mkdir(parents=True, exist_ok=True)
            data = {"levels": [level.to_dict() for level in self.levels]}
            with open(self.filename, "w", encoding="utf-8") as f:
                json.dump(data, f, indent=2)
            logger.info("Campaign progress saved")
        except Exception as e:
            logger.error(f"Failed to save campaign progress: {e}")

    def get_level(self, level_id: int) -> Optional[Level]:
        """Get level by ID"""
        for level in self.levels:
            if level.id == level_id:
                return level
        return None

    def complete_level(self, level_id: int, stars: int = 1, time_taken: Optional[float] = None) -> bool:
        """Mark level as completed"""
        level = self.get_level(level_id)
        if not level:
            return False

        level.completed = True
        level.stars = max(level.stars, stars)

        if time_taken and (level.best_time is None or time_taken < level.best_time):
            level.best_time = time_taken

        # Unlock next level
        next_level = self.get_level(level_id + 1)
        if next_level:
            next_level.unlocked = True

        self.save_progress()
        return True

    def get_total_stars(self) -> int:
        """Get total stars earned"""
        return sum(level.stars for level in self.levels)

    def get_completion_percentage(self) -> float:
        """Get campaign completion percentage"""
        completed = sum(1 for level in self.levels if level.completed)
        return (completed / len(self.levels)) * 100 if self.levels else 0.0
