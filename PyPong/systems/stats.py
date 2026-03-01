"""Stats manager for tracking game statistics"""
import json
import os
from pathlib import Path
from datetime import datetime
from PyPong.core.logger import logger, log_exception


class StatsManager:
    def __init__(self, filename="stats.json"):
        # Use absolute path relative to this module
        self.filename = Path(__file__).parent.parent / 'data' / filename
        self.stats = self.load_stats()

    def load_stats(self):
        if self.filename.exists():
            try:
                with open(self.filename, 'r', encoding='utf-8') as f:
                    return json.load(f)
            except json.JSONDecodeError as e:
                logger.error(f"Failed to parse stats file: {e}")
                return self.default_stats()
            except Exception as e:
                logger.error(f"Failed to load stats: {e}")
                return self.default_stats()
        return self.default_stats()

    def default_stats(self):
        return {
            "games_played": 0,
            "player1_wins": 0,
            "player2_wins": 0,
            "highest_score": 0,
            "total_goals": 0,
            "best_streak": 0,
            "last_played": None
        }

    @log_exception
    def save_stats(self):
        try:
            # Ensure data directory exists
            self.filename.parent.mkdir(parents=True, exist_ok=True)
            with open(self.filename, 'w', encoding='utf-8') as f:
                json.dump(self.stats, f, indent=2)
        except Exception as e:
            logger.error(f"Failed to save stats: {e}")

    def record_game(self, winner, player1_score, player2_score):
        self.stats["games_played"] += 1
        
        if winner == 1:
            self.stats["player1_wins"] += 1
        else:
            self.stats["player2_wins"] += 1
        
        self.stats["highest_score"] = max(
            self.stats["highest_score"],
            player1_score,
            player2_score
        )
        
        self.stats["total_goals"] += player1_score + player2_score
        self.stats["last_played"] = datetime.now().isoformat()
        
        self.save_stats()

    def get_win_rate(self, player):
        total = self.stats["player1_wins"] + self.stats["player2_wins"]
        if total == 0:
            return 0
        
        wins = self.stats[f"player{player}_wins"]
        return (wins / total) * 100

    def reset_stats(self):
        self.stats = self.default_stats()
        self.save_stats()
