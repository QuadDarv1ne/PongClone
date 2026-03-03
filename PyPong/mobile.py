from typing import Any, Dict, List, Optional, Tuple

import pygame

from PyPong.core.config import FONT_NAME, GREEN, WINDOW_HEIGHT, WINDOW_WIDTH, YELLOW


class TouchControls:
    """Touch controls for mobile and tablet devices"""

    def __init__(self, screen_width: int, screen_height: int) -> None:
        self.screen_width = screen_width
        self.screen_height = screen_height
        self.touch_zones = self._create_touch_zones()
        self.active_touches: Dict[str, bool] = {}
        self.font = pygame.font.SysFont(FONT_NAME, max(16, int(screen_height * 0.025)))
        self.show_zones = True  # Show touch zones by default on mobile

    def _create_touch_zones(self) -> Dict[str, pygame.Rect]:
        """Create touch zones optimized for different screen sizes"""
        # Left side for player 1, right side for player 2
        zone_width = self.screen_width // 2

        return {
            "p1_up": pygame.Rect(0, 0, zone_width, self.screen_height // 2),
            "p1_down": pygame.Rect(0, self.screen_height // 2, zone_width, self.screen_height // 2),
            "p2_up": pygame.Rect(zone_width, 0, zone_width, self.screen_height // 2),
            "p2_down": pygame.Rect(zone_width, self.screen_height // 2, zone_width, self.screen_height // 2),
        }

    def update_screen_size(self, width: int, height: int) -> None:
        """Update touch zones when screen size changes"""
        self.screen_width = width
        self.screen_height = height
        self.touch_zones = self._create_touch_zones()
        self.font = pygame.font.SysFont(FONT_NAME, max(16, int(height * 0.025)))

    def handle_touch(self, event):
        """Handle touch/mouse events"""
        if event.type == pygame.MOUSEBUTTONDOWN:
            pos = event.pos
            for zone_name, zone_rect in self.touch_zones.items():
                if zone_rect.collidepoint(pos):
                    self.active_touches[zone_name] = True

        elif event.type == pygame.MOUSEBUTTONUP:
            self.active_touches.clear()

        # Support for pygame FINGERDOWN/FINGERUP events (if available)
        elif hasattr(pygame, "FINGERDOWN") and event.type == pygame.FINGERDOWN:
            # Convert normalized coordinates to screen coordinates
            x = int(event.x * self.screen_width)
            y = int(event.y * self.screen_height)
            pos = (x, y)
            for zone_name, zone_rect in self.touch_zones.items():
                if zone_rect.collidepoint(pos):
                    self.active_touches[zone_name] = True

        elif hasattr(pygame, "FINGERUP") and event.type == pygame.FINGERUP:
            self.active_touches.clear()

    def get_input(self, player):
        """Get input state for specified player"""
        if player == 1:
            return {"up": self.active_touches.get("p1_up", False), "down": self.active_touches.get("p1_down", False)}
        elif player == 2:
            return {"up": self.active_touches.get("p2_up", False), "down": self.active_touches.get("p2_down", False)}
        return {"up": False, "down": False}

    def toggle_zones(self) -> None:
        """Toggle visibility of touch zones"""
        self.show_zones = not self.show_zones

    def draw(self, surface):
        """Draw touch zones with transparency"""
        if not self.show_zones:
            return

        # Draw touch zones with transparency
        overlay = pygame.Surface((self.screen_width, self.screen_height))
        overlay.set_alpha(30)

        # Player 1 zones (left side)
        color_p1 = GREEN if any(self.active_touches.get(k, False) for k in ["p1_up", "p1_down"]) else (0, 255, 0)
        pygame.draw.rect(overlay, color_p1, self.touch_zones["p1_up"], 2)
        pygame.draw.rect(overlay, color_p1, self.touch_zones["p1_down"], 2)

        # Player 2 zones (right side)
        color_p2 = YELLOW if any(self.active_touches.get(k, False) for k in ["p2_up", "p2_down"]) else (255, 255, 0)
        pygame.draw.rect(overlay, color_p2, self.touch_zones["p2_up"], 2)
        pygame.draw.rect(overlay, color_p2, self.touch_zones["p2_down"], 2)

        surface.blit(overlay, (0, 0))

        # Draw labels
        p1_up_text = self.font.render("↑", True, color_p1)
        p1_down_text = self.font.render("↓", True, color_p1)
        p2_up_text = self.font.render("↑", True, color_p2)
        p2_down_text = self.font.render("↓", True, color_p2)

        # Position labels in center of zones
        padding = 20
        surface.blit(p1_up_text, (self.screen_width // 4 - p1_up_text.get_width() // 2, padding))
        surface.blit(
            p1_down_text,
            (
                self.screen_width // 4 - p1_down_text.get_width() // 2,
                self.screen_height - padding - p1_down_text.get_height(),
            ),
        )
        surface.blit(p2_up_text, (3 * self.screen_width // 4 - p2_up_text.get_width() // 2, padding))
        surface.blit(
            p2_down_text,
            (
                3 * self.screen_width // 4 - p2_down_text.get_width() // 2,
                self.screen_height - padding - p2_down_text.get_height(),
            ),
        )


class AdaptiveScreen:
    """Adaptive screen scaling for different resolutions and devices"""

    def __init__(self) -> None:
        self.base_width = WINDOW_WIDTH
        self.base_height = WINDOW_HEIGHT
        self.current_width = WINDOW_WIDTH
        self.current_height = WINDOW_HEIGHT
        self.scale_x = 1.0
        self.scale_y = 1.0
        self._needs_resize = False
        self.aspect_ratio = WINDOW_WIDTH / WINDOW_HEIGHT
        self.maintain_aspect_ratio = True

    def update_resolution(self, width: int, height: int) -> None:
        """Update screen resolution and calculate scaling factors"""
        self.current_width = width
        self.current_height = height

        if self.maintain_aspect_ratio:
            # Calculate scale to fit while maintaining aspect ratio
            scale_w = width / self.base_width
            scale_h = height / self.base_height
            scale = min(scale_w, scale_h)
            self.scale_x = scale
            self.scale_y = scale
        else:
            # Stretch to fill screen
            self.scale_x = width / self.base_width
            self.scale_y = height / self.base_height

        self._needs_resize = self.scale_x != 1.0 or self.scale_y != 1.0

    def scale_position(self, x: float, y: float) -> Tuple[int, int]:
        """Scale position coordinates"""
        return int(x * self.scale_x), int(y * self.scale_y)

    def scale_size(self, width: float, height: float) -> Tuple[int, int]:
        """Scale size dimensions"""
        return int(width * self.scale_x), int(height * self.scale_y)

    def unscale_position(self, x: float, y: float) -> Tuple[int, int]:
        """Convert screen coordinates back to game coordinates"""
        if self.scale_x == 0 or self.scale_y == 0:
            return int(x), int(y)
        return int(x / self.scale_x), int(y / self.scale_y)

    def get_scaled_surface(self, surface: pygame.Surface) -> pygame.Surface:
        """Scale surface to current resolution"""
        if not self._needs_resize:
            return surface

        if self.maintain_aspect_ratio:
            # Scale with aspect ratio, center on screen
            scaled_width = int(self.base_width * self.scale_x)
            scaled_height = int(self.base_height * self.scale_y)
            scaled_surface = pygame.transform.smoothscale(surface, (scaled_width, scaled_height))

            # Create black background and center scaled surface
            final_surface = pygame.Surface((self.current_width, self.current_height))
            final_surface.fill((0, 0, 0))

            offset_x = (self.current_width - scaled_width) // 2
            offset_y = (self.current_height - scaled_height) // 2
            final_surface.blit(scaled_surface, (offset_x, offset_y))

            return final_surface
        else:
            # Stretch to fill
            return pygame.transform.smoothscale(surface, (self.current_width, self.current_height))

    def get_display_info(self) -> Dict[str, Any]:
        """Get current display information"""
        return {
            "base_resolution": (self.base_width, self.base_height),
            "current_resolution": (self.current_width, self.current_height),
            "scale": (self.scale_x, self.scale_y),
            "aspect_ratio": self.aspect_ratio,
            "needs_resize": self._needs_resize,
        }
