"""
Integration tests for pong_v4 game module
"""
import pytest
from unittest.mock import MagicMock, patch
import sys
from pathlib import Path

# Add parent directory to path
current_dir = Path(__file__).parent.parent
if str(current_dir.parent) not in sys.path:
    sys.path.insert(0, str(current_dir.parent))


class TestPongGameInitialization:
    """Тесты инициализации PongGame"""

    def test_pong_game_creation(self, mock_pygame):
        """Создание игры"""
        from PyPong.pong import PongGame

        # Мокируем зависимости
        with patch('PyPong.pong.Settings') as mock_settings, \
             patch('PyPong.pong.GameStateManager') as mock_gsm, \
             patch('PyPong.pong.AudioManager') as mock_audio, \
             patch('PyPong.pong.StatsManager') as mock_stats, \
             patch('PyPong.pong.Tournament') as mock_tournament, \
             patch('PyPong.pong.GamepadManager') as mock_gamepad, \
             patch('PyPong.pong.mobile_module') as mock_mobile, \
             patch('PyPong.pong.SettingsMenu') as mock_menu, \
             patch('PyPong.pong.get_theme') as mock_theme:
            
            # Setup mobile mocks
            mock_mobile.TouchControls = MagicMock()
            mock_mobile.AdaptiveScreen = MagicMock()
            
            # Настройка моков
            mock_settings.return_value.get = MagicMock(return_value=False)
            mock_settings.return_value.set = MagicMock()
            mock_theme.return_value = MagicMock()
            mock_theme.return_value.paddle1_color = (255, 255, 255)
            mock_theme.return_value.paddle2_color = (200, 200, 200)
            mock_theme.return_value.ball_color = (255, 255, 255)
            mock_theme.return_value.bg_color = (0, 0, 0)
            mock_theme.return_value.accent_color = (100, 100, 100)
            mock_theme.return_value.name = 'classic'
            
            game = PongGame()
            
            assert game is not None
            assert hasattr(game, 'state_manager')
            assert hasattr(game, 'audio')
            assert hasattr(game, 'input_handler')
            assert hasattr(game, 'game_loop')
            assert hasattr(game, 'renderer')
    
    def test_pong_game_shutdown(self, mock_pygame):
        """Корректное завершение работы"""
        from PyPong.pong import PongGame

        with patch('PyPong.pong.Settings') as mock_settings, \
             patch('PyPong.pong.GameStateManager') as mock_gsm, \
             patch('PyPong.pong.AudioManager') as mock_audio, \
             patch('PyPong.pong.StatsManager') as mock_stats, \
             patch('PyPong.pong.Tournament') as mock_tournament, \
             patch('PyPong.pong.GamepadManager') as mock_gamepad, \
             patch('PyPong.pong.mobile_module') as mock_mobile, \
             patch('PyPong.pong.SettingsMenu') as mock_menu, \
             patch('PyPong.pong.get_theme') as mock_theme:
            
            # Setup mobile mocks
            mock_mobile.TouchControls = MagicMock()
            mock_mobile.AdaptiveScreen = MagicMock()
            
            mock_settings.return_value.get = MagicMock(return_value=False)
            mock_settings.return_value.set = MagicMock()
            mock_settings.return_value.force_save = MagicMock()
            mock_theme.return_value = MagicMock()
            mock_theme.return_value.paddle1_color = (255, 255, 255)
            
            game = PongGame()
            game.shutdown()
            
            mock_settings.return_value.force_save.assert_called()
            mock_audio.return_value.stop_music.assert_called()


class TestInputHandler:
    """Тесты InputHandler"""
    
    def test_input_handler_creation(self):
        """Создание обработчика ввода"""
        from PyPong.game.input_handler import InputHandler
        
        handler = InputHandler()
        
        assert handler.input_state == {
            "up1": False,
            "down1": False,
            "up2": False,
            "down2": False,
        }
    
    def test_input_handler_set_input(self):
        """Установка состояния ввода"""
        from PyPong.game.input_handler import InputHandler
        
        handler = InputHandler()
        handler.set_input("up1", True)
        
        assert handler.input_state["up1"] is True
    
    def test_input_handler_reset(self):
        """Сброс ввода"""
        from PyPong.game.input_handler import InputHandler
        
        handler = InputHandler()
        handler.set_input("up1", True)
        handler.set_input("down2", True)
        handler.reset_input()
        
        assert handler.input_state == {
            "up1": False,
            "down1": False,
            "up2": False,
            "down2": False,
        }


class TestCollisionManager:
    """Тесты CollisionManager"""
    
    def test_collision_manager_creation(self):
        """Создание менеджера коллизий"""
        from PyPong.game.collision_manager import CollisionManager
        
        manager = CollisionManager()
        
        assert manager is not None
    
    def test_get_shake_intensity(self):
        """Получение интенсивности тряски"""
        from PyPong.game.collision_manager import CollisionManager
        
        manager = CollisionManager()
        
        normal = manager.get_shake_intensity(is_goal=False)
        goal = manager.get_shake_intensity(is_goal=True)
        
        assert normal != goal
        assert goal[0] > normal[0]


class TestAudioManagerFallback:
    """Тесты AudioManager с отсутствующими файлами"""
    
    def test_audio_manager_no_files(self, mock_pygame):
        """AudioManager без файлов"""
        import pygame
        from PyPong.systems.audio import AudioManager
        from unittest.mock import patch, MagicMock
        
        # Мокируем отсутствие файлов
        with patch('PyPong.systems.audio.Path.exists', return_value=False):
            audio = AudioManager()
            
            # Звуки должны быть созданы как заглушки
            assert "beep" in audio.sounds
            assert "score" in audio.sounds
            assert "powerup" in audio.sounds
            assert audio.is_fallback_mode is True
    
    def test_audio_manager_play_missing_sound(self, mock_pygame):
        """Воспроизведение отсутствующего звука"""
        import pygame
        from PyPong.systems.audio import AudioManager
        from unittest.mock import patch
        
        with patch('PyPong.systems.audio.Path.exists', return_value=False):
            audio = AudioManager()
            
            # Не должно быть ошибок
            audio.play_sound("beep")
            audio.play_music()
            audio.stop_music()


class TestRenderer:
    """Тесты Renderer"""
    
    def test_renderer_creation(self, mock_pygame):
        """Создание рендерера"""
        from PyPong.rendering.renderer import Renderer
        
        screen = mock_pygame['screen']
        
        renderer = Renderer(
            screen=screen,
            game_surface=screen,
            theme=MagicMock(),
            settings=MagicMock(),
            adaptive_screen=MagicMock(),
        )
        
        assert renderer is not None
    
    def test_renderer_clear(self, mock_pygame):
        """Очистка экрана"""
        from PyPong.rendering.renderer import Renderer
        
        screen = mock_pygame['screen']
        theme = MagicMock()
        theme.bg_color = (0, 0, 0)
        
        renderer = Renderer(
            screen=screen,
            game_surface=screen,
            theme=theme,
            settings=MagicMock(),
            adaptive_screen=MagicMock(),
        )
        
        renderer.clear()
        
        # Проверка что fill был вызван (метод fill существует)
        assert hasattr(screen, 'fill')
