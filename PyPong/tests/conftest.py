"""
Pytest configuration and fixtures for PyPong tests
"""
import pytest
from unittest.mock import MagicMock, patch
import sys
from pathlib import Path

# Add parent directory to path
current_dir = Path(__file__).parent.parent
if str(current_dir.parent) not in sys.path:
    sys.path.insert(0, str(current_dir.parent))


@pytest.fixture(scope="function")
def mock_pygame():
    """
    Фикстура для мокирования pygame.
    Предотвращает реальную инициализацию pygame в тестах.
    """
    with patch('pygame.init') as mock_init, \
         patch('pygame.quit') as mock_quit, \
         patch('pygame.display.set_mode') as mock_set_mode, \
         patch('pygame.display.set_caption') as mock_caption, \
         patch('pygame.time.Clock') as mock_clock, \
         patch('pygame.font.SysFont') as mock_font, \
         patch('pygame.mixer.init') as mock_mixer_init, \
         patch('pygame.mixer.music.load') as mock_music_load, \
         patch('pygame.mixer.Sound') as mock_sound, \
         patch('pygame.Surface') as mock_surface, \
         patch('pygame.Rect') as mock_rect, \
         patch('pygame.sprite.Group') as mock_group:
        
        # Настройка моков
        mock_surface_instance = MagicMock()
        mock_surface_instance.get_rect.return_value = MagicMock()
        mock_surface.return_value = mock_surface_instance
        
        mock_rect_instance = MagicMock()
        mock_rect_instance.clamp_ip = MagicMock()
        mock_rect.return_value = mock_rect_instance
        
        mock_group_instance = MagicMock()
        mock_group_instance.__len__ = MagicMock(return_value=0)
        mock_group_instance.__iter__ = MagicMock(return_value=iter([]))
        mock_group.return_value = mock_group_instance
        
        mock_font_instance = MagicMock()
        mock_font_instance.render = MagicMock(return_value=MagicMock())
        mock_font.return_value = mock_font_instance
        
        mock_clock_instance = MagicMock()
        mock_clock_instance.tick = MagicMock()
        mock_clock.return_value = mock_clock_instance
        
        yield {
            'init': mock_init,
            'quit': mock_quit,
            'set_mode': mock_set_mode,
            'caption': mock_caption,
            'clock': mock_clock,
            'font': mock_font,
            'mixer_init': mock_mixer_init,
            'music_load': mock_music_load,
            'sound': mock_sound,
            'surface': mock_surface,
            'rect': mock_rect,
            'group': mock_group,
        }


@pytest.fixture
def mock_logger():
    """Фикстура для мокирования логгера"""
    with patch('PyPong.core.logger.logger') as mock_logger:
        yield mock_logger


@pytest.fixture
def mock_settings():
    """Фикстура для мокирования настроек"""
    settings_mock = MagicMock()
    settings_mock.get = MagicMock(side_effect=lambda key, default=None: {
        'music_volume': 0.5,
        'sfx_volume': 0.7,
        'fullscreen': False,
        'theme': 'classic',
        'touch_controls': False,
        'show_fps': False,
    }.get(key, default))
    settings_mock.set = MagicMock()
    settings_mock.update = MagicMock()
    settings_mock.force_save = MagicMock()
    yield settings_mock


@pytest.fixture
def mock_audio():
    """Фикстура для мокирования аудио менеджера"""
    audio_mock = MagicMock()
    audio_mock.sounds = {
        'beep': MagicMock(),
        'score': MagicMock(),
        'powerup': MagicMock(),
    }
    audio_mock.play_music = MagicMock()
    audio_mock.stop_music = MagicMock()
    audio_mock.play_sound = MagicMock()
    yield audio_mock


@pytest.fixture
def mock_stats():
    """Фикстура для мокирования статистики"""
    stats_mock = MagicMock()
    stats_mock.stats = {
        'games_played': 0,
        'player1_wins': 0,
        'player2_wins': 0,
        'highest_score': 0,
        'total_goals': 0,
        'best_streak': 0,
        'last_played': None,
    }
    stats_mock.record_game = MagicMock()
    stats_mock.get_win_rate = MagicMock(return_value=0.0)
    stats_mock.reset_stats = MagicMock()
    yield stats_mock


@pytest.fixture
def mock_gamepad():
    """Фикстура для мокирования геймпада"""
    gamepad_mock = MagicMock()
    gamepad_mock.has_gamepad = MagicMock(return_value=False)
    gamepad_mock.get_input = MagicMock(return_value={
        'up': False,
        'down': False,
    })
    yield gamepad_mock


@pytest.fixture
def mock_touch_controls():
    """Фикстура для мокирования сенсорного управления"""
    touch_mock = MagicMock()
    touch_mock.handle_touch = MagicMock()
    touch_mock.get_input = MagicMock(return_value={
        'up': False,
        'down': False,
    })
    touch_mock.draw = MagicMock()
    yield touch_mock


@pytest.fixture
def mock_adaptive_screen():
    """Фикстура для мокирования адаптивного экрана"""
    screen_mock = MagicMock()
    screen_mock.update_resolution = MagicMock()
    screen_mock.get_scaled_surface = MagicMock(side_effect=lambda x: x)
    yield screen_mock


@pytest.fixture
def sample_game_state():
    """Фикстура с тестовым состоянием игры"""
    return {
        'state': 'MENU',
        'player1_score': 0,
        'player2_score': 0,
        'winner': None,
        'difficulty': 'Medium',
        'game_mode': 'ai',
        'tournament_mode': False,
    }
