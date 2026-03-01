"""Game modifiers that change physics and gameplay"""
import pygame
import math
from random import uniform, choice

class GameModifier:
    """Base class for game modifiers"""
    def __init__(self, name, description):
        self.name = name
        self.description = description
        self.active = True

    def apply_to_ball(self, ball):
        """Apply modifier effect to ball"""
        pass

    def apply_to_paddle(self, paddle):
        """Apply modifier effect to paddle"""
        pass

    def update(self):
        """Update modifier state"""
        pass


class GravityModifier(GameModifier):
    """Adds gravity effect to ball"""
    def __init__(self, strength=0.2):
        super().__init__("Gravity", f"Ball affected by gravity (strength: {strength})")
        self.strength = strength

    def apply_to_ball(self, ball):
        if self.active:
            ball.velocity_y += self.strength


class WindModifier(GameModifier):
    """Adds wind effect that pushes ball horizontally"""
    def __init__(self, strength=0.15, variable=True):
        super().__init__("Wind", "Wind pushes the ball")
        self.base_strength = strength
        self.strength = strength
        self.variable = variable
        self.direction = 1
        self.change_timer = 0
        self.change_interval = 3000  # Change direction every 3 seconds

    def apply_to_ball(self, ball):
        if self.active:
            ball.velocity_x += self.strength * self.direction

    def update(self):
        if self.variable:
            self.change_timer += 16  # Assuming 60 FPS
            if self.change_timer >= self.change_interval:
                self.direction = choice([-1, 1])
                self.strength = uniform(self.base_strength * 0.5, self.base_strength * 1.5)
                self.change_timer = 0


class InvisibleBallModifier(GameModifier):
    """Makes ball invisible periodically"""
    def __init__(self, interval=3000, duration=2000):
        super().__init__("Invisible Ball", "Ball becomes invisible periodically")
        self.interval = interval
        self.duration = duration
        self.timer = 0
        self.invisible = False
        self.original_alpha = 255

    def apply_to_ball(self, ball):
        if self.active:
            self.timer += 16
            
            if not self.invisible and self.timer >= self.interval:
                self.invisible = True
                self.timer = 0
                ball.image.set_alpha(0)
            elif self.invisible and self.timer >= self.duration:
                self.invisible = False
                self.timer = 0
                ball.image.set_alpha(self.original_alpha)

    def is_invisible(self):
        return self.invisible


class SizeModifier(GameModifier):
    """Changes paddle size"""
    def __init__(self, scale=0.6, target_player=1):
        super().__init__("Size Change", f"Paddle size scaled to {scale}x")
        self.scale = scale
        self.target_player = target_player
        self.applied = False

    def apply_to_paddle(self, paddle):
        if self.active and not self.applied and paddle.player_number == self.target_player:
            new_height = int(paddle.original_height * self.scale)
            paddle.resize(new_height)
            self.applied = True


class SpeedModifier(GameModifier):
    """Changes game speed"""
    def __init__(self, ball_speed_multiplier=1.5, paddle_speed_multiplier=1.2):
        super().__init__("Speed Change", "Game speed modified")
        self.ball_multiplier = ball_speed_multiplier
        self.paddle_multiplier = paddle_speed_multiplier
        self.applied = False

    def apply_to_ball(self, ball):
        if self.active and not self.applied:
            ball.speed *= self.ball_multiplier
            current_angle = math.atan2(ball.velocity_y, ball.velocity_x)
            ball.velocity_x = ball.speed * math.cos(current_angle)
            ball.velocity_y = ball.speed * math.sin(current_angle)

    def apply_to_paddle(self, paddle):
        if self.active and not self.applied:
            paddle.speed *= self.paddle_multiplier
            self.applied = True


class CurveModifier(GameModifier):
    """Ball curves in flight"""
    def __init__(self, strength=0.1):
        super().__init__("Curve Ball", "Ball curves during flight")
        self.strength = strength
        self.curve_direction = 1

    def apply_to_ball(self, ball):
        if self.active:
            # Add curve based on horizontal velocity
            if abs(ball.velocity_x) > 2:
                curve = self.strength * self.curve_direction
                ball.velocity_y += curve
                
                # Change curve direction randomly
                if uniform(0, 1) < 0.01:
                    self.curve_direction *= -1


class MultiballModifier(GameModifier):
    """Spawns multiple balls"""
    def __init__(self, ball_count=3):
        super().__init__("Multiball", f"Spawn {ball_count} balls")
        self.ball_count = ball_count
        self.spawned = False

    def spawn_balls(self, original_ball):
        """Create additional balls"""
        from entities import Ball
        new_balls = []
        
        for i in range(self.ball_count - 1):
            ball = Ball()
            ball.rect.center = original_ball.rect.center
            
            # Random angle
            angle = uniform(30, 150) if i % 2 == 0 else uniform(210, 330)
            rad = math.radians(angle)
            ball.velocity_x = ball.speed * math.cos(rad)
            ball.velocity_y = ball.speed * math.sin(rad)
            
            new_balls.append(ball)
        
        self.spawned = True
        return new_balls


class ReverseControlsModifier(GameModifier):
    """Reverses paddle controls"""
    def __init__(self, target_player=2):
        super().__init__("Reverse Controls", "Controls are reversed")
        self.target_player = target_player
        self.reversed = True


class BouncyWallsModifier(GameModifier):
    """Walls bounce ball with extra speed"""
    def __init__(self, bounce_multiplier=1.3):
        super().__init__("Bouncy Walls", "Walls add extra bounce")
        self.bounce_multiplier = bounce_multiplier

    def apply_wall_bounce(self, ball):
        if self.active:
            ball.velocity_y *= self.bounce_multiplier


class SlipperyPaddleModifier(GameModifier):
    """Paddle has momentum/inertia"""
    def __init__(self):
        super().__init__("Slippery Paddle", "Paddle has momentum")
        self.momentum = {}

    def apply_to_paddle(self, paddle):
        if self.active:
            player_id = paddle.player_number
            if player_id not in self.momentum:
                self.momentum[player_id] = 0
            
            # Apply momentum decay
            self.momentum[player_id] *= 0.9


class ModifierManager:
    """Manages active game modifiers"""
    def __init__(self):
        self.modifiers = []

    def add_modifier(self, modifier):
        """Add a modifier"""
        self.modifiers.append(modifier)

    def remove_modifier(self, modifier):
        """Remove a modifier"""
        if modifier in self.modifiers:
            self.modifiers.remove(modifier)

    def clear_modifiers(self):
        """Remove all modifiers"""
        self.modifiers.clear()

    def apply_to_ball(self, ball):
        """Apply all modifiers to ball"""
        for modifier in self.modifiers:
            if modifier.active:
                modifier.apply_to_ball(ball)

    def apply_to_paddle(self, paddle):
        """Apply all modifiers to paddle"""
        for modifier in self.modifiers:
            if modifier.active:
                modifier.apply_to_paddle(paddle)

    def update(self):
        """Update all modifiers"""
        for modifier in self.modifiers:
            modifier.update()

    def get_active_modifiers(self):
        """Get list of active modifier names"""
        return [m.name for m in self.modifiers if m.active]

    def has_modifier(self, modifier_type):
        """Check if specific modifier type is active"""
        return any(isinstance(m, modifier_type) and m.active for m in self.modifiers)
