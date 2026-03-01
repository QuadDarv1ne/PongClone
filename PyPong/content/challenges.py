"""Daily and weekly challenges system"""
import json
import os
from datetime import datetime, timedelta
from random import choice, randint

class Challenge:
    def __init__(self, challenge_id, name, description, challenge_type, target, reward, expires_at=None):
        self.id = challenge_id
        self.name = name
        self.description = description
        self.type = challenge_type  # 'daily' or 'weekly'
        self.target = target  # Target value to achieve
        self.progress = 0
        self.completed = False
        self.reward = reward  # Points or unlockables
        self.expires_at = expires_at
        self.claimed = False

    def update_progress(self, value):
        """Update challenge progress"""
        if not self.completed:
            self.progress = min(self.progress + value, self.target)
            if self.progress >= self.target:
                self.completed = True

    def is_expired(self):
        """Check if challenge has expired"""
        if self.expires_at:
            return datetime.now() > self.expires_at
        return False

    def to_dict(self):
        return {
            "id": self.id,
            "name": self.name,
            "description": self.description,
            "type": self.type,
            "target": self.target,
            "progress": self.progress,
            "completed": self.completed,
            "reward": self.reward,
            "expires_at": self.expires_at.isoformat() if self.expires_at else None,
            "claimed": self.claimed
        }

    @staticmethod
    def from_dict(data):
        expires_at = datetime.fromisoformat(data["expires_at"]) if data.get("expires_at") else None
        challenge = Challenge(
            data["id"], data["name"], data["description"],
            data["type"], data["target"], data["reward"], expires_at
        )
        challenge.progress = data.get("progress", 0)
        challenge.completed = data.get("completed", False)
        challenge.claimed = data.get("claimed", False)
        return challenge


class ChallengeManager:
    def __init__(self, filename="PyPong/data/challenges.json"):
        self.filename = filename
        self.daily_challenges = []
        self.weekly_challenges = []
        self.load_challenges()
        self.refresh_challenges()

    def load_challenges(self):
        """Load challenges from file"""
        if os.path.exists(self.filename):
            try:
                with open(self.filename, 'r') as f:
                    data = json.load(f)
                    self.daily_challenges = [Challenge.from_dict(c) for c in data.get("daily", [])]
                    self.weekly_challenges = [Challenge.from_dict(c) for c in data.get("weekly", [])]
            except:
                pass

    def save_challenges(self):
        """Save challenges to file"""
        try:
            data = {
                "daily": [c.to_dict() for c in self.daily_challenges],
                "weekly": [c.to_dict() for c in self.weekly_challenges]
            }
            with open(self.filename, 'w') as f:
                json.dump(data, f, indent=2)
        except:
            pass

    def refresh_challenges(self):
        """Refresh expired challenges"""
        # Remove expired daily challenges
        self.daily_challenges = [c for c in self.daily_challenges if not c.is_expired()]
        
        # Remove expired weekly challenges
        self.weekly_challenges = [c for c in self.weekly_challenges if not c.is_expired()]
        
        # Generate new daily challenges if needed
        if len(self.daily_challenges) < 3:
            self._generate_daily_challenges()
        
        # Generate new weekly challenges if needed
        if len(self.weekly_challenges) < 2:
            self._generate_weekly_challenges()
        
        self.save_challenges()

    def _generate_daily_challenges(self):
        """Generate new daily challenges"""
        tomorrow = datetime.now() + timedelta(days=1)
        tomorrow = tomorrow.replace(hour=0, minute=0, second=0, microsecond=0)
        
        challenge_templates = [
            ("Win Streak", "Win {target} games in a row", "win_streak", (3, 5), 100),
            ("Score Master", "Score {target} total points", "total_score", (20, 30), 100),
            ("Perfect Defense", "Win a game without missing {target} times", "no_miss", (3, 5), 150),
            ("Power Collector", "Collect {target} power-ups", "collect_powerups", (5, 10), 100),
            ("Speed Runner", "Win a game in under {target} minutes", "win_time", (2, 3), 150),
            ("Comeback King", "Win after being down by {target} points", "comeback", (3, 4), 200),
        ]
        
        while len(self.daily_challenges) < 3:
            template = choice(challenge_templates)
            target = randint(template[3][0], template[3][1])
            
            challenge = Challenge(
                f"daily_{len(self.daily_challenges)}_{datetime.now().strftime('%Y%m%d')}",
                template[0],
                template[1].format(target=target),
                "daily",
                target,
                template[4],
                tomorrow
            )
            self.daily_challenges.append(challenge)

    def _generate_weekly_challenges(self):
        """Generate new weekly challenges"""
        next_week = datetime.now() + timedelta(days=7)
        next_week = next_week.replace(hour=0, minute=0, second=0, microsecond=0)
        
        challenge_templates = [
            ("Weekly Warrior", "Win {target} games this week", "weekly_wins", (10, 15), 500),
            ("Point Machine", "Score {target} total points this week", "weekly_score", (100, 150), 500),
            ("Power Master", "Collect {target} power-ups this week", "weekly_powerups", (20, 30), 400),
            ("Undefeated", "Win {target} games without losing", "win_streak", (5, 7), 600),
            ("Marathon", "Play {target} games this week", "games_played", (15, 20), 400),
        ]
        
        while len(self.weekly_challenges) < 2:
            template = choice(challenge_templates)
            target = randint(template[3][0], template[3][1])
            
            challenge = Challenge(
                f"weekly_{len(self.weekly_challenges)}_{datetime.now().strftime('%Y%m%d')}",
                template[0],
                template[1].format(target=target),
                "weekly",
                target,
                template[4],
                next_week
            )
            self.weekly_challenges.append(challenge)

    def update_challenge(self, challenge_type, value):
        """Update challenge progress"""
        all_challenges = self.daily_challenges + self.weekly_challenges
        
        for challenge in all_challenges:
            if challenge.type == challenge_type or challenge.id.startswith(challenge_type):
                challenge.update_progress(value)
        
        self.save_challenges()

    def get_active_challenges(self):
        """Get all active challenges"""
        return {
            "daily": [c for c in self.daily_challenges if not c.completed],
            "weekly": [c for c in self.weekly_challenges if not c.completed]
        }

    def get_completed_challenges(self):
        """Get completed but unclaimed challenges"""
        return [c for c in self.daily_challenges + self.weekly_challenges 
                if c.completed and not c.claimed]

    def claim_reward(self, challenge_id):
        """Claim challenge reward"""
        for challenge in self.daily_challenges + self.weekly_challenges:
            if challenge.id == challenge_id and challenge.completed and not challenge.claimed:
                challenge.claimed = True
                self.save_challenges()
                return challenge.reward
        return 0
