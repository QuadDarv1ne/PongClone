"""
Tests for game state management
"""
import sys
from pathlib import Path
from unittest.mock import MagicMock, patch

import pytest

# Add parent directory to path
current_dir = Path(__file__).parent.parent
if str(current_dir.parent) not in sys.path:
    sys.path.insert(0, str(current_dir.parent))


class TestGameState:
    """Тесты для enum GameState"""

    def test_game_state_enum_exists(self):
        """Проверка существования enum GameState"""
        from PyPong.core.game_state import GameState

        assert GameState.MENU is not None
        assert GameState.PLAYING is not None
        assert GameState.PAUSED is not None
        assert GameState.GAME_OVER is not None

    def test_game_state_values(self):
        """Проверка значений GameState"""
        from PyPong.core.game_state import GameState

        states = [
            GameState.MENU,
            GameState.MODE_SELECT,
            GameState.PLAYING,
            GameState.PAUSED,
            GameState.GAME_OVER,
            GameState.STATS,
            GameState.SETTINGS,
            GameState.HELP,
        ]

        for state in states:
            assert state.value > 0


class TestGameStateManager:
    """Тесты для GameStateManager"""

    @pytest.fixture
    def mock_screen(self, mock_pygame):
        """Создать реальный экран для тестов"""
        return mock_pygame["screen"]

    @pytest.fixture
    def state_manager(self, mock_screen):
        """Создать GameStateManager для тестов"""
        from PyPong.core.game_state import GameStateManager

        return GameStateManager(mock_screen)

    def test_state_manager_creation(self, state_manager):
        """Создание GameStateManager"""
        assert state_manager.state.name == "MENU"
        assert state_manager.player1_score == 0
        assert state_manager.player2_score == 0

    def test_reset_scores(self, state_manager):
        """Сброс очков"""
        state_manager.player1_score = 5
        state_manager.player2_score = 3

        state_manager.reset_scores()

        assert state_manager.player1_score == 0
        assert state_manager.player2_score == 0
        assert state_manager.winner is None

    def test_add_score_player1(self, state_manager):
        """Добавление очка игроку 1"""
        state_manager.add_score(1)

        assert state_manager.player1_score == 1

    def test_add_score_player2(self, state_manager):
        """Добавление очка игроку 2"""
        state_manager.add_score(2)

        assert state_manager.player2_score == 1

    def test_add_score_wins_game(self, state_manager):
        """Победа при достижении WINNING_SCORE"""
        from PyPong.core.config import WINNING_SCORE

        for _ in range(WINNING_SCORE):
            state_manager.add_score(1)

        assert state_manager.winner == 1
        assert state_manager.state.name == "GAME_OVER"

    def test_set_difficulty(self, state_manager):
        """Установка сложности"""
        state_manager.set_difficulty("Hard")

        assert state_manager.difficulty == "Hard"

    def test_set_invalid_difficulty(self, state_manager):
        """Установка невалидной сложности"""
        initial_difficulty = state_manager.difficulty

        state_manager.set_difficulty("Invalid")

        assert state_manager.difficulty == initial_difficulty

    def test_draw_methods_exist(self, state_manager):
        """Проверка существования методов отрисовки"""
        assert hasattr(state_manager, "draw_menu")
        assert hasattr(state_manager, "draw_mode_select")
        assert hasattr(state_manager, "draw_pause")
        assert hasattr(state_manager, "draw_game_over")
        assert hasattr(state_manager, "draw_score")
        assert hasattr(state_manager, "draw_stats")
        assert hasattr(state_manager, "draw_help")


class TestGameStateTransitions:
    """Тесты для переходов между состояниями"""

    @pytest.fixture
    def state_manager(self, mock_pygame):
        """Создать GameStateManager для тестов"""
        from PyPong.core.game_state import GameStateManager

        mock_screen = mock_pygame["screen"]
        return GameStateManager(mock_screen)

    def test_menu_to_mode_select(self, state_manager):
        """Переход из меню в выбор режима"""
        from PyPong.core.game_state import GameState

        state_manager.state = GameState.MENU
        state_manager.state = GameState.MODE_SELECT

        assert state_manager.state.name == "MODE_SELECT"

    def test_mode_select_to_playing(self, state_manager):
        """Переход из выбора режима в игру"""
        from PyPong.core.game_state import GameState

        state_manager.state = GameState.MODE_SELECT
        state_manager.state = GameState.PLAYING

        assert state_manager.state.name == "PLAYING"

    def test_playing_to_paused(self, state_manager):
        """Переход из игры в паузу"""
        from PyPong.core.game_state import GameState

        state_manager.state = GameState.PLAYING
        state_manager.state = GameState.PAUSED

        assert state_manager.state.name == "PAUSED"

    def test_paused_to_menu(self, state_manager):
        """Переход из паузы в меню"""
        from PyPong.core.game_state import GameState

        state_manager.state = GameState.PAUSED
        state_manager.state = GameState.MENU

        assert state_manager.state.name == "MENU"

    def test_game_over_to_menu(self, state_manager):
        """Переход из конца игры в меню"""
        from PyPong.core.game_state import GameState

        state_manager.state = GameState.GAME_OVER
        state_manager.state = GameState.MENU

        assert state_manager.state.name == "MENU"
