"""Tests for GameStateManager"""
import unittest
from unittest.mock import MagicMock

import pygame

from PyPong.core.game_state import GameState, GameStateManager


class TestGameStateManager(unittest.TestCase):
    """Test game state manager functionality"""

    def setUp(self) -> None:
        """Set up test fixtures"""
        pygame.init()
        self.screen = pygame.Surface((1024, 720))
        self.state_manager = GameStateManager(self.screen)

    def tearDown(self) -> None:
        """Clean up"""
        pygame.quit()

    def test_initial_state(self) -> None:
        """Test initial game state"""
        self.assertEqual(self.state_manager.state, GameState.MENU)
        self.assertEqual(self.state_manager.player1_score, 0)
        self.assertEqual(self.state_manager.player2_score, 0)
        self.assertIsNone(self.state_manager.winner)
        self.assertEqual(self.state_manager.difficulty, "Medium")
        self.assertEqual(self.state_manager.game_mode, "ai")
        self.assertFalse(self.state_manager.tournament_mode)

    def test_reset_scores(self) -> None:
        """Test score reset"""
        self.state_manager.player1_score = 3
        self.state_manager.player2_score = 2
        self.state_manager.winner = 1

        self.state_manager.reset_scores()

        self.assertEqual(self.state_manager.player1_score, 0)
        self.assertEqual(self.state_manager.player2_score, 0)
        self.assertIsNone(self.state_manager.winner)

    def test_add_score_player1(self) -> None:
        """Test adding score to player 1"""
        initial_score = self.state_manager.player1_score
        self.state_manager.add_score(1)
        self.assertEqual(self.state_manager.player1_score, initial_score + 1)

    def test_add_score_player2(self) -> None:
        """Test adding score to player 2"""
        initial_score = self.state_manager.player2_score
        self.state_manager.add_score(2)
        self.assertEqual(self.state_manager.player2_score, initial_score + 1)

    def test_add_score_winning_score(self) -> None:
        """Test reaching winning score"""
        # Set score to one below winning
        self.state_manager.player1_score = 4
        self.state_manager.state = GameState.PLAYING

        # Add winning score
        self.state_manager.add_score(1)

        self.assertEqual(self.state_manager.winner, 1)
        self.assertEqual(self.state_manager.state, GameState.GAME_OVER)

    def test_add_score_winning_score_player2(self) -> None:
        """Test player 2 reaching winning score"""
        self.state_manager.player2_score = 4
        self.state_manager.state = GameState.PLAYING

        self.state_manager.add_score(2)

        self.assertEqual(self.state_manager.winner, 2)
        self.assertEqual(self.state_manager.state, GameState.GAME_OVER)

    def test_set_difficulty(self) -> None:
        """Test setting difficulty"""
        self.state_manager.set_difficulty("Hard")
        self.assertEqual(self.state_manager.difficulty, "Hard")

    def test_set_difficulty_invalid(self) -> None:
        """Test setting invalid difficulty"""
        self.state_manager.set_difficulty("Invalid")
        # Should keep previous value
        self.assertEqual(self.state_manager.difficulty, "Medium")

    def test_state_transitions(self) -> None:
        """Test state transitions"""
        # Menu to mode select
        self.state_manager.state = GameState.MODE_SELECT
        self.assertEqual(self.state_manager.state, GameState.MODE_SELECT)

        # Mode select to playing
        self.state_manager.state = GameState.PLAYING
        self.assertEqual(self.state_manager.state, GameState.PLAYING)

        # Playing to paused
        self.state_manager.state = GameState.PAUSED
        self.assertEqual(self.state_manager.state, GameState.PAUSED)

        # Paused to playing
        self.state_manager.state = GameState.PLAYING
        self.assertEqual(self.state_manager.state, GameState.PLAYING)

    def test_net_surface_created(self) -> None:
        """Test net surface is pre-rendered"""
        self.assertIsNotNone(self.state_manager._net_surface)
        self.assertIsInstance(self.state_manager._net_surface, pygame.Surface)

    def test_fonts_initialized(self) -> None:
        """Test fonts are initialized"""
        self.assertIsNotNone(self.state_manager.title_font)
        self.assertIsNotNone(self.state_manager.menu_font)
        self.assertIsNotNone(self.state_manager.score_font)
        self.assertIsNotNone(self.state_manager.small_font)


if __name__ == "__main__":
    unittest.main()
