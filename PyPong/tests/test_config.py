"""
Tests for configuration system
"""
import pytest
import json
from pathlib import Path
from PyPong.core.config_extended import Config, DEFAULT_CONFIG


class TestConfig:
    """Test suite for Config class"""
    
    def test_default_values(self):
        """Test that default values are loaded"""
        config = Config()
        
        assert config.window_width == 1024
        assert config.window_height == 720
        assert config.fps == 60
        assert config.winning_score == 5
    
    def test_get_method(self):
        """Test get method with dot notation"""
        config = Config()
        
        assert config.get('window_width') == 1024
        assert config.get('colors.white') == (255, 255, 255)
        assert config.get('nonexistent', 'default') == 'default'
    
    def test_set_method(self):
        """Test set method"""
        config = Config()
        
        config.set('window_width', 1920)
        assert config.window_width == 1920
        
        config.set('custom.nested.value', 42)
        assert config.get('custom.nested.value') == 42
    
    def test_properties(self):
        """Test property accessors"""
        config = Config()
        
        assert isinstance(config.window_width, int)
        assert isinstance(config.fps, int)
        assert isinstance(config.fullscreen, bool)
        assert isinstance(config.colors, dict)
        assert isinstance(config.difficulty_levels, dict)
    
    def test_difficulty_levels(self):
        """Test difficulty level configuration"""
        config = Config()
        
        assert 'Easy' in config.difficulty_levels
        assert 'Medium' in config.difficulty_levels
        assert 'Hard' in config.difficulty_levels
        
        easy = config.difficulty_levels['Easy']
        assert 'ai_speed' in easy
        assert 'ball_increase' in easy
    
    def test_save_and_load(self, tmp_path):
        """Test saving and loading configuration"""
        config_file = tmp_path / "test_config.json"
        
        config = Config()
        config.set('window_width', 1920)
        config.save(config_file)
        
        assert config_file.exists()
        
        # Load saved config
        with open(config_file, 'r') as f:
            saved_data = json.load(f)
        
        assert saved_data['window_width'] == 1920
    
    def test_merge_config(self):
        """Test merging user config with defaults"""
        config = Config()
        
        user_config = {
            'window_width': 1920,
            'colors': {
                'white': (200, 200, 200)
            }
        }
        
        config._merge_config(user_config)
        
        # User values should override
        assert config.window_width == 1920
        assert config.get('colors.white') == (200, 200, 200)
        
        # Other defaults should remain
        assert config.get('colors.black') == (0, 0, 0)
        assert config.fps == 60
