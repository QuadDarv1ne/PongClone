"""Daily and weekly challenges system"""
import json
from datetime import datetime, timedelta
from pathlib import Path
from typing import List, Dict, Any, Optional
from random import choice, randint
from PyPong.core.logger import logger, log_exception


class Challenge:
    """Daily or weekly challenge"""
    
    def __init__(
        self, 
        challenge_id: str, 
        name: str, 
        description: str, 
        challenge_type: str,
        target: int, 
        reward: int, 
        expires_at: Optional[datetime] = None
    ) -> None:
        self.id = challenge_id
        self.name = name
        self.description = description
        self.type = challenge_type
        self.target = target
        self.progress = 0
        self.completed = False
        self.reward = reward
        self.expires_at = expires_at
        self.claimed = False

    def update_progress(self, value: int) -> None:
        """Update challenge progress"""
        if not self.completed:
            self.progress = min(self.progress + value, self.target)
            if self.progress >= self.target:
                self.completed = True

    def is_expired(self) -> bool:
        """Check if challenge has expired"""
        if self.expires_at:
            return datetime.now() > self.expires_at
        return False

    def to_dict(self) -> Dict[str, Any]:
        """Serialize to dictionary"""
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
    def from_dict(data: Dict[str, Any]) -> 'Challenge':
        """Deserialize from dictionary"""
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
    """Manages daily and weekly challenges"""
    
    def __init__(self, filename: str = "challenges.json") -> None:
        self.filename = Path(__file__).parent.parent / 'data' / filename
        self.daily: List[Challenge] = []
        self.weekly: List[Challenge] = []
        self._create_challenges()
        self.load_challenges()
    
    def _create_challenges(self) -> None:
        """Create default challenges"""
        challenge_templates = [
            ("Win Streak", "Win 3 games in a row", 3, 100),
            ("Power Collector", "Collect 5 power-ups", 5, 80),
            ("Perfect Game", "Win without missing 5 times", 5, 150),
            ("Speed Demon", "Win a game with ball speed > 15", 1, 120),
        ]
        
        now = datetime.now()
        daily_expires = now + timedelta(days=1)
        daily_expires = daily_expires.replace(hour=0, minute=0, second=0, microsecond=0)
        
        weekly_expires = now + timedelta(weeks=1)
        
        self.daily = [
            Challenge(f"daily_{i}_{now.strftime('%Y%m%d')}", name, desc, "daily", target, reward, daily_expires)
            for i, (name, desc, target, reward) in enumerate(challenge_templates[:3])
        ]
        
        self.weekly = [
            Challenge(f"weekly_{i}_{now.strftime('%Y%m')}", name, desc, "weekly", target * 3, reward * 2, weekly_expires)
            for i, (name, desc, target, reward) in enumerate(challenge_templates[:2])
        ]
    
    def load_challenges(self) -> None:
        """Load challenges from file"""
        if self.filename.exists():
            try:
                with open(self.filename, 'r', encoding='utf-8') as f:
                    data = json.load(f)
                    self.daily = [Challenge.from_dict(c) for c in data.get("daily", [])]
                    self.weekly = [Challenge.from_dict(c) for c in data.get("weekly", [])]
                logger.info("Challenges loaded")
            except Exception as e:
                logger.error(f"Failed to load challenges: {e}")
    
    def save_challenges(self) -> None:
        """Save challenges to file"""
        try:
            self.filename.parent.mkdir(parents=True, exist_ok=True)
            data = {
                "daily": [c.to_dict() for c in self.daily],
                "weekly": [c.to_dict() for c in self.weekly]
            }
            with open(self.filename, 'w', encoding='utf-8') as f:
                json.dump(data, f, indent=2)
        except Exception as e:
            logger.error(f"Failed to save challenges: {e}")
    
    def get_all_challenges(self) -> List[Challenge]:
        """Get all active challenges"""
        return self.daily + self.weekly
    
    def update_challenge(self, challenge_type: str, value: int) -> None:
        """Update challenge progress"""
        for challenge in self.get_all_challenges():
            if challenge.type == challenge_type and not challenge.completed:
                challenge.update_progress(value)
    
    def get_completed_challenges(self) -> List[Challenge]:
        """Get all completed challenges"""
        return [c for c in self.get_all_challenges() if c.completed]
