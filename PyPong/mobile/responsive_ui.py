"""
Responsive UI system for different screen sizes and orientations
"""
from enum import Enum, auto
from typing import Any, Callable, Dict, Optional, Tuple

import pygame

from PyPong.core.logger import logger


class ScreenOrientation(Enum):
    """Screen orientation types"""

    PORTRAIT = auto()
    LANDSCAPE = auto()
    SQUARE = auto()


class DeviceType(Enum):
    """Device type categories"""

    PHONE = auto()
    TABLET = auto()
    DESKTOP = auto()


class BreakPoint:
    """Responsive breakpoints for different screen sizes"""

    # Width breakpoints (pixels)
    PHONE_MAX = 480
    TABLET_MAX = 1024
    DESKTOP_MIN = 1025

    # Height breakpoints
    SMALL_HEIGHT = 600
    MEDIUM_HEIGHT = 900
    LARGE_HEIGHT = 1080


class ResponsiveLayout:
    """
    Responsive layout system that adapts to screen size.
    Provides scaled dimensions and positions.
    """

    def __init__(self, base_width: int = 1024, base_height: int = 720):
        self.base_width = base_width
        self.base_height = base_height
        self.current_width = base_width
        self.current_height = base_height

        self._device_type = DeviceType.DESKTOP
        self._orientation = ScreenOrientation.LANDSCAPE
        self._scale_factor = 1.0

        self._update_device_info()

    def update_screen_size(self, width: int, height: int) -> None:
        """Update screen size and recalculate layout"""
        self.current_width = width
        self.current_height = height
        self._update_device_info()
        logger.info(
            f"Screen updated: {width}x{height}, device={self._device_type.name}, orientation={self._orientation.name}"
        )

    def _update_device_info(self) -> None:
        """Update device type and orientation based on screen size"""
        # Detect device type
        if self.current_width <= BreakPoint.PHONE_MAX:
            self._device_type = DeviceType.PHONE
        elif self.current_width <= BreakPoint.TABLET_MAX:
            self._device_type = DeviceType.TABLET
        else:
            self._device_type = DeviceType.DESKTOP

        # Detect orientation
        aspect_ratio = self.current_width / self.current_height
        if aspect_ratio < 0.9:
            self._orientation = ScreenOrientation.PORTRAIT
        elif aspect_ratio > 1.1:
            self._orientation = ScreenOrientation.LANDSCAPE
        else:
            self._orientation = ScreenOrientation.SQUARE

        # Calculate scale factor
        self._scale_factor = min(self.current_width / self.base_width, self.current_height / self.base_height)

    @property
    def device_type(self) -> DeviceType:
        """Get current device type"""
        return self._device_type

    @property
    def orientation(self) -> ScreenOrientation:
        """Get current orientation"""
        return self._orientation

    @property
    def is_mobile(self) -> bool:
        """Check if device is mobile (phone or tablet)"""
        return self._device_type in (DeviceType.PHONE, DeviceType.TABLET)

    @property
    def is_portrait(self) -> bool:
        """Check if orientation is portrait"""
        return self._orientation == ScreenOrientation.PORTRAIT

    def scale(self, value: float) -> int:
        """Scale a value based on screen size"""
        return int(value * self._scale_factor)

    def scale_font_size(self, base_size: int) -> int:
        """Scale font size with minimum threshold"""
        scaled = self.scale(base_size)
        # Ensure minimum readable size
        min_size = 12 if self.is_mobile else 14
        return max(min_size, scaled)

    def scale_rect(self, x: float, y: float, width: float, height: float) -> pygame.Rect:
        """Scale a rectangle"""
        return pygame.Rect(self.scale(x), self.scale(y), self.scale(width), self.scale(height))

    def get_safe_area(self, padding_percent: float = 0.05) -> pygame.Rect:
        """
        Get safe area with padding (avoids notches, rounded corners).

        Args:
            padding_percent: Padding as percentage of screen size
        """
        padding_x = int(self.current_width * padding_percent)
        padding_y = int(self.current_height * padding_percent)

        return pygame.Rect(
            padding_x, padding_y, self.current_width - 2 * padding_x, self.current_height - 2 * padding_y
        )

    def get_layout_config(self) -> Dict[str, Any]:
        """Get layout configuration for current screen"""
        return {
            "device_type": self._device_type,
            "orientation": self._orientation,
            "scale_factor": self._scale_factor,
            "is_mobile": self.is_mobile,
            "is_portrait": self.is_portrait,
            "screen_size": (self.current_width, self.current_height),
            "safe_area": self.get_safe_area(),
        }


class AdaptiveButton:
    """Button that adapts to screen size"""

    def __init__(
        self,
        text: str,
        x: float,
        y: float,
        width: float,
        height: float,
        callback: Callable,
        layout: ResponsiveLayout,
    ):
        self.text = text
        self.base_x = x
        self.base_y = y
        self.base_width = width
        self.base_height = height
        self.callback = callback
        self.layout = layout

        self.rect = self._calculate_rect()
        self.font = self._create_font()
        self.hovered = False
        self.pressed = False

    def _calculate_rect(self) -> pygame.Rect:
        """Calculate button rectangle based on layout"""
        return self.layout.scale_rect(self.base_x, self.base_y, self.base_width, self.base_height)

    def _create_font(self) -> pygame.font.Font:
        """Create font with appropriate size"""
        font_size = self.layout.scale_font_size(24)
        return pygame.font.SysFont("Arial", font_size)

    def update_layout(self) -> None:
        """Update button layout when screen changes"""
        self.rect = self._calculate_rect()
        self.font = self._create_font()

    def handle_event(self, event: pygame.event.Event) -> bool:
        """
        Handle input event.

        Returns:
            True if button was clicked
        """
        if event.type == pygame.MOUSEBUTTONDOWN:
            if self.rect.collidepoint(event.pos):
                self.pressed = True
                return False

        elif event.type == pygame.MOUSEBUTTONUP:
            if self.pressed and self.rect.collidepoint(event.pos):
                self.pressed = False
                self.callback()
                return True
            self.pressed = False

        elif event.type == pygame.MOUSEMOTION:
            self.hovered = self.rect.collidepoint(event.pos)

        # Touch events
        elif hasattr(pygame, "FINGERDOWN") and event.type == pygame.FINGERDOWN:
            x = int(event.x * self.layout.current_width)
            y = int(event.y * self.layout.current_height)
            if self.rect.collidepoint(x, y):
                self.pressed = True

        elif hasattr(pygame, "FINGERUP") and event.type == pygame.FINGERUP:
            x = int(event.x * self.layout.current_width)
            y = int(event.y * self.layout.current_height)
            if self.pressed and self.rect.collidepoint(x, y):
                self.pressed = False
                self.callback()
                return True
            self.pressed = False

        return False

    def draw(self, surface: pygame.Surface) -> None:
        """Draw button"""
        # Button color based on state
        if self.pressed:
            color = (100, 100, 100)
        elif self.hovered:
            color = (150, 150, 150)
        else:
            color = (200, 200, 200)

        # Draw button
        pygame.draw.rect(surface, color, self.rect)
        pygame.draw.rect(surface, (255, 255, 255), self.rect, 2)

        # Draw text
        text_surface = self.font.render(self.text, True, (255, 255, 255))
        text_rect = text_surface.get_rect(center=self.rect.center)
        surface.blit(text_surface, text_rect)


class AdaptiveText:
    """Text that scales with screen size"""

    def __init__(
        self,
        text: str,
        x: float,
        y: float,
        font_size: int,
        layout: ResponsiveLayout,
        color: Tuple[int, int, int] = (255, 255, 255),
        align: str = "center",
    ):
        self.text = text
        self.base_x = x
        self.base_y = y
        self.base_font_size = font_size
        self.layout = layout
        self.color = color
        self.align = align

        self.font = self._create_font()
        self.position = self._calculate_position()

    def _create_font(self) -> pygame.font.Font:
        """Create scaled font"""
        font_size = self.layout.scale_font_size(self.base_font_size)
        return pygame.font.SysFont("Arial", font_size)

    def _calculate_position(self) -> Tuple[int, int]:
        """Calculate text position"""
        return (self.layout.scale(self.base_x), self.layout.scale(self.base_y))

    def update_layout(self) -> None:
        """Update text layout when screen changes"""
        self.font = self._create_font()
        self.position = self._calculate_position()

    def draw(self, surface: pygame.Surface) -> None:
        """Draw text"""
        text_surface = self.font.render(self.text, True, self.color)

        if self.align == "center":
            rect = text_surface.get_rect(center=self.position)
        elif self.align == "left":
            rect = text_surface.get_rect(midleft=self.position)
        elif self.align == "right":
            rect = text_surface.get_rect(midright=self.position)
        else:
            rect = text_surface.get_rect(topleft=self.position)

        surface.blit(text_surface, rect)


class GridLayout:
    """Grid-based layout system"""

    def __init__(
        self,
        rows: int,
        cols: int,
        layout: ResponsiveLayout,
        padding: float = 10,
    ):
        self.rows = rows
        self.cols = cols
        self.layout = layout
        self.padding = padding

        self._calculate_cells()

    def _calculate_cells(self) -> None:
        """Calculate cell dimensions"""
        safe_area = self.layout.get_safe_area()

        self.cell_width = (safe_area.width - (self.cols + 1) * self.padding) / self.cols
        self.cell_height = (safe_area.height - (self.rows + 1) * self.padding) / self.rows
        self.offset_x = safe_area.x
        self.offset_y = safe_area.y

    def get_cell_rect(self, row: int, col: int, row_span: int = 1, col_span: int = 1) -> pygame.Rect:
        """Get rectangle for a grid cell"""
        x = self.offset_x + col * (self.cell_width + self.padding) + self.padding
        y = self.offset_y + row * (self.cell_height + self.padding) + self.padding

        width = col_span * self.cell_width + (col_span - 1) * self.padding
        height = row_span * self.cell_height + (row_span - 1) * self.padding

        return pygame.Rect(int(x), int(y), int(width), int(height))

    def update_layout(self) -> None:
        """Update grid when screen changes"""
        self._calculate_cells()
