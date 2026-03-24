#!/usr/bin/env python3
"""
FPS Benchmark Runner for PyPong

Run this script to benchmark game performance on your hardware.
Results help determine optimal settings for your system.

Usage:
    python -m PyPong.tests.test_fps_benchmark
    # or
    python PyPong/tests/test_fps_benchmark.py
"""
import sys
import unittest

# Add parent directory to path
sys.path.insert(0, "..")

from PyPong.tests.test_fps_benchmark import FPSBenchmark, run_benchmark_summary


def main():
    """Run all FPS benchmarks and print summary"""
    run_benchmark_summary()

    # Create test suite
    loader = unittest.TestLoader()
    suite = loader.loadTestsFromTestCase(FPSBenchmark)

    # Run with verbosity
    runner = unittest.TextTestRunner(verbosity=2)
    result = runner.run(suite)

    # Print final summary
    print("\n" + "=" * 60)
    print("BENCHMARK COMPLETE")
    print("=" * 60)

    if result.wasSuccessful():
        print("All benchmarks PASSED")
        print("\nInterpretation:")
        print("- If all tests pass: Your system can handle max settings")
        print("- If some tests fail: Lower particle/trail settings")
        print("- Target: 60 FPS for smooth gameplay")
        print("- Minimum: 30 FPS for playable experience")
    else:
        print("Some benchmarks FAILED")
        print("\nRecommendations:")
        print("- Try running with 'low' performance profile")
        print("- Reduce particles and trails in settings")
        print("- Close other applications")

    print("=" * 60)

    return 0 if result.wasSuccessful() else 1


if __name__ == "__main__":
    sys.exit(main())
