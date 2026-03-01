"""Campaign mode with progressive difficulty levels"""
import json
import os
from datetime import datetime
from PyPong.core.config import *

class Level:
    def __init__(self, level_id, name, description, difficulty, modifiers, objectives, unlocked=False):
        self.id = level_id
        self.name = name
        self.description = description
        self.difficulty = difficulty
        self.modifiers = modifiers  # Dict of game modifiers
        self.objectives = objectives  # List of objectives to complete
        self.unlocked = unlocked
        self.completed = False
        self.stars = 0  # 0-3 stars based on performance
        self.best_time = None

    def to_dict(self):
        return {
            "id": self.id,
            "unlocked": self.unlocked,
            "completed": self.completed,
            "stars": self.stars,
            "best_time": self.best_time
        }

    def from_dict(self, data):
        self.unlocked = data.get("unlocked", False)
        self.completed = data.get("completed", False)
        self.stars = data.get("stars", 0)
        self.best_time = data.get("best_time")


class CampaignManager:
    def __init__(self, filename="PyPong/data/campaign_progress.json"):
        self.filename = filename
        self.levels = self._create_levels()
        self.current_level = None
        self.load_progress()

    def _create_levels(self):
        """Create all campaign levels"""
        levels = [
            # Tutorial levels
            Level(1, "First Contact", "Learn the basics", "Tutorial",
                  {"ai_speed": 3, "ball_speed": 3},
                  ["Score 3 points", "Don't miss more than 2 times"],
                  unlocked=True),
            
            Level(2, "Speed Up", "The game gets faster", "Easy",
                  {"ai_speed": 4, "ball_speed": 4, "speed_increase": 1.05},
                  ["Score 5 points", "Win the match"],
                  unlocked=False),
            
            # Modifier introduction levels
            Level(3, "Gravity Pull", "Ball affected by gravity", "Easy",
                  {"ai_speed": 4, "gravity": 0.2},
                  ["Score 5 points", "Complete in under 2 minutes"],
                  unlocked=False),
            
            Level(4, "Windy Day", "Wind pushes the ball", "Medium",
                  {"ai_speed": 5, "wind": 0.15},
                  ["Score 5 points", "Hit 10 perfect shots"],
                  unlocked=False),
            
            Level(5, "Power Rush", "Power-ups spawn frequently", "Medium",
                  {"ai_speed": 5, "powerup_frequency": 200},
                  ["Score 5 points", "Collect 5 power-ups"],
                  unlocked=False),
            
            # Challenge levels
            Level(6, "Speed Demon", "Everything is faster", "Hard",
                  {"ai_speed": 7, "ball_speed": 6, "speed_increase": 1.15},
                  ["Score 7 points", "Win without missing"],
                  unlocked=False),
            
            Level(7, "Chaos Mode", "Multiple modifiers active", "Hard",
                  {"ai_speed": 6, "gravity": 0.15, "wind": 0.1, "powerup_frequency": 300},
                  ["Score 7 points", "Complete in under 3 minutes"],
                  unlocked=False),
            
            Level(8, "Invisible Ball", "Ball becomes invisible periodically", "Hard",
                  {"ai_speed": 6, "invisible_ball": True, "invisible_interval": 3000},
                  ["Score 7 points", "Hit 15 shots while invisible"],
                  unlocked=False),
            
            Level(9, "Tiny Paddle", "Your paddle is smaller", "Expert",
                  {"ai_speed": 7, "player_paddle_size": 0.6},
                  ["Score 10 points", "Win the match"],
                  unlocked=False),
            
            Level(10, "Final Boss", "Ultimate challenge", "Expert",
                  {"ai_speed": 8, "ball_speed": 5, "gravity": 0.1, "wind": 0.1, 
                   "powerup_frequency": 400, "speed_increase": 1.2},
                  ["Score 10 points", "Complete in under 5 minutes", "Don't miss more than 3 times"],
                  unlocked=False),
        ]
        return levels

    def load_progress(self):
        """Load campaign progress from file"""
        if os.path.exists(self.filename):
            try:
                with open(self.filename, 'r') as f:
                    data = json.load(f)
                    for level in self.levels:
                        if str(level.id) in data:
                            level.from_dict(data[str(level.id)])
            except:
                pass

    def save_progress(self):
        """Save campaign progress to file"""
        try:
            data = {str(level.id): level.to_dict() for level in self.levels}
            with open(self.filename, 'w') as f:
                json.dump(data, f, indent=2)
        except:
            pass

    def get_level(self, level_id):
        """Get level by ID"""
        for level in self.levels:
            if level.id == level_id:
                return level
        return None

    def complete_level(self, level_id, stars, time_taken):
        """Mark level as completed and unlock next"""
        level = self.get_level(level_id)
        if level:
            level.completed = True
            level.stars = max(level.stars, stars)
            if level.best_time is None or time_taken < level.best_time:
                level.best_time = time_taken
            
            # Unlock next level
            next_level = self.get_level(level_id + 1)
            if next_level:
                next_level.unlocked = True
            
            self.save_progress()

    def get_unlocked_levels(self):
        """Get all unlocked levels"""
        return [level for level in self.levels if level.unlocked]

    def get_total_stars(self):
        """Get total stars earned"""
        return sum(level.stars for level in self.levels)

    def get_completion_percentage(self):
        """Get campaign completion percentage"""
        completed = sum(1 for level in self.levels if level.completed)
        return (completed / len(self.levels)) * 100
