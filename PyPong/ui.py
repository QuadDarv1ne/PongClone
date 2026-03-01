import pygame
from config import *

class PowerUpIndicator:
    def __init__(self):
        self.font = pygame.font.SysFont(FONT_NAME, 24)
        self.small_font = pygame.font.SysFont(FONT_NAME, 18)

    def draw(self, screen, powerups, paddle1, paddle2):
        y_offset = 150
        
        for powerup in powerups:
            if powerup.active:
                paddle = paddle1 if powerup.affected_paddle == paddle1 else paddle2
                x_pos = 20 if paddle == paddle1 else WINDOW_WIDTH - 220
                
                # Background
                bg_rect = pygame.Rect(x_pos, y_offset, 200, 50)
                pygame.draw.rect(screen, (40, 40, 40), bg_rect)
                pygame.draw.rect(screen, WHITE, bg_rect, 2)
                
                # Power-up name
                name_map = {
                    "speed_boost": "Speed Boost",
                    "large_paddle": "Large Paddle",
                    "slow_ball": "Slow Ball"
                }
                name = self.font.render(name_map.get(powerup.type, "Power-Up"), True, WHITE)
                screen.blit(name, (x_pos + 10, y_offset + 5))
                
                # Timer bar
                elapsed = pygame.time.get_ticks() - powerup.start_time
                duration = powerup.TYPES[powerup.type]["duration"]
                progress = 1 - (elapsed / duration)
                
                bar_width = 180
                bar_height = 10
                bar_x = x_pos + 10
                bar_y = y_offset + 32
                
                pygame.draw.rect(screen, (60, 60, 60), (bar_x, bar_y, bar_width, bar_height))
                pygame.draw.rect(screen, GREEN, (bar_x, bar_y, int(bar_width * progress), bar_height))
                
                y_offset += 60

class FPSCounter:
    def __init__(self):
        self.font = pygame.font.SysFont(FONT_NAME, 20)
        self.clock = pygame.time.Clock()

    def draw(self, screen, clock):
        fps = int(clock.get_fps())
        color = GREEN if fps >= 55 else YELLOW if fps >= 30 else RED
        fps_text = self.font.render(f"FPS: {fps}", True, color)
        screen.blit(fps_text, (WINDOW_WIDTH - 100, 10))

class SettingsMenu:
    def __init__(self, screen, settings):
        self.screen = screen
        self.settings = settings
        self.font = pygame.font.SysFont(FONT_NAME, 36)
        self.small_font = pygame.font.SysFont(FONT_NAME, 28)
        self.selected = 0
        self.options = [
            "music_volume",
            "sfx_volume",
            "show_fps",
            "fullscreen",
            "theme",
            "back"
        ]

    def draw(self):
        self.screen.fill(GRAY)
        
        title = self.font.render("Settings", True, WHITE)
        self.screen.blit(title, title.get_rect(center=(WINDOW_WIDTH // 2, 100)))
        
        y = 200
        for i, option in enumerate(self.options):
            color = YELLOW if i == self.selected else WHITE
            
            if option == "music_volume":
                vol = int(self.settings.get("music_volume", 0.5) * 100)
                text = f"Music Volume: {vol}%"
            elif option == "sfx_volume":
                vol = int(self.settings.get("sfx_volume", 0.7) * 100)
                text = f"SFX Volume: {vol}%"
            elif option == "show_fps":
                val = "ON" if self.settings.get("show_fps", False) else "OFF"
                text = f"Show FPS: {val}"
            elif option == "fullscreen":
                val = "ON" if self.settings.get("fullscreen", False) else "OFF"
                text = f"Fullscreen: {val}"
            elif option == "theme":
                theme = self.settings.get("theme", "classic").title()
                text = f"Theme: {theme}"
            elif option == "back":
                text = "Back to Menu"
            
            rendered = self.small_font.render(text, True, color)
            self.screen.blit(rendered, rendered.get_rect(center=(WINDOW_WIDTH // 2, y)))
            y += 60
        
        hint = self.small_font.render("Arrow Keys: Navigate | Left/Right: Adjust | Enter: Select", True, WHITE)
        self.screen.blit(hint, hint.get_rect(center=(WINDOW_WIDTH // 2, WINDOW_HEIGHT - 50)))

    def handle_input(self, event):
        if event.type == pygame.KEYDOWN:
            if event.key == pygame.K_UP:
                self.selected = (self.selected - 1) % len(self.options)
            elif event.key == pygame.K_DOWN:
                self.selected = (self.selected + 1) % len(self.options)
            elif event.key == pygame.K_LEFT:
                self.adjust_value(-1)
            elif event.key == pygame.K_RIGHT:
                self.adjust_value(1)
            elif event.key == pygame.K_RETURN:
                if self.options[self.selected] == "back":
                    return "back"
            elif event.key == pygame.K_ESCAPE:
                return "back"
        return None

    def adjust_value(self, direction):
        option = self.options[self.selected]
        
        if option == "music_volume":
            current = self.settings.get("music_volume", 0.5)
            new_val = max(0, min(1, current + direction * 0.1))
            self.settings.set("music_volume", new_val)
            pygame.mixer.music.set_volume(new_val)
        
        elif option == "sfx_volume":
            current = self.settings.get("sfx_volume", 0.7)
            new_val = max(0, min(1, current + direction * 0.1))
            self.settings.set("sfx_volume", new_val)
        
        elif option == "show_fps":
            current = self.settings.get("show_fps", False)
            self.settings.set("show_fps", not current)
        
        elif option == "fullscreen":
            current = self.settings.get("fullscreen", False)
            self.settings.set("fullscreen", not current)
        
        elif option == "theme":
            themes = ["classic", "neon", "retro", "ocean"]
            current = self.settings.get("theme", "classic")
            idx = themes.index(current) if current in themes else 0
            new_idx = (idx + direction) % len(themes)
            self.settings.set("theme", themes[new_idx])
