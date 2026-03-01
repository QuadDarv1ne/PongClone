import pygame
from PyPong.core.config import *

class TouchControls:
    def __init__(self, screen_width, screen_height):
        self.screen_width = screen_width
        self.screen_height = screen_height
        self.touch_zones = self._create_touch_zones()
        self.active_touches = {}
        self.font = pygame.font.SysFont(FONT_NAME, 20)

    def _create_touch_zones(self):
        # Left side for player 1, right side for player 2
        zone_width = self.screen_width // 2
        
        return {
            "p1_up": pygame.Rect(0, 0, zone_width, self.screen_height // 2),
            "p1_down": pygame.Rect(0, self.screen_height // 2, zone_width, self.screen_height // 2),
            "p2_up": pygame.Rect(zone_width, 0, zone_width, self.screen_height // 2),
            "p2_down": pygame.Rect(zone_width, self.screen_height // 2, zone_width, self.screen_height // 2)
        }

    def handle_touch(self, event):
        if event.type == pygame.MOUSEBUTTONDOWN:
            pos = event.pos
            for zone_name, zone_rect in self.touch_zones.items():
                if zone_rect.collidepoint(pos):
                    self.active_touches[zone_name] = True
        
        elif event.type == pygame.MOUSEBUTTONUP:
            self.active_touches.clear()

    def get_input(self, player):
        if player == 1:
            return {
                "up": self.active_touches.get("p1_up", False),
                "down": self.active_touches.get("p1_down", False)
            }
        elif player == 2:
            return {
                "up": self.active_touches.get("p2_up", False),
                "down": self.active_touches.get("p2_down", False)
            }
        return {"up": False, "down": False}

    def draw(self, surface):
        # Draw touch zones with transparency
        overlay = pygame.Surface((self.screen_width, self.screen_height))
        overlay.set_alpha(30)
        
        # Player 1 zones
        pygame.draw.rect(overlay, GREEN, self.touch_zones["p1_up"], 2)
        pygame.draw.rect(overlay, GREEN, self.touch_zones["p1_down"], 2)
        
        # Player 2 zones
        pygame.draw.rect(overlay, YELLOW, self.touch_zones["p2_up"], 2)
        pygame.draw.rect(overlay, YELLOW, self.touch_zones["p2_down"], 2)
        
        surface.blit(overlay, (0, 0))
        
        # Draw labels
        p1_up_text = self.font.render("P1 UP", True, GREEN)
        p1_down_text = self.font.render("P1 DOWN", True, GREEN)
        p2_up_text = self.font.render("P2 UP", True, YELLOW)
        p2_down_text = self.font.render("P2 DOWN", True, YELLOW)
        
        surface.blit(p1_up_text, (20, 20))
        surface.blit(p1_down_text, (20, self.screen_height - 40))
        surface.blit(p2_up_text, (self.screen_width - 100, 20))
        surface.blit(p2_down_text, (self.screen_width - 140, self.screen_height - 40))


class AdaptiveScreen:
    def __init__(self):
        self.base_width = WINDOW_WIDTH
        self.base_height = WINDOW_HEIGHT
        self.current_width = WINDOW_WIDTH
        self.current_height = WINDOW_HEIGHT
        self.scale_x = 1.0
        self.scale_y = 1.0

    def update_resolution(self, width, height):
        self.current_width = width
        self.current_height = height
        self.scale_x = width / self.base_width
        self.scale_y = height / self.base_height

    def scale_position(self, x, y):
        return int(x * self.scale_x), int(y * self.scale_y)

    def scale_size(self, width, height):
        return int(width * self.scale_x), int(height * self.scale_y)

    def get_scaled_surface(self, surface):
        if self.scale_x == 1.0 and self.scale_y == 1.0:
            return surface
        return pygame.transform.scale(surface, (self.current_width, self.current_height))
