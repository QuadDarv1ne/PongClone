"""
Automatic hardware detection for optimal game settings.
Runs once at first launch or when no settings.json exists.
"""
import os
from typing import Dict, Any

import pygame

from PyPong.core.config import PERFORMANCE_PROFILES
from PyPong.core.logger import logger

# Base game resolution — all draw methods use these constants
BASE_WIDTH = 1024
BASE_HEIGHT = 720
BASE_ASPECT = BASE_WIDTH / BASE_HEIGHT  # ~1.422 (4:3)


def detect_display_resolution() -> Dict[str, int]:
    """
    Detect native display resolution and recommend window size
    that matches the game's 4:3 aspect ratio.

    Prefers clean integer scale multiples (1x, 1.5x, 2x) of the
    base resolution. Falls back to the largest 4:3 window that
    fits within the desktop.

    Returns:
        dict: {"width": int, "height": int}
    """
    MAX_WIDTH = 1920
    MAX_HEIGHT = 1080

    try:
        sizes = pygame.display.get_desktop_sizes()
        if sizes:
            primary = max(sizes, key=lambda s: s[0] * s[1])
            desktop_w, desktop_h = primary
        else:
            info = pygame.display.Info()
            desktop_w, desktop_h = info.current_w, info.current_h
    except (pygame.error, AttributeError):
        desktop_w, desktop_h = 1920, 1080

    if not desktop_w or not desktop_h:
        desktop_w, desktop_h = 1920, 1080

    desktop_w = min(desktop_w, MAX_WIDTH)
    desktop_h = min(desktop_h, MAX_HEIGHT)

    logger.info(
        f"Auto-detect: desktop={desktop_w}x{desktop_h}, "
        f"game base={BASE_WIDTH}x{BASE_HEIGHT} ({BASE_ASPECT:.3f})"
    )

    # Prefer clean integer scale multiples
    for multiplier in [2.0, 1.5, 1.0]:
        candidate_w = int(BASE_WIDTH * multiplier)
        candidate_h = int(BASE_HEIGHT * multiplier)
        if candidate_w <= desktop_w and candidate_h <= desktop_h:
            logger.info(
                f"Auto-detect: selected {candidate_w}x{candidate_h} "
                f"({multiplier}x scale, fits in desktop)"
            )
            return {"width": candidate_w, "height": candidate_h}

    # Fallback: largest 4:3 window fitting desktop
    if desktop_w / desktop_h > BASE_ASPECT:
        target_h = desktop_h
        target_w = int(target_h * BASE_ASPECT)
    else:
        target_w = desktop_w
        target_h = int(target_w / BASE_ASPECT)

    # Enforce minimum
    MIN_WIDTH = 800
    MIN_HEIGHT = 600
    target_w = max(target_w, MIN_WIDTH)
    target_h = max(target_h, MIN_HEIGHT)
    target_w = min(target_w, desktop_w)
    target_h = min(target_h, desktop_h)

    logger.info(
        f"Auto-detect: selected {target_w}x{target_h} "
        f"(fallback, fits in desktop)"
    )

    return {"width": target_w, "height": target_h}


def detect_performance_profile() -> Dict[str, Any]:
    """
    Detect CPU/RAM/VRAM and recommend performance profile.

    Returns:
        dict: {"profile": str, "cpu_count": int,
               "memory_mb": int, "vram_mb": int}
    """
    cpu_count = os.cpu_count() or 2
    memory_mb = _detect_memory_mb()
    vram_mb = _detect_vram_mb()

    profile = _classify_profile(cpu_count, memory_mb, vram_mb)

    logger.info(
        f"Auto-detect: performance profile={profile} "
        f"(CPU={cpu_count} cores, RAM={memory_mb}MB, VRAM={vram_mb}MB)"
    )

    return {
        "profile": profile,
        "cpu_count": cpu_count,
        "memory_mb": memory_mb,
        "vram_mb": vram_mb,
    }


def _detect_memory_mb() -> int:
    """Detect available system memory in MB."""
    # Try psutil first
    try:
        import psutil
        return psutil.virtual_memory().total // (1024 * 1024)
    except ImportError:
        pass

    # Linux: read /proc/meminfo
    try:
        with open("/proc/meminfo", "r") as f:
            for line in f:
                if line.startswith("MemTotal:"):
                    parts = line.split()
                    return int(parts[1]) // 1024
    except (IOError, OSError, IndexError, ValueError):
        pass

    # macOS: sysctl
    try:
        import subprocess
        result = subprocess.run(
            ["sysctl", "-n", "hw.memsize"],
            capture_output=True, text=True, timeout=2
        )
        if result.returncode == 0:
            return int(result.stdout.strip()) // (1024 * 1024)
    except (subprocess.TimeoutExpired, FileNotFoundError, ValueError):
        pass

    # Windows: wmic
    try:
        import subprocess
        result = subprocess.run(
            ["wmic", "OS", "get", "TotalVisibleMemorySize", "/Value"],
            capture_output=True, text=True, timeout=2
        )
        if result.returncode == 0:
            for line in result.stdout.split("\n"):
                if line.startswith("TotalVisibleMemorySize="):
                    value = line.split("=")[1].strip()
                    return int(value) // 1024
    except (subprocess.TimeoutExpired, FileNotFoundError, ValueError, IndexError):
        pass

    return 4096


def _detect_vram_mb() -> int:
    """Detect GPU video memory in MB."""
    # Windows: wmic
    try:
        import subprocess
        result = subprocess.run(
            ["wmic", "path", "Win32_VideoController", "get", "AdapterRAM", "/Value"],
            capture_output=True, text=True, timeout=3
        )
        if result.returncode == 0:
            for line in result.stdout.split("\n"):
                if line.startswith("AdapterRAM="):
                    value = line.split("=")[1].strip()
                    if value.isdigit():
                        return int(value) // (1024 * 1024)
    except (subprocess.TimeoutExpired, FileNotFoundError, ValueError, IndexError):
        pass

    # Try pygame display info for video memory
    try:
        info = pygame.display.Info()
        if hasattr(info, 'video_memory') and info.video_memory:
            return info.video_memory // (1024 * 1024)
    except (pygame.error, AttributeError):
        pass

    return 0


def _classify_profile(cpu_count: int, memory_mb: int, vram_mb: int = 0) -> str:
    """Classify hardware into a performance profile."""
    # Ultra: 8+ cores, 16GB+ RAM, 4GB+ VRAM
    if cpu_count >= 8 and memory_mb >= 16384 and vram_mb >= 4096:
        return "ultra"
    # High: 4+ cores, 8GB+ RAM (VRAM optional)
    if cpu_count >= 4 and memory_mb >= 8192:
        return "high"
    # Medium: 2+ cores, 4GB+ RAM
    if cpu_count >= 2 and memory_mb >= 4096:
        return "medium"
    return "low"


def get_recommended_settings() -> Dict[str, Any]:
    """
    Coordinator: runs all detections and returns combined settings dict.

    Returns:
        dict: Settings compatible with Settings.set()
    """
    result: Dict[str, Any] = {}

    # Display resolution
    try:
        display = detect_display_resolution()
        result["width"] = display["width"]
        result["height"] = display["height"]
    except Exception as e:
        logger.warning(f"Display detection failed: {e}")

    # Performance profile
    try:
        perf = detect_performance_profile()
        profile_name = perf["profile"]
        result["profile"] = profile_name

        # Apply profile values
        profile = PERFORMANCE_PROFILES.get(profile_name, PERFORMANCE_PROFILES["medium"])
        result["max_particles"] = profile["max_particles"]
        result["max_trails"] = profile["max_trails"]
        result["target_fps"] = profile["target_fps"]
        result["enable_shake"] = profile["enable_shake"]
        result["enable_effects"] = profile["enable_effects"]
    except Exception as e:
        logger.warning(f"Performance detection failed: {e}")

    return result
