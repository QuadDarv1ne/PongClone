"""
Performance profiling utilities
"""
import cProfile
import functools
import io
import pstats
import time
from contextlib import contextmanager
from typing import Any, Callable, Optional

from PyPong.core.logger import logger


class PerformanceProfiler:
    """Performance profiler for game systems"""

    def __init__(self):
        self._profiler: Optional[cProfile.Profile] = None
        self._timings: dict[str, list[float]] = {}
        self._enabled = False

    def enable(self) -> None:
        """Enable profiling"""
        self._enabled = True
        logger.info("Performance profiling enabled")

    def disable(self) -> None:
        """Disable profiling"""
        self._enabled = False
        logger.info("Performance profiling disabled")

    def start(self) -> None:
        """Start profiling session"""
        if not self._enabled:
            return

        self._profiler = cProfile.Profile()
        self._profiler.enable()

    def stop(self, print_stats: bool = True, top_n: int = 20) -> Optional[str]:
        """
        Stop profiling and optionally print statistics

        Args:
            print_stats: Whether to print statistics
            top_n: Number of top functions to show

        Returns:
            Statistics as string if print_stats is True
        """
        if not self._enabled or not self._profiler:
            return None

        self._profiler.disable()

        if print_stats:
            s = io.StringIO()
            stats = pstats.Stats(self._profiler, stream=s)
            stats.sort_stats("cumulative")
            stats.print_stats(top_n)

            result = s.getvalue()
            logger.info(f"Profiling results:\n{result}")
            return result

        return None

    @contextmanager
    def profile_section(self, name: str):
        """
        Context manager for profiling a code section

        Usage:
            with profiler.profile_section('render'):
                # code to profile
                pass
        """
        if not self._enabled:
            yield
            return

        start_time = time.perf_counter()
        try:
            yield
        finally:
            elapsed = time.perf_counter() - start_time
            if name not in self._timings:
                self._timings[name] = []
            self._timings[name].append(elapsed)

    def get_timing_stats(self, name: str) -> dict[str, float]:
        """
        Get timing statistics for a profiled section

        Returns:
            Dictionary with min, max, avg, total times
        """
        if name not in self._timings or not self._timings[name]:
            return {}

        timings = self._timings[name]
        return {
            "count": len(timings),
            "min": min(timings),
            "max": max(timings),
            "avg": sum(timings) / len(timings),
            "total": sum(timings),
        }

    def get_all_stats(self) -> dict[str, dict[str, float]]:
        """Get timing statistics for all profiled sections"""
        return {name: self.get_timing_stats(name) for name in self._timings}

    def print_timing_report(self) -> None:
        """Print a formatted timing report"""
        if not self._timings:
            logger.info("No timing data collected")
            return

        report = "\n" + "=" * 60 + "\n"
        report += "Performance Timing Report\n"
        report += "=" * 60 + "\n"

        for name, stats in self.get_all_stats().items():
            report += f"\n{name}:\n"
            report += f"  Count: {stats['count']}\n"
            report += f"  Avg:   {stats['avg']*1000:.2f}ms\n"
            report += f"  Min:   {stats['min']*1000:.2f}ms\n"
            report += f"  Max:   {stats['max']*1000:.2f}ms\n"
            report += f"  Total: {stats['total']*1000:.2f}ms\n"

        report += "=" * 60 + "\n"
        logger.info(report)

    def reset(self) -> None:
        """Reset all timing data"""
        self._timings.clear()
        self._profiler = None


def profile(func: Optional[Callable] = None, *, print_stats: bool = True, top_n: int = 10) -> Callable:
    """
    Decorator for profiling functions

    Usage:
        @profile
        def my_function():
            pass

        @profile(print_stats=True, top_n=20)
        def another_function():
            pass
    """

    def decorator(f: Callable) -> Callable:
        @functools.wraps(f)
        def wrapper(*args: Any, **kwargs: Any) -> Any:
            profiler = cProfile.Profile()
            profiler.enable()

            try:
                result = f(*args, **kwargs)
                return result
            finally:
                profiler.disable()

                if print_stats:
                    s = io.StringIO()
                    stats = pstats.Stats(profiler, stream=s)
                    stats.sort_stats("cumulative")
                    stats.print_stats(top_n)

                    logger.info(f"Profile for {f.__name__}:\n{s.getvalue()}")

        return wrapper

    if func is None:
        return decorator
    else:
        return decorator(func)


def timeit(func: Optional[Callable] = None, *, log_result: bool = True) -> Callable:
    """
    Decorator for timing function execution

    Usage:
        @timeit
        def my_function():
            pass

        @timeit(log_result=False)
        def another_function():
            pass
    """

    def decorator(f: Callable) -> Callable:
        @functools.wraps(f)
        def wrapper(*args: Any, **kwargs: Any) -> Any:
            start_time = time.perf_counter()
            result = f(*args, **kwargs)
            elapsed = time.perf_counter() - start_time

            if log_result:
                logger.debug(f"{f.__name__} took {elapsed*1000:.2f}ms")

            return result

        return wrapper

    if func is None:
        return decorator
    else:
        return decorator(func)


# Global profiler instance
_profiler: Optional[PerformanceProfiler] = None


def get_profiler() -> PerformanceProfiler:
    """Get the global profiler instance"""
    global _profiler
    if _profiler is None:
        _profiler = PerformanceProfiler()
    return _profiler
