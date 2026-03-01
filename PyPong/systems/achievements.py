"""
Achievement system with unlockable rewards
"""
import json
from pathlib import Path
from typing import Dict, List, Optional, Callable
from datetime import datetime
from dataclasses import dataclass, asdict
from PyPong.core.constants import AchievementType, Balance, EventType
from PyPong.core.logger import logger, log_exception


@dataclass
class Achievement:
    """Achievement data class"""
    id: str
    name: str
    description: str
    type: AchievementType
    requirement: int
    progress: int = 0
    unlocked: bool = False
    unlocked_at: Optional[str] = None
    points: int = 0
    icon: str = "🏆"
    hidden: bool = False
    
    def update_progress(self, value: int) -> bool:
        """Update progress and check if unlocked"""
        if self.unlocked:
            return False
        
        self.progress = min(self.progress + value, self.requirement)
        
        if self.progress >= self.requirement:
            self.unlock()
            return True
        
        return False
    
    def unlock(self) -> None:
        """Unlock achievement"""
        if not self.unlocked:
            self.unlocked = True
            self.unlocked_at = datetime.now().isoformat()
            logger.info(f"Achievement unlocked: {self.name}")
    
    def get_progress_percent(self) -> float:
        """Get progress as percentage"""
        if self.requirement == 0:
            return 100.0
        return (self.progress / self.requirement) * 100
    
    def to_dict(self) -> dict:
        """Convert to dictionary"""
        data = asdict(self)
        # Convert enum to string for JSON serialization
        data['type'] = self.type.value
        return data
    
    @staticmethod
    def from_dict(data: dict) -> 'Achievement':
        """Create from dictionary"""
        # Convert type string back to enum
        if isinstance(data.get('type'), str):
            data['type'] = AchievementType(data['type'])
        return Achievement(**data)


class AchievementManager:
    """Manages achievements and unlockables"""
    
    def __init__(self, filename: str = "PyPong/data/achievements.json"):
        self.filename = Path(filename)
        self.achievements: Dict[str, Achievement] = {}
        self.listeners: Dict[EventType, List[Callable]] = {}
        self._create_achievements()
        self.load_progress()
        logger.info("Achievement system initialized")
    
    def _create_achievements(self) -> None:
        """Create all achievements"""
        achievements_data = [
            # Basic achievements
            Achievement(
                "first_win", "First Victory", "Win your first game",
                AchievementType.FIRST_WIN, 1,
                points=Balance.ACHIEVEMENT_POINTS[AchievementType.FIRST_WIN],
                icon="🎉"
            ),
            Achievement(
                "win_10", "Winning Streak", "Win 10 games",
                AchievementType.WIN_STREAK, 10,
                points=200, icon="🔥"
            ),
            Achievement(
                "win_50", "Champion", "Win 50 games",
                AchievementType.WIN_STREAK, 50,
                points=500, icon="👑"
            ),
            Achievement(
                "win_100", "Legend", "Win 100 games",
                AchievementType.WIN_STREAK, 100,
                points=1000, icon="⭐"
            ),
            
            # Perfect game achievements
            Achievement(
                "perfect_5", "Flawless", "Win without missing (score 5)",
                AchievementType.PERFECT_GAME, 1,
                points=300, icon="💎"
            ),
            Achievement(
                "perfect_10", "Untouchable", "Win 10 perfect games",
                AchievementType.PERFECT_GAME, 10,
                points=1000, icon="🛡️"
            ),
            
            # Speed achievements
            Achievement(
                "speed_60", "Quick Match", "Win in under 60 seconds",
                AchievementType.SPEED_DEMON, 1,
                points=250, icon="⚡"
            ),
            Achievement(
                "speed_30", "Lightning Fast", "Win in under 30 seconds",
                AchievementType.SPEED_DEMON, 1,
                points=750, icon="⚡⚡"
            ),
            
            # Power-up achievements
            Achievement(
                "powerup_10", "Power User", "Collect 10 power-ups",
                AchievementType.POWER_COLLECTOR, 10,
                points=150, icon="💪"
            ),
            Achievement(
                "powerup_50", "Power Master", "Collect 50 power-ups",
                AchievementType.POWER_COLLECTOR, 50,
                points=300, icon="💪💪"
            ),
            Achievement(
                "powerup_all", "Gotta Catch 'Em All", "Collect all power-up types",
                AchievementType.POWER_COLLECTOR, 10,
                points=500, icon="🎁"
            ),
            
            # Campaign achievements
            Achievement(
                "campaign_5", "Adventurer", "Complete 5 campaign levels",
                AchievementType.CAMPAIGN_COMPLETE, 5,
                points=500, icon="🗺️"
            ),
            Achievement(
                "campaign_all", "Campaign Master", "Complete all campaign levels",
                AchievementType.CAMPAIGN_COMPLETE, 10,
                points=2000, icon="🏆"
            ),
            Achievement(
                "all_stars", "Star Collector", "Get 3 stars on all levels",
                AchievementType.ALL_STARS, 30,
                points=5000, icon="⭐⭐⭐"
            ),
            
            # Challenge achievements
            Achievement(
                "challenge_10", "Challenge Accepted", "Complete 10 challenges",
                AchievementType.CHALLENGE_MASTER, 10,
                points=300, icon="📋"
            ),
            Achievement(
                "challenge_50", "Challenge Master", "Complete 50 challenges",
                AchievementType.CHALLENGE_MASTER, 50,
                points=1500, icon="📋📋"
            ),
            
            # Mini-game achievements
            Achievement(
                "minigame_all", "Mini-game Expert", "Complete all mini-games",
                AchievementType.MINIGAME_EXPERT, 5,
                points=1000, icon="🎮"
            ),
            Achievement(
                "target_1000", "Sharpshooter", "Score 1000 in Target Practice",
                AchievementType.MINIGAME_EXPERT, 1000,
                points=500, icon="🎯"
            ),
            Achievement(
                "breakout_clear", "Brick Breaker", "Clear all bricks in Breakout",
                AchievementType.MINIGAME_EXPERT, 1,
                points=300, icon="🧱"
            ),
            
            # Hidden achievements
            Achievement(
                "secret_combo", "Combo Master", "Get a 20x combo",
                AchievementType.PERFECT_GAME, 1,
                points=1000, icon="🔗", hidden=True
            ),
            Achievement(
                "secret_reverse", "Backwards Wizard", "Win with reverse controls",
                AchievementType.PERFECT_GAME, 1,
                points=750, icon="🔄", hidden=True
            ),
        ]
        
        for achievement in achievements_data:
            self.achievements[achievement.id] = achievement
    
    @log_exception
    def load_progress(self) -> None:
        """Load achievement progress"""
        if not self.filename.exists():
            logger.debug("No achievement file found, starting fresh")
            return
        
        try:
            with open(self.filename, 'r', encoding='utf-8') as f:
                data = json.load(f)
                
            for ach_id, ach_data in data.items():
                if ach_id in self.achievements:
                    # Update existing achievement with saved data
                    saved = Achievement.from_dict(ach_data)
                    self.achievements[ach_id].progress = saved.progress
                    self.achievements[ach_id].unlocked = saved.unlocked
                    self.achievements[ach_id].unlocked_at = saved.unlocked_at
            
            logger.info(f"Loaded {len(data)} achievement records")
        except Exception as e:
            logger.error(f"Failed to load achievements: {e}", exc_info=True)
    
    @log_exception
    def save_progress(self) -> None:
        """Save achievement progress"""
        try:
            data = {
                ach_id: ach.to_dict()
                for ach_id, ach in self.achievements.items()
            }
            
            with open(self.filename, 'w', encoding='utf-8') as f:
                json.dump(data, f, indent=2)
            
            logger.debug("Achievement progress saved")
        except Exception as e:
            logger.error(f"Failed to save achievements: {e}", exc_info=True)
    
    def update_achievement(self, achievement_id: str, value: int = 1) -> bool:
        """Update achievement progress"""
        if achievement_id not in self.achievements:
            logger.warning(f"Unknown achievement: {achievement_id}")
            return False
        
        achievement = self.achievements[achievement_id]
        unlocked = achievement.update_progress(value)
        
        if unlocked:
            self._on_achievement_unlocked(achievement)
            self.save_progress()
        
        return unlocked
    
    def _on_achievement_unlocked(self, achievement: Achievement) -> None:
        """Handle achievement unlock"""
        logger.log_event(
            EventType.ACHIEVEMENT_UNLOCKED.value,
            {
                'achievement_id': achievement.id,
                'achievement_name': achievement.name,
                'points': achievement.points
            }
        )
        
        # Trigger listeners
        if EventType.ACHIEVEMENT_UNLOCKED in self.listeners:
            for callback in self.listeners[EventType.ACHIEVEMENT_UNLOCKED]:
                try:
                    callback(achievement)
                except Exception as e:
                    logger.error(f"Achievement callback error: {e}")
    
    def get_unlocked_achievements(self) -> List[Achievement]:
        """Get all unlocked achievements"""
        return [ach for ach in self.achievements.values() if ach.unlocked]
    
    def get_locked_achievements(self) -> List[Achievement]:
        """Get all locked achievements (excluding hidden)"""
        return [
            ach for ach in self.achievements.values()
            if not ach.unlocked and not ach.hidden
        ]
    
    def get_total_points(self) -> int:
        """Get total achievement points earned"""
        return sum(
            ach.points for ach in self.achievements.values()
            if ach.unlocked
        )
    
    def get_completion_percentage(self) -> float:
        """Get achievement completion percentage"""
        total = len(self.achievements)
        unlocked = len(self.get_unlocked_achievements())
        return (unlocked / total) * 100 if total > 0 else 0
    
    def register_listener(self, event_type: EventType, callback: Callable) -> None:
        """Register event listener"""
        if event_type not in self.listeners:
            self.listeners[event_type] = []
        self.listeners[event_type].append(callback)
    
    def check_event(self, event_type: EventType, **kwargs) -> None:
        """Check and update achievements based on event"""
        if event_type == EventType.GAME_END:
            if kwargs.get('won'):
                self.update_achievement('first_win')
                self.update_achievement('win_10')
                self.update_achievement('win_50')
                self.update_achievement('win_100')
                
                if kwargs.get('perfect'):
                    self.update_achievement('perfect_5')
                    self.update_achievement('perfect_10')
                
                duration = kwargs.get('duration', 0)
                if duration < 60:
                    self.update_achievement('speed_60')
                if duration < 30:
                    self.update_achievement('speed_30')
        
        elif event_type == EventType.POWERUP_COLLECTED:
            self.update_achievement('powerup_10')
            self.update_achievement('powerup_50')
        
        elif event_type == EventType.LEVEL_COMPLETE:
            self.update_achievement('campaign_5')
            self.update_achievement('campaign_all')
            
            stars = kwargs.get('stars', 0)
            if stars == 3:
                self.update_achievement('all_stars')
        
        elif event_type == EventType.CHALLENGE_COMPLETE:
            self.update_achievement('challenge_10')
            self.update_achievement('challenge_50')
        
        elif event_type == EventType.COMBO:
            combo = kwargs.get('combo', 0)
            if combo >= 20:
                self.update_achievement('secret_combo')
