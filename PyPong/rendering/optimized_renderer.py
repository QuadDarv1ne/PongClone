"""
Optimized renderer with dirty rect rendering and caching
"""
from typing import Any, Dict, List, Optional, Tuple

import pygame

from PyPong.core.config import BLACK
from PyPong.core.game_state import GameState
from PyPong.core.logger import logger


class DirtyRectRenderer:
    """
    Optimized renderer using dirty rectangles.
    Only redraws changed areas instead of full screen.
    """

    def __init__(
        self,
        screen: pygame.Surface,
        game_surface: pygame.Surface,
        theme: Any,
        settings: Any,
    ):
        self.screen = screen
        self.game_surface = game_surface
        self.theme = theme
        self.settings = settings

        # Dirty rect tracking
        self.dirty_rects: List[pygame.Rect] = []
        self.use_dirty_rects = settings.get("use_dirty_rects", True)

        # Surface caching
        self._cached_surfaces: Dict[str, pygame.Surface] = {}
        self._cache_enabled = settings.get("cache_surfaces", True)

        # Background cache
        self._background_cache: Optional[pygame.Surface] = None
        self._background_dirty = True

    def mark_dirty(self, rect: pygame.Rect) -> None:
        """Mark a rectangle as dirty (needs redraw)"""
        if self.use_dirty_rects:
            self.dirty_rects.append(rect)

    def clear_dirty_rects(self) -> None:
        """Clear all dirty rectangles"""
        self.dirty_rects.clear()

    def get_cached_surface(self, key: str) -> Optional[pygame.Surface]:
        """Get a cached surface by key"""
        if not self._cache_enabled:
            return None
        return self._cached_surfaces.get(key)

    def cache_surface(self, key: str, surface: pygame.Surface) -> None:
        """Cache a surface for reuse"""
        if self._cache_enabled:
            self._cached_surfaces[key] = surface.copy()

    def clear_cache(self, key: Optional[str] = None) -> None:
        """Clear cached surfaces"""
        if key:
            self._cached_surfaces.pop(key, None)
        else:
            self._cached_surfaces.clear()

    def render_background(self) -> pygame.Surface:
        """
        Render and cache background.
        Only redraws when marked dirty.
        """
        if self._background_cache and not self._background_dirty:
            return self._background_cache

        # Create background surface
        bg = pygame.Surface(self.game_surface.get_size())
        bg.fill(self.theme.bg_color)

        # Cache it
        self._background_cache = bg
        self._background_dirty = False

        return bg

    def invalidate_background(self) -> None:
        """Mark background as dirty"""
        self._background_dirty = True

    def render_sprites_optimized(
        self,
        sprite_group: pygame.sprite.Group,
        background: pygame.Surface,
    ) -> List[pygame.Rect]:
        """
        Render sprites using RenderUpdates for dirty rect tracking.

        Returns:
            List of dirty rectangles
        """
        if not sprite_group:
            return []

        # Use RenderUpdates if available
        if isinstance(sprite_group, pygame.sprite.RenderUpdates):
            return sprite_group.draw(self.game_surface)
        else:
            # Fallback to regular draw
            sprite_group.draw(self.game_surface)
            return []

    def blit_optimized(
        self,
        source: pygame.Surface,
        dest: pygame.Surface,
        pos: Tuple[int, int],
        area: Optional[pygame.Rect] = None,
    ) -> pygame.Rect:
        """
        Optimized blit that tracks dirty rects.

        Returns:
            Dirty rectangle
        """
        rect = dest.blit(source, pos, area)
        self.mark_dirty(rect)
        return rect

    def update_display_optimized(self) -> None:
        """
        Update display using dirty rectangles.
        Only updates changed areas.
        """
        if self.use_dirty_rects and self.dirty_rects:
            # Update only dirty areas
            pygame.display.update(self.dirty_rects)
            logger.debug(f"Updated {len(self.dirty_rects)} dirty rects")
        else:
            # Full screen update
            pygame.display.flip()

    def get_memory_usage(self) -> Dict[str, int]:
        """Get memory usage statistics"""
        cache_size = sum(
            surf.get_width() * surf.get_height() * surf.get_bytesize() for surf in self._cached_surfaces.values()
        )

        bg_size = 0
        if self._background_cache:
            bg_size = (
                self._background_cache.get_width()
                * self._background_cache.get_height()
                * self._background_cache.get_bytesize()
            )

        return {
            "cached_surfaces": len(self._cached_surfaces),
            "cache_size_bytes": cache_size,
            "background_size_bytes": bg_size,
            "total_bytes": cache_size + bg_size,
        }


class OptimizedRenderer:
    """
    Enhanced renderer with performance optimizations:
    - Dirty rect rendering
    - Surface caching
    - Batch rendering
    - Culling off-screen objects
    """

    def __init__(
        self,
        screen: pygame.Surface,
        game_surface: pygame.Surface,
        theme: Any,
        settings: Any,
        adaptive_screen: Any,
    ):
        self.screen = screen
        self.game_surface = game_surface
        self.theme = theme
        self.settings = settings
        self.adaptive_screen = adaptive_screen

        # Dirty rect renderer
        self.dirty_renderer = DirtyRectRenderer(screen, game_surface, theme, settings)

        # Sprite groups (converted to RenderUpdates for optimization)
        self.all_sprites: Optional[pygame.sprite.RenderUpdates] = None
        self.powerups: Optional[pygame.sprite.RenderUpdates] = None
        self.particles: Optional[Any] = None
        self.trails: Optional[pygame.sprite.RenderUpdates] = None

        # Performance tracking
        self._frame_count = 0
        self._render_times: List[float] = []

    def set_sprite_groups(
        self,
        all_sprites: Optional[pygame.sprite.Group],
        powerups: Optional[pygame.sprite.Group],
        particles: Optional[Any],
        trails: Optional[pygame.sprite.Group],
    ) -> None:
        """Set sprite groups (converts to RenderUpdates)"""
        # Convert to RenderUpdates for dirty rect tracking
        if all_sprites and not isinstance(all_sprites, pygame.sprite.RenderUpdates):
            new_group = pygame.sprite.RenderUpdates()
            new_group.add(*all_sprites.sprites())
            self.all_sprites = new_group
        else:
            self.all_sprites = all_sprites

        if powerups and not isinstance(powerups, pygame.sprite.RenderUpdates):
            new_group = pygame.sprite.RenderUpdates()
            new_group.add(*powerups.sprites())
            self.powerups = new_group
        else:
            self.powerups = powerups

        if trails and not isinstance(trails, pygame.sprite.RenderUpdates):
            new_group = pygame.sprite.RenderUpdates()
            new_group.add(*trails.sprites())
            self.trails = new_group
        else:
            self.trails = trails

        self.particles = particles

    def cull_offscreen_sprites(
        self,
        sprite_group: pygame.sprite.Group,
        screen_rect: pygame.Rect,
    ) -> List[pygame.sprite.Sprite]:
        """
        Cull sprites that are off-screen.

        Returns:
            List of visible sprites
        """
        if not sprite_group:
            return []

        visible = []
        for sprite in sprite_group:
            if hasattr(sprite, "rect") and screen_rect.colliderect(sprite.rect):
                visible.append(sprite)

        return visible

    def render_game_optimized(self, state_manager: Any, shake: Any) -> None:
        """Optimized game rendering"""
        import time

        start_time = time.perf_counter()

        # Clear dirty rects from previous frame
        self.dirty_renderer.clear_dirty_rects()

        # Render background (cached)
        background = self.dirty_renderer.render_background()
        self.game_surface.blit(background, (0, 0))
        # Mark entire screen as dirty since background was drawn
        self.dirty_renderer.mark_dirty(self.game_surface.get_rect())

        # Draw net and score (these change frequently, so no caching)
        state_manager.draw_net()
        state_manager.draw_score()

        # Draw sprites with dirty rect tracking
        if self.trails:
            self.dirty_renderer.render_sprites_optimized(self.trails, background)

        if self.all_sprites:
            self.dirty_renderer.render_sprites_optimized(self.all_sprites, background)

        if self.powerups:
            self.dirty_renderer.render_sprites_optimized(self.powerups, background)

        if self.particles:
            self.particles.draw(self.game_surface)

        # Track render time
        elapsed = time.perf_counter() - start_time
        self._render_times.append(elapsed)
        if len(self._render_times) > 100:
            self._render_times.pop(0)

        self._frame_count += 1

        # Blit game_surface to screen for display
        screen_rect = self.screen.blit(self.game_surface, (0, 0))
        # Mark the blitted area as dirty
        self.dirty_renderer.mark_dirty(screen_rect)

    def get_performance_stats(self) -> Dict[str, Any]:
        """Get rendering performance statistics"""
        if not self._render_times:
            return {}

        avg_time = sum(self._render_times) / len(self._render_times)

        return {
            "frame_count": self._frame_count,
            "avg_render_time_ms": avg_time * 1000,
            "fps_estimate": 1.0 / avg_time if avg_time > 0 else 0,
            "memory_usage": self.dirty_renderer.get_memory_usage(),
        }

    def clear(self) -> None:
        """Clear screen"""
        self.game_surface.fill(self.theme.bg_color)
        self.dirty_renderer.invalidate_background()
