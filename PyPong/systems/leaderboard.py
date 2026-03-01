"""
High scores / Leaderboard system
"""
import json
from pathlib import Path
from typing import List, Optional, Dict, Any
from dataclasses import dataclass, asdict
from datetime import datetime

from PyPong.core.logger import logger


@dataclass
class HighScore:
    """Single high score entry"""
    rank: int
    name: str
    score: int
    mode: str
    difficulty: str
    date: str
    duration: int  # seconds
    
    def to_dict(self) -> Dict[str, Any]:
        return asdict(self)
    
    @staticmethod
    def from_dict(data: Dict[str, Any]) -> 'HighScore':
        return HighScore(**data)


class Leaderboard:
    """
    High scores manager with multiple categories
    """
    
    def __init__(self, filename: str = "leaderboard.json", max_entries: int = 100):
        self.filename = Path("PyPong/data") / filename
        self.max_entries = max_entries
        self.scores: Dict[str, List[HighScore]] = {
            'classic': [],
            'arcade': [],
            'multiplayer': [],
            'overall': [],
        }
        self._load()
    
    def _load(self):
        """Load scores from file"""
        if not self.filename.exists():
            return
        
        try:
            with open(self.filename, 'r', encoding='utf-8') as f:
                data = json.load(f)
            
            for mode, scores in data.get('scores', {}).items():
                if mode in self.scores:
                    self.scores[mode] = [
                        HighScore.from_dict(s) for s in scores[:self.max_entries]
                    ]
            
            logger.info(f"Loaded leaderboard: {self.filename}")
        except (json.JSONDecodeError, IOError) as e:
            logger.warning(f"Failed to load leaderboard: {e}")
    
    def save(self):
        """Save scores to file"""
        self.filename.parent.mkdir(parents=True, exist_ok=True)
        
        data = {
            'scores': {
                mode: [s.to_dict() for s in scores]
                for mode, scores in self.scores.items()
            },
            'last_updated': datetime.now().isoformat()
        }
        
        with open(self.filename, 'w', encoding='utf-8') as f:
            json.dump(data, f, indent=2)
        
        logger.info("Leaderboard saved")
    
    def add_score(self, name: str, score: int, mode: str, 
                  difficulty: str = "Medium", duration: int = 0) -> Optional[int]:
        """
        Add a new score.
        Returns rank if score is in top, None otherwise.
        """
        # Create new entry
        entry = HighScore(
            rank=0,
            name=name[:20],  # Limit name length
            score=score,
            mode=mode,
            difficulty=difficulty,
            date=datetime.now().strftime("%Y-%m-%d"),
            duration=duration
        )
        
        # Add to mode-specific list
        if mode not in self.scores:
            self.scores[mode] = []
        
        scores = self.scores[mode]
        rank = self._insert_score(scores, entry)
        
        # Add to overall
        if mode != 'overall':
            if 'overall' not in self.scores:
                self.scores['overall'] = []
            self._insert_score(self.scores['overall'], entry)
        
        # Recalculate ranks
        self._update_ranks()
        
        # Save
        self.save()
        
        return rank
    
    def _insert_score(self, scores: List[HighScore], entry: HighScore) -> Optional[int]:
        """Insert score in sorted list. Returns rank or None."""
        # Find position
        position = 0
        for i, s in enumerate(scores):
            if entry.score > s.score:
                position = i
                break
            position = i + 1
        
        if position < self.max_entries:
            scores.insert(position, entry)
            scores = scores[:self.max_entries]
            return position + 1
        
        return None
    
    def _update_ranks(self):
        """Update rank numbers for all lists"""
        for mode, scores in self.scores.items():
            for i, score in enumerate(scores):
                score.rank = i + 1
    
    def get_top(self, mode: str = 'overall', limit: int = 10) -> List[HighScore]:
        """Get top scores for mode"""
        if mode not in self.scores:
            return []
        return self.scores[mode][:limit]
    
    def get_player_rank(self, name: str, mode: str = 'overall') -> Optional[int]:
        """Get player's best rank"""
        if mode not in self.scores:
            return None
        
        for score in self.scores[mode]:
            if score.name == name:
                return score.rank
        
        return None
    
    def is_high_score(self, score: int, mode: str = 'overall') -> bool:
        """Check if score would be in leaderboard"""
        if mode not in self.scores:
            return True
        
        scores = self.scores[mode]
        
        if len(scores) < self.max_entries:
            return True
        
        return score > scores[-1].score
    
    def clear(self, mode: Optional[str] = None):
        """Clear scores"""
        if mode:
            if mode in self.scores:
                self.scores[mode] = []
        else:
            for key in self.scores:
                self.scores[key] = []
        
        self.save()
        logger.info(f"Cleared leaderboard: {mode or 'all'}")


# Global instance
_leaderboard: Optional[Leaderboard] = None


def get_leaderboard() -> Leaderboard:
    """Get global leaderboard instance"""
    global _leaderboard
    if _leaderboard is None:
        _leaderboard = Leaderboard()
    return _leaderboard
