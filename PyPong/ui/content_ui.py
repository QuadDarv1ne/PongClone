"""UI components for campaign, challenges, and mini-games"""
import pygame
from PyPong.core.config import *

class CampaignUI:
    """UI for campaign mode"""
    def __init__(self, screen, campaign_manager):
        self.screen = screen
        self.campaign = campaign_manager
        self.font = pygame.font.SysFont(FONT_NAME, 32)
        self.small_font = pygame.font.SysFont(FONT_NAME, 24)
        self.title_font = pygame.font.SysFont(FONT_NAME, 48)
        self.selected_level = 0
        self.scroll_offset = 0

    def draw_level_select(self):
        """Draw level selection screen"""
        self.screen.fill(GRAY)
        
        # Title
        title = self.title_font.render("Campaign", True, WHITE)
        self.screen.blit(title, title.get_rect(center=(WINDOW_WIDTH // 2, 50)))
        
        # Progress
        completion = self.campaign.get_completion_percentage()
        stars = self.campaign.get_total_stars()
        progress_text = self.small_font.render(
            f"Progress: {completion:.0f}% | Stars: {stars}/{len(self.campaign.levels) * 3}",
            True, YELLOW
        )
        self.screen.blit(progress_text, progress_text.get_rect(center=(WINDOW_WIDTH // 2, 100)))
        
        # Levels
        unlocked_levels = self.campaign.get_unlocked_levels()
        y = 160
        
        for i, level in enumerate(unlocked_levels):
            color = YELLOW if i == self.selected_level else WHITE
            if level.completed:
                color = GREEN
            
            # Level name and difficulty
            level_text = self.font.render(
                f"{level.id}. {level.name} [{level.difficulty}]",
                True, color
            )
            self.screen.blit(level_text, (100, y))
            
            # Stars
            star_x = WINDOW_WIDTH - 200
            for s in range(3):
                star_color = YELLOW if s < level.stars else (60, 60, 60)
                pygame.draw.polygon(self.screen, star_color, [
                    (star_x + s * 30 + 10, y + 5),
                    (star_x + s * 30 + 13, y + 15),
                    (star_x + s * 30 + 23, y + 15),
                    (star_x + s * 30 + 15, y + 22),
                    (star_x + s * 30 + 18, y + 32),
                    (star_x + s * 30 + 10, y + 26),
                    (star_x + s * 30 + 2, y + 32),
                    (star_x + s * 30 + 5, y + 22),
                    (star_x + s * 30 - 3, y + 15),
                    (star_x + s * 30 + 7, y + 15),
                ])
            
            y += 50
        
        # Controls hint
        hint = self.small_font.render(
            "Arrow Keys: Navigate | ENTER: Start Level | ESC: Back",
            True, WHITE
        )
        self.screen.blit(hint, hint.get_rect(center=(WINDOW_WIDTH // 2, WINDOW_HEIGHT - 40)))

    def draw_level_briefing(self, level):
        """Draw level briefing before starting"""
        self.screen.fill(GRAY)
        
        # Level info
        title = self.title_font.render(f"Level {level.id}: {level.name}", True, WHITE)
        self.screen.blit(title, title.get_rect(center=(WINDOW_WIDTH // 2, 100)))
        
        desc = self.font.render(level.description, True, WHITE)
        self.screen.blit(desc, desc.get_rect(center=(WINDOW_WIDTH // 2, 180)))
        
        diff = self.small_font.render(f"Difficulty: {level.difficulty}", True, YELLOW)
        self.screen.blit(diff, diff.get_rect(center=(WINDOW_WIDTH // 2, 240)))
        
        # Modifiers
        y = 300
        mod_title = self.font.render("Modifiers:", True, WHITE)
        self.screen.blit(mod_title, (150, y))
        y += 50
        
        for key, value in level.modifiers.items():
            mod_text = self.small_font.render(f"• {key}: {value}", True, LIGHT_BLUE)
            self.screen.blit(mod_text, (180, y))
            y += 35
        
        # Objectives
        y += 20
        obj_title = self.font.render("Objectives:", True, WHITE)
        self.screen.blit(obj_title, (150, y))
        y += 50
        
        for obj in level.objectives:
            obj_text = self.small_font.render(f"• {obj}", True, GREEN)
            self.screen.blit(obj_text, (180, y))
            y += 35
        
        # Start hint
        start = self.font.render("Press ENTER to Start", True, GREEN)
        self.screen.blit(start, start.get_rect(center=(WINDOW_WIDTH // 2, WINDOW_HEIGHT - 60)))

    def draw_level_complete(self, level, stars, time_taken):
        """Draw level completion screen"""
        self.screen.fill(GRAY)
        
        title = self.title_font.render("Level Complete!", True, GREEN)
        self.screen.blit(title, title.get_rect(center=(WINDOW_WIDTH // 2, 150)))
        
        # Stars earned
        star_text = self.font.render(f"Stars Earned: {stars}/3", True, YELLOW)
        self.screen.blit(star_text, star_text.get_rect(center=(WINDOW_WIDTH // 2, 250)))
        
        # Draw stars
        star_x = WINDOW_WIDTH // 2 - 60
        star_y = 300
        for s in range(3):
            star_color = YELLOW if s < stars else (60, 60, 60)
            size = 40
            pygame.draw.polygon(self.screen, star_color, [
                (star_x + s * 60 + size//2, star_y),
                (star_x + s * 60 + size//2 + 5, star_y + 15),
                (star_x + s * 60 + size//2 + 20, star_y + 15),
                (star_x + s * 60 + size//2 + 8, star_y + 25),
                (star_x + s * 60 + size//2 + 12, star_y + 40),
                (star_x + s * 60 + size//2, star_y + 32),
                (star_x + s * 60 + size//2 - 12, star_y + 40),
                (star_x + s * 60 + size//2 - 8, star_y + 25),
                (star_x + s * 60 + size//2 - 20, star_y + 15),
                (star_x + s * 60 + size//2 - 5, star_y + 15),
            ])
        
        # Time
        time_text = self.small_font.render(f"Time: {time_taken:.1f}s", True, WHITE)
        self.screen.blit(time_text, time_text.get_rect(center=(WINDOW_WIDTH // 2, 400)))
        
        # Continue hint
        continue_text = self.font.render("Press ENTER to Continue", True, WHITE)
        self.screen.blit(continue_text, continue_text.get_rect(center=(WINDOW_WIDTH // 2, 500)))

    def handle_input(self, event):
        """Handle input for level selection"""
        if event.type == pygame.KEYDOWN:
            unlocked_levels = self.campaign.get_unlocked_levels()
            
            if event.key == pygame.K_UP:
                self.selected_level = max(0, self.selected_level - 1)
            elif event.key == pygame.K_DOWN:
                self.selected_level = min(len(unlocked_levels) - 1, self.selected_level + 1)
            elif event.key == pygame.K_RETURN:
                if unlocked_levels:
                    return unlocked_levels[self.selected_level]
            elif event.key == pygame.K_ESCAPE:
                return "back"
        return None


class ChallengesUI:
    """UI for challenges"""
    def __init__(self, screen, challenge_manager):
        self.screen = screen
        self.challenges = challenge_manager
        self.font = pygame.font.SysFont(FONT_NAME, 28)
        self.small_font = pygame.font.SysFont(FONT_NAME, 22)
        self.title_font = pygame.font.SysFont(FONT_NAME, 48)

    def draw(self):
        """Draw challenges screen"""
        self.screen.fill(GRAY)
        
        title = self.title_font.render("Challenges", True, WHITE)
        self.screen.blit(title, title.get_rect(center=(WINDOW_WIDTH // 2, 50)))
        
        active = self.challenges.get_active_challenges()
        
        # Daily challenges
        y = 130
        daily_title = self.font.render("Daily Challenges", True, YELLOW)
        self.screen.blit(daily_title, (50, y))
        y += 50
        
        for challenge in active['daily']:
            self._draw_challenge(challenge, 70, y)
            y += 100
        
        # Weekly challenges
        y += 20
        weekly_title = self.font.render("Weekly Challenges", True, GREEN)
        self.screen.blit(weekly_title, (50, y))
        y += 50
        
        for challenge in active['weekly']:
            self._draw_challenge(challenge, 70, y)
            y += 100
        
        # Back hint
        hint = self.small_font.render("Press ESC to go back", True, WHITE)
        self.screen.blit(hint, hint.get_rect(center=(WINDOW_WIDTH // 2, WINDOW_HEIGHT - 30)))

    def _draw_challenge(self, challenge, x, y):
        """Draw a single challenge"""
        # Background
        bg_rect = pygame.Rect(x, y, WINDOW_WIDTH - 140, 80)
        pygame.draw.rect(self.screen, (40, 40, 40), bg_rect)
        pygame.draw.rect(self.screen, WHITE, bg_rect, 2)
        
        # Name and description
        name = self.font.render(challenge.name, True, WHITE)
        self.screen.blit(name, (x + 10, y + 10))
        
        desc = self.small_font.render(challenge.description, True, (200, 200, 200))
        self.screen.blit(desc, (x + 10, y + 40))
        
        # Progress bar
        progress_width = WINDOW_WIDTH - 180
        progress_height = 15
        progress_x = x + 10
        progress_y = y + 65
        
        # Background bar
        pygame.draw.rect(self.screen, (60, 60, 60), 
                        (progress_x, progress_y, progress_width, progress_height))
        
        # Progress fill
        progress_percent = min(1.0, challenge.progress / challenge.target)
        fill_width = int(progress_width * progress_percent)
        color = GREEN if challenge.completed else YELLOW
        pygame.draw.rect(self.screen, color,
                        (progress_x, progress_y, fill_width, progress_height))
        
        # Progress text
        progress_text = self.small_font.render(
            f"{challenge.progress}/{challenge.target}",
            True, WHITE
        )
        self.screen.blit(progress_text, (progress_x + progress_width + 10, progress_y - 2))
        
        # Reward
        if challenge.completed:
            reward_text = self.small_font.render(f"✓ +{challenge.reward} pts", True, GREEN)
        else:
            reward_text = self.small_font.render(f"Reward: {challenge.reward} pts", True, YELLOW)
        self.screen.blit(reward_text, (x + progress_width - 150, y + 10))


class MiniGameUI:
    """UI for mini-games"""
    def __init__(self, screen, minigame_manager):
        self.screen = screen
        self.minigames = minigame_manager
        self.font = pygame.font.SysFont(FONT_NAME, 32)
        self.small_font = pygame.font.SysFont(FONT_NAME, 24)
        self.title_font = pygame.font.SysFont(FONT_NAME, 48)
        self.selected = 0
        self.minigame_list = [
            ('target_practice', 'Target Practice', 'Hit as many targets as possible'),
            ('breakout', 'Breakout', 'Break all the bricks'),
            ('survival', 'Survival', 'Survive as long as possible'),
            ('keep_up', 'Keep Up', 'Don\'t let the ball touch the bottom'),
            ('precision', 'Precision', 'Hit the sweet spot for bonus points'),
        ]

    def draw_select(self):
        """Draw mini-game selection screen"""
        self.screen.fill(GRAY)
        
        title = self.title_font.render("Mini-Games", True, WHITE)
        self.screen.blit(title, title.get_rect(center=(WINDOW_WIDTH // 2, 50)))
        
        y = 150
        for i, (key, name, desc) in enumerate(self.minigame_list):
            color = YELLOW if i == self.selected else WHITE
            
            name_text = self.font.render(f"{i+1}. {name}", True, color)
            self.screen.blit(name_text, (150, y))
            
            desc_text = self.small_font.render(desc, True, (200, 200, 200))
            self.screen.blit(desc_text, (180, y + 40))
            
            y += 90
        
        hint = self.small_font.render(
            "Arrow Keys: Navigate | ENTER: Start | ESC: Back",
            True, WHITE
        )
        self.screen.blit(hint, hint.get_rect(center=(WINDOW_WIDTH // 2, WINDOW_HEIGHT - 40)))

    def draw_playing(self, minigame):
        """Draw mini-game HUD"""
        # Score
        score_text = self.font.render(f"Score: {minigame.score}", True, WHITE)
        self.screen.blit(score_text, (20, 20))
        
        # Timer
        if minigame.time_limit:
            remaining = minigame.get_remaining_time()
            timer_text = self.font.render(f"Time: {remaining:.1f}s", True, WHITE)
            self.screen.blit(timer_text, (WINDOW_WIDTH - 200, 20))

    def draw_complete(self, minigame):
        """Draw mini-game completion screen"""
        overlay = pygame.Surface((WINDOW_WIDTH, WINDOW_HEIGHT))
        overlay.set_alpha(200)
        overlay.fill(BLACK)
        self.screen.blit(overlay, (0, 0))
        
        title = self.title_font.render("Complete!", True, GREEN)
        self.screen.blit(title, title.get_rect(center=(WINDOW_WIDTH // 2, 200)))
        
        score_text = self.font.render(f"Final Score: {minigame.score}", True, YELLOW)
        self.screen.blit(score_text, score_text.get_rect(center=(WINDOW_WIDTH // 2, 300)))
        
        continue_text = self.small_font.render("Press ENTER to Continue", True, WHITE)
        self.screen.blit(continue_text, continue_text.get_rect(center=(WINDOW_WIDTH // 2, 400)))

    def handle_input(self, event):
        """Handle input for mini-game selection"""
        if event.type == pygame.KEYDOWN:
            if event.key == pygame.K_UP:
                self.selected = max(0, self.selected - 1)
            elif event.key == pygame.K_DOWN:
                self.selected = min(len(self.minigame_list) - 1, self.selected + 1)
            elif event.key == pygame.K_RETURN:
                return self.minigame_list[self.selected][0]
            elif event.key == pygame.K_ESCAPE:
                return "back"
        return None
