"""
Event Bus for decoupled communication between game systems
"""
from dataclasses import dataclass
from enum import Enum, auto
from typing import Any, Callable, Dict, List, Optional

from PyPong.core.logger import logger


class GameEvent(Enum):
    """Game event types"""

    # Game state events
    GAME_START = auto()
    GAME_PAUSE = auto()
    GAME_RESUME = auto()
    GAME_OVER = auto()
    ROUND_START = auto()
    ROUND_END = auto()

    # Gameplay events
    BALL_HIT_PADDLE = auto()
    BALL_HIT_WALL = auto()
    GOAL_SCORED = auto()
    COMBO_ACHIEVED = auto()

    # Power-up events
    POWERUP_SPAWNED = auto()
    POWERUP_COLLECTED = auto()
    POWERUP_ACTIVATED = auto()
    POWERUP_EXPIRED = auto()

    # Achievement events
    ACHIEVEMENT_UNLOCKED = auto()
    CHALLENGE_COMPLETED = auto()

    # UI events
    MENU_OPENED = auto()
    MENU_CLOSED = auto()
    SETTINGS_CHANGED = auto()
    THEME_CHANGED = auto()

    # Audio events
    MUSIC_STARTED = auto()
    MUSIC_STOPPED = auto()
    SOUND_PLAYED = auto()

    # System events
    ERROR_OCCURRED = auto()
    PERFORMANCE_WARNING = auto()


@dataclass
class EventData:
    """Container for event data"""

    event_type: GameEvent
    data: Dict[str, Any]
    source: Optional[str] = None
    timestamp: Optional[float] = None

    def __post_init__(self):
        if self.timestamp is None:
            import time

            self.timestamp = time.time()


class EventBus:
    """
    Central event bus for game-wide communication.
    Allows systems to communicate without direct dependencies.

    Usage:
        # Subscribe to events
        event_bus.subscribe(GameEvent.GOAL_SCORED, on_goal_scored)

        # Publish events
        event_bus.publish(GameEvent.GOAL_SCORED, {'player': 1, 'score': 5})

        # Unsubscribe
        event_bus.unsubscribe(GameEvent.GOAL_SCORED, on_goal_scored)
    """

    def __init__(self):
        self._listeners: Dict[GameEvent, List[Callable]] = {}
        self._event_history: List[EventData] = []
        self._max_history = 100
        self._enabled = True

    def subscribe(self, event_type: GameEvent, callback: Callable[[Dict[str, Any]], None]) -> None:
        """
        Subscribe to an event type

        Args:
            event_type: Type of event to listen for
            callback: Function to call when event occurs (receives event data dict)
        """
        if event_type not in self._listeners:
            self._listeners[event_type] = []

        if callback not in self._listeners[event_type]:
            self._listeners[event_type].append(callback)
            logger.debug(f"Subscribed to {event_type.name}: {callback.__name__}")

    def unsubscribe(self, event_type: GameEvent, callback: Callable) -> None:
        """
        Unsubscribe from an event type

        Args:
            event_type: Type of event to stop listening for
            callback: Function to remove from listeners
        """
        if event_type in self._listeners:
            try:
                self._listeners[event_type].remove(callback)
                logger.debug(f"Unsubscribed from {event_type.name}: {callback.__name__}")
            except ValueError:
                pass

    def publish(
        self, event_type: GameEvent, data: Optional[Dict[str, Any]] = None, source: Optional[str] = None
    ) -> None:
        """
        Publish an event to all subscribers

        Args:
            event_type: Type of event to publish
            data: Optional data to pass to listeners
            source: Optional source identifier
        """
        if not self._enabled:
            return

        data = data or {}
        event_data = EventData(event_type=event_type, data=data, source=source)

        # Store in history
        self._event_history.append(event_data)
        if len(self._event_history) > self._max_history:
            self._event_history.pop(0)

        # Notify listeners
        listeners = self._listeners.get(event_type, [])
        logger.debug(f"Publishing {event_type.name} to {len(listeners)} listeners")

        for callback in listeners:
            try:
                callback(data)
            except Exception as e:
                logger.error(f"Error in event listener {callback.__name__} for {event_type.name}: {e}", exc_info=True)

    def clear_listeners(self, event_type: Optional[GameEvent] = None) -> None:
        """
        Clear all listeners for an event type, or all listeners if no type specified

        Args:
            event_type: Optional event type to clear listeners for
        """
        if event_type:
            self._listeners[event_type] = []
        else:
            self._listeners.clear()

    def get_history(self, event_type: Optional[GameEvent] = None, limit: int = 10) -> List[EventData]:
        """
        Get recent event history

        Args:
            event_type: Optional filter by event type
            limit: Maximum number of events to return

        Returns:
            List of recent events
        """
        if event_type:
            filtered = [e for e in self._event_history if e.event_type == event_type]
            return filtered[-limit:]
        return self._event_history[-limit:]

    def enable(self) -> None:
        """Enable event publishing"""
        self._enabled = True

    def disable(self) -> None:
        """Disable event publishing (for testing or performance)"""
        self._enabled = False

    def get_listener_count(self, event_type: GameEvent) -> int:
        """Get number of listeners for an event type"""
        return len(self._listeners.get(event_type, []))

    def get_all_listeners(self) -> Dict[GameEvent, int]:
        """Get count of listeners for all event types"""
        return {event_type: len(listeners) for event_type, listeners in self._listeners.items()}


# Global event bus instance
_event_bus: Optional[EventBus] = None


def get_event_bus() -> EventBus:
    """Get the global event bus instance"""
    global _event_bus
    if _event_bus is None:
        _event_bus = EventBus()
    return _event_bus


def reset_event_bus() -> None:
    """Reset the global event bus (useful for testing)"""
    global _event_bus
    _event_bus = EventBus()
