"""Tests for auto-detect module"""
import os
import pytest
import pygame

from PyPong.core.auto_detect import (
    detect_performance_profile,
    _detect_memory_mb,
    _classify_profile,
    get_recommended_settings,
)
from PyPong.core.config import PERFORMANCE_PROFILES


class TestPerformanceProfile:
    """Test performance profile detection"""

    def test_detect_performance_profile_returns_valid_profile(self):
        """Detection should return a valid profile name"""
        result = detect_performance_profile()
        assert "profile" in result
        assert result["profile"] in PERFORMANCE_PROFILES
        assert "cpu_count" in result
        assert result["cpu_count"] >= 1

    def test_detect_performance_profile_returns_memory(self):
        """Detection should return memory in MB"""
        result = detect_performance_profile()
        assert "memory_mb" in result
        assert result["memory_mb"] > 0

    def test_classify_profile_low_cpu(self):
        """1 core should return low profile"""
        assert _classify_profile(1, 4096) == "low"

    def test_classify_profile_medium(self):
        """2-4 cores with 4GB+ should return medium"""
        assert _classify_profile(2, 4096) == "medium"
        assert _classify_profile(4, 4096) == "medium"

    def test_classify_profile_high(self):
        """4+ cores with 8GB+ should return high"""
        assert _classify_profile(4, 8192) == "high"
        assert _classify_profile(6, 8192) == "high"

    def test_classify_profile_ultra(self):
        """8+ cores with 16GB+ should return ultra"""
        assert _classify_profile(8, 16384) == "ultra"
        assert _classify_profile(12, 32768) == "ultra"

    def test_detect_memory_mb_returns_positive(self):
        """Memory detection should return positive value"""
        memory = _detect_memory_mb()
        assert memory > 0
        assert isinstance(memory, int)


class TestRecommendedSettings:
    """Test get_recommended_settings coordinator"""

    def test_returns_expected_keys(self):
        """Should return all expected setting keys"""
        result = get_recommended_settings()
        assert "width" in result
        assert "height" in result
        assert "profile" in result
        assert "max_particles" in result
        assert "max_trails" in result
        assert "target_fps" in result
        assert "enable_shake" in result
        assert "enable_effects" in result

    def test_profile_matches_performance_values(self):
        """Profile values should match the corresponding PERFORMANCE_PROFILE"""
        result = get_recommended_settings()
        profile = PERFORMANCE_PROFILES[result["profile"]]
        assert result["max_particles"] == profile["max_particles"]
        assert result["max_trails"] == profile["max_trails"]
        assert result["target_fps"] == profile["target_fps"]
        assert result["enable_shake"] == profile["enable_shake"]
        assert result["enable_effects"] == profile["enable_effects"]

    def test_resolution_is_reasonable(self):
        """Detected resolution should be within reasonable bounds"""
        result = get_recommended_settings()
        assert 800 <= result["width"] <= 1920
        assert 600 <= result["height"] <= 1080


class TestSettingsFirstLaunch:
    """Test Settings.is_first_launch"""

    def test_is_first_launch_returns_bool(self, tmp_path):
        """is_first_launch should return True when file doesn't exist"""
        from PyPong.systems.settings import Settings

        # Create settings with a non-existent file path
        test_file = tmp_path / "test_settings.json"
        settings = Settings.__new__(Settings)
        settings.filename = test_file
        settings.data = {}
        settings._pending_save = False
        settings._save_timer = 0
        settings._SAVE_DELAY = 1000

        assert settings.is_first_launch() is True

        # Create the file
        test_file.write_text("{}")
        assert settings.is_first_launch() is False
