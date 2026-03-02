"""
Tests for performance profiler
"""
import pytest
import time
from PyPong.core.profiler import PerformanceProfiler, profile, timeit


class TestPerformanceProfiler:
    """Test suite for PerformanceProfiler"""
    
    def setup_method(self):
        """Setup for each test"""
        self.profiler = PerformanceProfiler()
    
    def test_enable_disable(self):
        """Test enabling and disabling profiler"""
        assert not self.profiler._enabled
        
        self.profiler.enable()
        assert self.profiler._enabled
        
        self.profiler.disable()
        assert not self.profiler._enabled
    
    def test_profile_section(self):
        """Test profiling a code section"""
        self.profiler.enable()
        
        with self.profiler.profile_section('test_section'):
            time.sleep(0.01)  # 10ms
        
        stats = self.profiler.get_timing_stats('test_section')
        assert stats['count'] == 1
        assert stats['avg'] >= 0.01  # At least 10ms
    
    def test_multiple_sections(self):
        """Test profiling multiple sections"""
        self.profiler.enable()
        
        with self.profiler.profile_section('section1'):
            time.sleep(0.01)
        
        with self.profiler.profile_section('section2'):
            time.sleep(0.02)
        
        stats1 = self.profiler.get_timing_stats('section1')
        stats2 = self.profiler.get_timing_stats('section2')
        
        assert stats1['avg'] < stats2['avg']
    
    def test_repeated_sections(self):
        """Test profiling same section multiple times"""
        self.profiler.enable()
        
        for _ in range(3):
            with self.profiler.profile_section('repeated'):
                time.sleep(0.01)
        
        stats = self.profiler.get_timing_stats('repeated')
        assert stats['count'] == 3
    
    def test_get_all_stats(self):
        """Test getting all statistics"""
        self.profiler.enable()
        
        with self.profiler.profile_section('section1'):
            pass
        
        with self.profiler.profile_section('section2'):
            pass
        
        all_stats = self.profiler.get_all_stats()
        assert 'section1' in all_stats
        assert 'section2' in all_stats
    
    def test_reset(self):
        """Test resetting profiler data"""
        self.profiler.enable()
        
        with self.profiler.profile_section('test'):
            pass
        
        assert len(self.profiler._timings) > 0
        
        self.profiler.reset()
        assert len(self.profiler._timings) == 0
    
    def test_disabled_profiler(self):
        """Test that disabled profiler doesn't collect data"""
        # Profiler is disabled by default
        with self.profiler.profile_section('test'):
            pass
        
        stats = self.profiler.get_timing_stats('test')
        assert stats == {}


class TestProfileDecorator:
    """Test suite for profile decorator"""
    
    def test_profile_decorator(self):
        """Test profile decorator on function"""
        @profile(print_stats=False)
        def test_function():
            return sum(range(1000))
        
        result = test_function()
        assert result == 499500
    
    def test_timeit_decorator(self):
        """Test timeit decorator on function"""
        @timeit(log_result=False)
        def test_function():
            time.sleep(0.01)
            return 42
        
        result = test_function()
        assert result == 42
