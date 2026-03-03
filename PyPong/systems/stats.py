"""Stats manager for tracking game statistics"""
import json
from datetime import datetime
from pathlib import Path
from typing import Any, Dict, Optional

from PyPong.core.event_bus import GameEvent, get_event_bus
from PyPong.core.logger import log_exception, logger


class StatsManager:
    """
    Менеджер статистики игр.
    """

    def __init__(self, filename: str = "stats.json") -> None:
        self.filename = Path(__file__).parent.parent / "data" / filename
        self.stats: Dict[str, Any] = self.load_stats()
        
        # Subscribe to event bus
        self.event_bus = get_event_bus()
        self._subscribe_to_events()

    def _subscribe_to_events(self) -> None:
        """Subscribe to relevant game events"""
        self.event_bus.subscribe(GameEvent.GAME_OVER, self._on_game_over)
        self.event_bus.subscribe(GameEvent.GOAL_SCORED, self._on_goal_scored)
        logger.debug("StatsManager subscribed to game events")

    def _on_game_over(self, data: Dict[str, Any]) -> None:
        """Handle game over event - record game stats"""
        winner = data.get("winner")
        player1_score = data.get("player1_score", 0)
        player2_score = data.get("player2_score", 0)
        
        if winner is not None:
            self.record_game(winner, player1_score, player2_score)

    def _on_goal_scored(self, data: Dict[str, Any]) -> None:
        """Handle goal scored event - track total goals"""
        self.stats["total_goals"] = self.stats.get("total_goals", 0) + 1

    def load_stats(self) -> Dict[str, Any]:
        """Загрузить статистику из файла"""
        if self.filename.exists():
            try:
                with open(self.filename, "r", encoding="utf-8") as f:
                    return json.load(f)
            except json.JSONDecodeError as e:
                logger.error(f"Failed to parse stats file: {e}")
                return self.default_stats()
            except Exception as e:
                logger.error(f"Failed to load stats: {e}")
                return self.default_stats()
        return self.default_stats()

    def default_stats(self) -> Dict[str, Any]:
        """Статистика по умолчанию"""
        return {
            "games_played": 0,
            "player1_wins": 0,
            "player2_wins": 0,
            "highest_score": 0,
            "total_goals": 0,
            "best_streak": 0,
            "last_played": None,
        }

    @log_exception
    def save_stats(self) -> None:
        """Сохранить статистику в файл"""
        try:
            self.filename.parent.mkdir(parents=True, exist_ok=True)
            with open(self.filename, "w", encoding="utf-8") as f:
                json.dump(self.stats, f, indent=2)
        except Exception as e:
            logger.error(f"Failed to save stats: {e}")

    def record_game(self, winner: int, player1_score: int, player2_score: int) -> None:
        """Записать результат игры"""
        self.stats["games_played"] += 1

        if winner == 1:
            self.stats["player1_wins"] += 1
        else:
            self.stats["player2_wins"] += 1

        self.stats["highest_score"] = max(self.stats["highest_score"], player1_score, player2_score)

        self.stats["last_played"] = datetime.now().isoformat()

        self.save_stats()

    def get_win_rate(self, player: int) -> float:
        """
        Получить процент побед игрока.

        Args:
            player: Номер игрока (1 или 2)

        Returns:
            float: Процент побед (0-100)
        """
        total = self.stats["player1_wins"] + self.stats["player2_wins"]
        if total == 0:
            return 0.0

        wins = self.stats[f"player{player}_wins"]
        return (wins / total) * 100

    def reset_stats(self) -> None:
        """Сбросить статистику"""
        self.stats = self.default_stats()
        self.save_stats()
