"""
FPS Benchmark tests for performance verification

This module provides benchmark tests to measure frame rate performance
on different hardware configurations.
"""
import time
import unittest
from typing import Any, Dict, List

import pygame

from PyPong.core.config import (
    PERFORMANCE_PROFILES,
    WINDOW_HEIGHT,
    WINDOW_WIDTH,
)
from PyPong.core.entities import Ball, Paddle
from PyPong.core.entity_pools import get_ball_pool
from PyPong.ui.effects import ParticlePool, Trail


class FPSBenchmark(unittest.TestCase):
    """FPS benchmark tests"""

    def setUp(self) -> None:
        """Set up test fixtures"""
        pygame.init()
        pygame.display.set_mode((WINDOW_WIDTH, WINDOW_HEIGHT), pygame.HIDDEN)
        self.clock = pygame.time.Clock()

    def tearDown(self) -> None:
        """Clean up"""
        pygame.quit()

    def _run_simulation(
        self,
        duration_seconds: float = 5.0,
        num_balls: int = 1,
        num_particles: int = 0,
        num_trails: int = 0,
    ) -> Dict[str, float]:
        """
        Run game simulation and measure FPS

        Args:
            duration_seconds: How long to run the simulation
            num_balls: Number of balls to simulate
            num_particles: Number of particle emitters
            num_trails: Number of trails to render

        Returns:
            Dictionary with FPS statistics
        """
        # Create game objects
        paddle1 = Paddle(1, is_ai=False)
        paddle2 = Paddle(2, is_ai=True)
        balls = [get_ball_pool().acquire() for _ in range(num_balls)]

        # Create effects
        particles = ParticlePool(max_size=50) if num_particles > 0 else None
        trails = pygame.sprite.Group()

        # Create surface for rendering
        surface = pygame.Surface((WINDOW_WIDTH, WINDOW_HEIGHT))

        # Run simulation - use frame counting for accurate measurement
        frame_count = 0
        frame_times: List[float] = []
        start_time = time.time()

        while time.time() - start_time < duration_seconds:
            frame_start = time.perf_counter()

            # Process events
            for event in pygame.event.get():
                if event.type == pygame.QUIT:
                    break

            # Update game objects
            paddle1.move(False, False, 360)  # AI follows ball
            paddle2.move(False, False, 360)

            for ball in balls:
                ball.move()
                ball.bounce_wall()

                # Spawn particles occasionally
                if particles and time.time() * 1000 % 500 < 50:
                    particles.emit(int(ball.rect.centerx), int(ball.rect.centery), (255, 255, 255), 4)

                # Spawn trails occasionally
                if trails and time.time() * 1000 % 200 < 50:
                    trail = Trail(int(ball.rect.centerx), int(ball.rect.centery))
                    trails.add(trail)

            # Update effects
            if particles:
                particles.update()
            if trails:
                trails.update()

            # Render
            surface.fill((0, 0, 0))
            if trails:
                trails.draw(surface)
            pygame.sprite.Group(paddle1, paddle2, *balls).draw(surface)
            if particles:
                particles.draw(surface)

            # Force display update (even with HIDDEN display)
            pygame.display.flip()

            # Measure frame time
            frame_time = (time.perf_counter() - frame_start) * 1000  # ms
            frame_times.append(frame_time)
            frame_count += 1

        # Return to pool
        for ball in balls:
            get_ball_pool().release(ball)

        # Calculate statistics from frame times
        total_time = time.time() - start_time
        if frame_times and total_time > 0:
            avg_frame_time = sum(frame_times) / len(frame_times)
            min_frame_time = min(frame_times)
            max_frame_time = max(frame_times)
            # Convert to FPS
            avg_fps = 1000 / avg_frame_time if avg_frame_time > 0 else float('inf')
            min_fps = 1000 / max_frame_time if max_frame_time > 0 else 0
            max_fps = 1000 / min_frame_time if min_frame_time > 0 else float('inf')
            # Stability: percentage of frames that took <= 33.33ms (30 FPS)
            stable_frames = sum(1 for t in frame_times if t <= 33.33)
            stable_fps = stable_frames / len(frame_times) * 100
        else:
            avg_fps = min_fps = max_fps = stable_fps = 0

        return {
            "avg_fps": avg_fps,
            "min_fps": min_fps,
            "max_fps": max_fps,
            "stability_percent": stable_fps,
            "sample_count": len(frame_times),
            "total_frames": frame_count,
            "duration": total_time,
        }

    def test_baseline_fps_no_effects(self) -> None:
        """Test baseline FPS with no effects (1 ball, no particles, no trails)"""
        results = self._run_simulation(duration_seconds=3.0, num_balls=1, num_particles=0, num_trails=0)

        print(f"\n=== Baseline FPS (no effects) ===")
        print(f"Average: {results['avg_fps']:.1f} FPS")
        print(f"Min: {results['min_fps']:.1f} FPS")
        print(f"Max: {results['max_fps']:.1f} FPS")
        print(f"Stability (>30 FPS): {results['stability_percent']:.1f}%")

        # Should maintain at least 30 FPS on any hardware
        self.assertGreater(results['avg_fps'], 30, "Average FPS should be above 30")
        self.assertGreater(results['stability_percent'], 90, "Should maintain 30+ FPS 90% of time")

    def test_low_profile_performance(self) -> None:
        """Test performance with low profile settings"""
        profile = PERFORMANCE_PROFILES["low"]
        results = self._run_simulation(
            duration_seconds=3.0,
            num_balls=2,
            num_particles=profile["max_particles"],
            num_trails=profile["max_trails"],
        )

        print(f"\n=== Low Profile Performance ===")
        print(f"Max particles: {profile['max_particles']}")
        print(f"Max trails: {profile['max_trails']}")
        print(f"Average: {results['avg_fps']:.1f} FPS")
        print(f"Stability (>30 FPS): {results['stability_percent']:.1f}%")

        # Low profile targets 30 FPS
        self.assertGreater(results['avg_fps'], 25, "Low profile should maintain 25+ FPS")

    def test_medium_profile_performance(self) -> None:
        """Test performance with medium profile settings"""
        profile = PERFORMANCE_PROFILES["medium"]
        results = self._run_simulation(
            duration_seconds=3.0,
            num_balls=2,
            num_particles=profile["max_particles"],
            num_trails=profile["max_trails"],
        )

        print(f"\n=== Medium Profile Performance ===")
        print(f"Max particles: {profile['max_particles']}")
        print(f"Max trails: {profile['max_trails']}")
        print(f"Average: {results['avg_fps']:.1f} FPS")
        print(f"Stability (>30 FPS): {results['stability_percent']:.1f}%")

        # Medium profile targets 60 FPS
        self.assertGreater(results['avg_fps'], 45, "Medium profile should maintain 45+ FPS")

    def test_high_profile_performance(self) -> None:
        """Test performance with high profile settings"""
        profile = PERFORMANCE_PROFILES["high"]
        results = self._run_simulation(
            duration_seconds=3.0,
            num_balls=2,
            num_particles=profile["max_particles"],
            num_trails=profile["max_trails"],
        )

        print(f"\n=== High Profile Performance ===")
        print(f"Max particles: {profile['max_particles']}")
        print(f"Max trails: {profile['max_trails']}")
        print(f"Average: {results['avg_fps']:.1f} FPS")
        print(f"Stability (>30 FPS): {results['stability_percent']:.1f}%")

        # High profile targets 60 FPS
        self.assertGreater(results['avg_fps'], 50, "High profile should maintain 50+ FPS")

    def test_multi_ball_stress(self) -> None:
        """Stress test with maximum balls (multi-ball powerup scenario)"""
        results = self._run_simulation(duration_seconds=3.0, num_balls=4, num_particles=50, num_trails=20)

        print(f"\n=== Multi-Ball Stress Test (4 balls) ===")
        print(f"Average: {results['avg_fps']:.1f} FPS")
        print(f"Min: {results['min_fps']:.1f} FPS")
        print(f"Stability (>30 FPS): {results['stability_percent']:.1f}%")

        # Should still be playable
        self.assertGreater(results['avg_fps'], 25, "Multi-ball should maintain 25+ FPS")

    def test_particle_stress(self) -> None:
        """Stress test with maximum particles"""
        results = self._run_simulation(duration_seconds=3.0, num_balls=2, num_particles=200, num_trails=40)

        print(f"\n=== Particle Stress Test (200 particles) ===")
        print(f"Average: {results['avg_fps']:.1f} FPS")
        print(f"Min: {results['min_fps']:.1f} FPS")
        print(f"Stability (>30 FPS): {results['stability_percent']:.1f}%")

        # Should maintain playable FPS
        self.assertGreater(results['avg_fps'], 25, "Particle stress should maintain 25+ FPS")

    def test_render_performance(self) -> None:
        """Test rendering performance with dirty rects simulation"""
        # Create many sprites
        paddle1 = Paddle(1, is_ai=False)
        paddle2 = Paddle(2, is_ai=True)
        balls = [get_ball_pool().acquire() for _ in range(4)]
        powerups = pygame.sprite.Group()

        # Create multiple powerups
        for i in range(5):
            from PyPong.core.entities import PowerUp

            powerup = PowerUp()
            powerup.rect.center = (200 + i * 150, 360)
            powerups.add(powerup)

        surface = pygame.Surface((WINDOW_WIDTH, WINDOW_HEIGHT))
        all_sprites = pygame.sprite.RenderUpdates(paddle1, paddle2, *balls, powerups)

        # Measure render time
        render_times: List[float] = []
        for _ in range(100):
            start = time.perf_counter()
            all_sprites.draw(surface)
            elapsed = (time.perf_counter() - start) * 1000
            render_times.append(elapsed)

        # Return balls to pool
        for ball in balls:
            get_ball_pool().release(ball)

        avg_render_time = sum(render_times) / len(render_times)
        max_render_time = max(render_times)

        print(f"\n=== Render Performance (10 sprites) ===")
        print(f"Average render time: {avg_render_time:.2f}ms")
        print(f"Max render time: {max_render_time:.2f}ms")

        # Render should complete in under 5ms for 60 FPS target
        self.assertLess(avg_render_time, 5.0, "Average render time should be under 5ms")

    def test_frame_pacing(self) -> None:
        """Test frame pacing consistency (important for smooth gameplay)"""
        # Run short simulation and measure frame time variance
        results = self._run_simulation(duration_seconds=2.0, num_balls=2, num_particles=50, num_trails=20)

        print(f"\n=== Frame Pacing Test ===")
        print(f"Total frames: {results['total_frames']}")
        print(f"Duration: {results['duration']:.2f}s")
        print(f"Average FPS: {results['avg_fps']:.1f}")
        print(f"Minimum FPS: {results['min_fps']:.1f}")

        # For uncapped FPS, min FPS is more meaningful than pacing score
        # The key metric: minimum FPS should be above 60 for smooth gameplay
        print(f"Minimum FPS target (60+): {'PASS' if results['min_fps'] >= 60 else 'FAIL'}")

        # Should maintain at least 60 FPS minimum for smooth gameplay
        self.assertGreater(results['min_fps'], 60, "Minimum FPS should be above 60 for smooth gameplay")


def run_benchmark_summary() -> None:
    """Run all benchmarks and print summary"""
    print("\n" + "=" * 60)
    print("FPS BENCHMARK SUMMARY")
    print("=" * 60)
    print("This benchmark tests game performance under various conditions.")
    print("Results help determine optimal settings for different hardware.")
    print("=" * 60 + "\n")


if __name__ == "__main__":
    run_benchmark_summary()
    unittest.main(verbosity=2)
