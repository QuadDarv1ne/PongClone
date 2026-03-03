"""
Online leaderboard system (placeholder for backend integration)
"""
import hashlib
import json
from dataclasses import asdict, dataclass
from datetime import datetime
from pathlib import Path
from typing import Any, Dict, List, Optional

from PyPong.core.logger import logger


@dataclass
class LeaderboardEntry:
    """Single leaderboard entry"""

    player_id: str
    player_name: str
    score: int
    rank: int
    wins: int
    losses: int
    win_rate: float
    highest_combo: int
    total_playtime: float
    last_played: str

    def to_dict(self) -> Dict[str, Any]:
        return asdict(self)

    @staticmethod
    def from_dict(data: Dict[str, Any]) -> "LeaderboardEntry":
        return LeaderboardEntry(**data)


class LocalLeaderboard:
    """Local leaderboard storage (offline mode)"""

    def __init__(self):
        self.data_file = Path("PyPong/data/leaderboard.json")
        self.entries: List[LeaderboardEntry] = []
        self._load()

    def _load(self) -> None:
        """Load leaderboard from file"""
        if not self.data_file.exists():
            return

        try:
            with open(self.data_file, "r", encoding="utf-8") as f:
                data = json.load(f)

            self.entries = [LeaderboardEntry.from_dict(e) for e in data]
            logger.info(f"Loaded {len(self.entries)} leaderboard entries")

        except Exception as e:
            logger.error(f"Failed to load leaderboard: {e}")

    def _save(self) -> None:
        """Save leaderboard to file"""
        try:
            self.data_file.parent.mkdir(parents=True, exist_ok=True)

            data = [e.to_dict() for e in self.entries]

            with open(self.data_file, "w", encoding="utf-8") as f:
                json.dump(data, f, indent=2)

            logger.debug("Leaderboard saved")

        except Exception as e:
            logger.error(f"Failed to save leaderboard: {e}")

    def add_or_update_entry(
        self, player_name: str, score: int, wins: int = 0, losses: int = 0, highest_combo: int = 0, playtime: float = 0
    ) -> LeaderboardEntry:
        """Add or update leaderboard entry"""
        # Generate player ID
        player_id = hashlib.md5(player_name.encode()).hexdigest()[:8]

        # Find existing entry
        existing = None
        for entry in self.entries:
            if entry.player_id == player_id:
                existing = entry
                break

        if existing:
            # Update existing
            existing.score = max(existing.score, score)
            existing.wins += wins
            existing.losses += losses
            existing.win_rate = (
                existing.wins / (existing.wins + existing.losses) if (existing.wins + existing.losses) > 0 else 0
            )
            existing.highest_combo = max(existing.highest_combo, highest_combo)
            existing.total_playtime += playtime
            existing.last_played = datetime.now().isoformat()
            entry = existing
        else:
            # Create new
            win_rate = wins / (wins + losses) if (wins + losses) > 0 else 0
            entry = LeaderboardEntry(
                player_id=player_id,
                player_name=player_name,
                score=score,
                rank=0,  # Will be calculated
                wins=wins,
                losses=losses,
                win_rate=win_rate,
                highest_combo=highest_combo,
                total_playtime=playtime,
                last_played=datetime.now().isoformat(),
            )
            self.entries.append(entry)

        # Recalculate ranks
        self._recalculate_ranks()
        self._save()

        return entry

    def _recalculate_ranks(self) -> None:
        """Recalculate ranks based on score"""
        # Sort by score (descending)
        self.entries.sort(key=lambda e: e.score, reverse=True)

        # Assign ranks
        for i, entry in enumerate(self.entries):
            entry.rank = i + 1

    def get_top_entries(self, limit: int = 10) -> List[LeaderboardEntry]:
        """Get top N entries"""
        return self.entries[:limit]

    def get_player_entry(self, player_name: str) -> Optional[LeaderboardEntry]:
        """Get entry for specific player"""
        player_id = hashlib.md5(player_name.encode()).hexdigest()[:8]

        for entry in self.entries:
            if entry.player_id == player_id:
                return entry

        return None

    def get_player_rank(self, player_name: str) -> Optional[int]:
        """Get rank for specific player"""
        entry = self.get_player_entry(player_name)
        return entry.rank if entry else None


class OnlineLeaderboard:
    """
    Online leaderboard (placeholder for backend integration).

    In a real implementation, this would:
    - Connect to a REST API or WebSocket server
    - Handle authentication
    - Sync with backend database
    - Support real-time updates
    """

    def __init__(self, api_url: str = "https://api.pypong.example.com"):
        self.api_url = api_url
        self.connected = False
        self.local_cache = LocalLeaderboard()

        logger.info(f"Online leaderboard initialized (API: {api_url})")

    def connect(self, api_key: Optional[str] = None) -> bool:
        """
        Connect to online leaderboard service.

        Args:
            api_key: Optional API key for authentication

        Returns:
            True if connected successfully
        """
        # Placeholder for actual connection logic
        # In real implementation:
        # - Make HTTP request to API
        # - Verify API key
        # - Establish WebSocket connection for real-time updates

        logger.info("Attempting to connect to online leaderboard...")

        try:
            # Simulate connection
            # response = requests.get(f"{self.api_url}/health")
            # self.connected = response.status_code == 200

            # For now, just use local cache
            self.connected = False
            logger.warning("Online leaderboard not available, using local cache")

            return self.connected

        except Exception as e:
            logger.error(f"Failed to connect to online leaderboard: {e}")
            self.connected = False
            return False

    def submit_score(self, player_name: str, score: int, **kwargs) -> bool:
        """
        Submit score to online leaderboard.

        Args:
            player_name: Player name
            score: Score to submit
            **kwargs: Additional stats (wins, losses, etc.)

        Returns:
            True if submitted successfully
        """
        if not self.connected:
            # Fallback to local
            self.local_cache.add_or_update_entry(player_name, score, **kwargs)
            return True

        try:
            # Placeholder for API call
            # response = requests.post(
            #     f"{self.api_url}/scores",
            #     json={
            #         'player_name': player_name,
            #         'score': score,
            #         **kwargs
            #     }
            # )
            # return response.status_code == 200

            logger.info(f"Score submitted: {player_name} - {score}")
            return True

        except Exception as e:
            logger.error(f"Failed to submit score: {e}")
            # Fallback to local
            self.local_cache.add_or_update_entry(player_name, score, **kwargs)
            return False

    def get_global_leaderboard(self, limit: int = 100) -> List[LeaderboardEntry]:
        """
        Get global leaderboard.

        Args:
            limit: Number of entries to retrieve

        Returns:
            List of leaderboard entries
        """
        if not self.connected:
            # Fallback to local
            return self.local_cache.get_top_entries(limit)

        try:
            # Placeholder for API call
            # response = requests.get(f"{self.api_url}/leaderboard?limit={limit}")
            # data = response.json()
            # return [LeaderboardEntry.from_dict(e) for e in data]

            return self.local_cache.get_top_entries(limit)

        except Exception as e:
            logger.error(f"Failed to get global leaderboard: {e}")
            return self.local_cache.get_top_entries(limit)

    def get_friends_leaderboard(self, friend_ids: List[str]) -> List[LeaderboardEntry]:
        """
        Get leaderboard for friends only.

        Args:
            friend_ids: List of friend player IDs

        Returns:
            List of friend leaderboard entries
        """
        # Placeholder for friends leaderboard
        logger.info("Friends leaderboard not implemented yet")
        return []

    def get_regional_leaderboard(self, region: str, limit: int = 100) -> List[LeaderboardEntry]:
        """
        Get regional leaderboard.

        Args:
            region: Region code (e.g., 'US', 'EU', 'ASIA')
            limit: Number of entries

        Returns:
            List of regional leaderboard entries
        """
        # Placeholder for regional leaderboard
        logger.info(f"Regional leaderboard ({region}) not implemented yet")
        return self.get_global_leaderboard(limit)


class LeaderboardManager:
    """Manages both local and online leaderboards"""

    def __init__(self, enable_online: bool = False):
        self.local = LocalLeaderboard()
        self.online = OnlineLeaderboard() if enable_online else None
        self.online_enabled = enable_online

        if self.online_enabled and self.online:
            self.online.connect()

        logger.info(f"Leaderboard manager initialized (online={enable_online})")

    def submit_score(
        self, player_name: str, score: int, wins: int = 0, losses: int = 0, highest_combo: int = 0, playtime: float = 0
    ) -> bool:
        """Submit score to leaderboard(s)"""
        # Always save locally
        self.local.add_or_update_entry(player_name, score, wins, losses, highest_combo, playtime)

        # Submit online if enabled
        if self.online_enabled and self.online:
            self.online.submit_score(
                player_name, score, wins=wins, losses=losses, highest_combo=highest_combo, playtime=playtime
            )

        return True

    def get_leaderboard(self, mode: str = "local", limit: int = 10) -> List[LeaderboardEntry]:
        """
        Get leaderboard entries.

        Args:
            mode: 'local', 'global', 'friends', or 'regional'
            limit: Number of entries

        Returns:
            List of leaderboard entries
        """
        if mode == "local":
            return self.local.get_top_entries(limit)
        elif mode == "global" and self.online:
            return self.online.get_global_leaderboard(limit)
        elif mode == "friends" and self.online:
            return self.online.get_friends_leaderboard([])
        elif mode == "regional" and self.online:
            return self.online.get_regional_leaderboard("GLOBAL", limit)
        else:
            return self.local.get_top_entries(limit)

    def get_player_stats(self, player_name: str) -> Optional[Dict[str, Any]]:
        """Get detailed stats for a player"""
        entry = self.local.get_player_entry(player_name)

        if not entry:
            return None

        return {
            "rank": entry.rank,
            "score": entry.score,
            "wins": entry.wins,
            "losses": entry.losses,
            "win_rate": entry.win_rate * 100,
            "highest_combo": entry.highest_combo,
            "total_playtime_hours": entry.total_playtime / 3600,
            "last_played": entry.last_played,
        }


# Global instance
_leaderboard_manager: Optional[LeaderboardManager] = None


def get_leaderboard_manager(enable_online: bool = False) -> LeaderboardManager:
    """Get global leaderboard manager"""
    global _leaderboard_manager
    if _leaderboard_manager is None:
        _leaderboard_manager = LeaderboardManager(enable_online)
    return _leaderboard_manager
