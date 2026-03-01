import json
import os
from datetime import datetime

class StatsManager:
    def __init__(self, filename="PyPong/data/stats.json"):
        self.filename = filename
        self.stats = self.load_stats()

    def load_stats(self):
        if os.path.exists(self.filename):
            try:
                with open(self.filename, 'r') as f:
                    return json.load(f)
            except:
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

    def save_stats(self):
        try:
            with open(self.filename, 'w') as f:
                json.dump(self.stats, f, indent=2)
        except:
            pass

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
