"""
Tests for Event Bus system
"""
import pytest

from PyPong.core.event_bus import EventBus, EventData, GameEvent


class TestEventBus:
    """Test suite for EventBus"""

    def setup_method(self):
        """Setup for each test"""
        self.event_bus = EventBus()
        self.callback_called = False
        self.callback_data = None

    def test_subscribe_and_publish(self):
        """Test basic subscribe and publish"""

        def callback(data):
            self.callback_called = True
            self.callback_data = data

        self.event_bus.subscribe(GameEvent.GOAL_SCORED, callback)
        self.event_bus.publish(GameEvent.GOAL_SCORED, {"player": 1})

        assert self.callback_called
        assert self.callback_data == {"player": 1}

    def test_multiple_subscribers(self):
        """Test multiple subscribers to same event"""
        call_count = []

        def callback1(data):
            call_count.append(1)

        def callback2(data):
            call_count.append(2)

        self.event_bus.subscribe(GameEvent.GOAL_SCORED, callback1)
        self.event_bus.subscribe(GameEvent.GOAL_SCORED, callback2)
        self.event_bus.publish(GameEvent.GOAL_SCORED)

        assert len(call_count) == 2
        assert 1 in call_count
        assert 2 in call_count

    def test_unsubscribe(self):
        """Test unsubscribing from events"""

        def callback(data):
            self.callback_called = True

        self.event_bus.subscribe(GameEvent.GOAL_SCORED, callback)
        self.event_bus.unsubscribe(GameEvent.GOAL_SCORED, callback)
        self.event_bus.publish(GameEvent.GOAL_SCORED)

        assert not self.callback_called

    def test_event_history(self):
        """Test event history tracking"""
        self.event_bus.publish(GameEvent.GOAL_SCORED, {"player": 1})
        self.event_bus.publish(GameEvent.GOAL_SCORED, {"player": 2})

        history = self.event_bus.get_history(GameEvent.GOAL_SCORED)
        assert len(history) == 2
        assert history[0].data == {"player": 1}
        assert history[1].data == {"player": 2}

    def test_disable_enable(self):
        """Test disabling and enabling event bus"""

        def callback(data):
            self.callback_called = True

        self.event_bus.subscribe(GameEvent.GOAL_SCORED, callback)
        self.event_bus.disable()
        self.event_bus.publish(GameEvent.GOAL_SCORED)

        assert not self.callback_called

        self.event_bus.enable()
        self.event_bus.publish(GameEvent.GOAL_SCORED)

        assert self.callback_called

    def test_error_handling(self):
        """Test that errors in callbacks don't break event bus"""

        def bad_callback(data):
            raise ValueError("Test error")

        def good_callback(data):
            self.callback_called = True

        self.event_bus.subscribe(GameEvent.GOAL_SCORED, bad_callback)
        self.event_bus.subscribe(GameEvent.GOAL_SCORED, good_callback)

        # Should not raise exception
        self.event_bus.publish(GameEvent.GOAL_SCORED)

        # Good callback should still be called
        assert self.callback_called

    def test_listener_count(self):
        """Test getting listener counts"""

        def callback1(data):
            pass

        def callback2(data):
            pass

        self.event_bus.subscribe(GameEvent.GOAL_SCORED, callback1)
        self.event_bus.subscribe(GameEvent.GOAL_SCORED, callback2)

        assert self.event_bus.get_listener_count(GameEvent.GOAL_SCORED) == 2
        assert self.event_bus.get_listener_count(GameEvent.GAME_START) == 0

    def test_clear_listeners(self):
        """Test clearing listeners"""

        def callback(data):
            pass

        self.event_bus.subscribe(GameEvent.GOAL_SCORED, callback)
        self.event_bus.subscribe(GameEvent.GAME_START, callback)

        self.event_bus.clear_listeners(GameEvent.GOAL_SCORED)

        assert self.event_bus.get_listener_count(GameEvent.GOAL_SCORED) == 0
        assert self.event_bus.get_listener_count(GameEvent.GAME_START) == 1
