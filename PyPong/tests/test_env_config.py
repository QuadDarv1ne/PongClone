"""
Tests for environment configuration
"""
import pytest
import os
from pathlib import Path
from PyPong.core.env_config import EnvConfig


class TestEnvConfig:
    """Test suite for EnvConfig"""
    
    def test_get_from_os_env(self, monkeypatch):
        """Test getting values from OS environment"""
        monkeypatch.setenv('TEST_VAR', 'test_value')
        
        config = EnvConfig()
        assert config.get('TEST_VAR') == 'test_value'
    
    def test_get_with_default(self):
        """Test getting values with default"""
        config = EnvConfig()
        assert config.get('NONEXISTENT', 'default') == 'default'
    
    def test_type_casting_int(self, monkeypatch):
        """Test integer type casting"""
        monkeypatch.setenv('INT_VAR', '42')
        
        config = EnvConfig()
        assert config.get_int('INT_VAR') == 42
        assert isinstance(config.get_int('INT_VAR'), int)
    
    def test_type_casting_float(self, monkeypatch):
        """Test float type casting"""
        monkeypatch.setenv('FLOAT_VAR', '3.14')
        
        config = EnvConfig()
        assert config.get_float('FLOAT_VAR') == 3.14
        assert isinstance(config.get_float('FLOAT_VAR'), float)
    
    def test_type_casting_bool(self, monkeypatch):
        """Test boolean type casting"""
        test_cases = [
            ('true', True),
            ('True', True),
            ('1', True),
            ('yes', True),
            ('on', True),
            ('false', False),
            ('False', False),
            ('0', False),
            ('no', False),
            ('off', False),
        ]
        
        config = EnvConfig()
        for value, expected in test_cases:
            monkeypatch.setenv('BOOL_VAR', value)
            assert config.get_bool('BOOL_VAR') == expected
    
    def test_load_from_env_file(self, tmp_path):
        """Test loading from .env file"""
        env_file = tmp_path / ".env"
        env_file.write_text(
            "TEST_VAR=test_value\n"
            "INT_VAR=42\n"
            "# Comment line\n"
            "FLOAT_VAR=3.14\n"
        )
        
        config = EnvConfig(str(env_file))
        assert config.get('TEST_VAR') == 'test_value'
        assert config.get_int('INT_VAR') == 42
        assert config.get_float('FLOAT_VAR') == 3.14
    
    def test_env_file_priority(self, tmp_path, monkeypatch):
        """Test that OS environment has priority over .env file"""
        env_file = tmp_path / ".env"
        env_file.write_text("TEST_VAR=from_file\n")
        
        monkeypatch.setenv('TEST_VAR', 'from_os')
        
        config = EnvConfig(str(env_file))
        # OS environment should take priority
        assert config.get('TEST_VAR') == 'from_os'
    
    def test_invalid_type_casting(self, monkeypatch):
        """Test handling of invalid type casting"""
        monkeypatch.setenv('INVALID_INT', 'not_a_number')
        
        config = EnvConfig()
        # Should return default on casting error
        assert config.get_int('INVALID_INT', 0) == 0
    
    def test_missing_env_file(self):
        """Test handling of missing .env file"""
        config = EnvConfig('nonexistent.env')
        # Should not raise exception
        assert config.get('ANY_VAR', 'default') == 'default'
