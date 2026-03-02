"""
Main game loop manager
"""
import pygame
from typing import Optional, Any, Tuple, Union

from PyPong.core.game_state import GameState, GameStateManager
from PyPong.game.input_handler import InputHandler
from PyPong.game.collision_manager import CollisionManager
from PyPong.core.entities import Paddle, Ball, PowerUp
from PyPong.core.config import (
    WINDOW_WIDTH, WINDOW_HEIGHT,
    MAX_TRAILS, TRAIL_SPAWN_CHANCE,
    POWERUP_SPAWN_CHANCE, MAX_PARTICLES, PARTICLES_PER_HIT,
    DIFFICULTY_LEVELS,
)
from PyPong.ui.effects import Trail, Particle, ParticlePool
from PyPong.core.logger import logger, log_exception


class GameLoop:
    """
    Управляет основным игровым циклом.
    """
    
    def __init__(
        self,
        state_manager: GameStateManager,
        input_handler: InputHandler,
        collision_manager: CollisionManager,
        audio: Any,
        settings: Any,
        theme: Any,
        gamepad: Any,
        touch: Any,
    ):
        self.state_manager = state_manager
        self.input_handler = input_handler
        self.collision_manager = collision_manager
        self.audio = audio
        self.settings = settings
        self.theme = theme
        self.gamepad = gamepad
        self.touch = touch
        
        # Game objects
        self.paddle1: Optional[Paddle] = None
        self.paddle2: Optional[Paddle] = None
        self.ball: Optional[Ball] = None
        self.all_sprites: Optional[pygame.sprite.Group] = None
        self.powerups: Optional[pygame.sprite.Group] = None

        # Effects
        self.particles: Optional[Union[pygame.sprite.Group, ParticlePool]] = None
        self.trails: Optional[pygame.sprite.Group] = None
        self.shake: Optional[Any] = None
        self.goal_anim: Optional[Any] = None
    
    def set_effects(
        self,
        particles: Union[pygame.sprite.Group, ParticlePool],
        trails: pygame.sprite.Group,
        shake: Any,
        goal_anim: Any,
    ) -> None:
        """Установить эффекты"""
        self.particles = particles
        self.trails = trails
        self.shake = shake
        self.goal_anim = goal_anim
    
    def init_game_objects(self) -> None:
        """Инициализировать игровые объекты"""
        is_ai = self.state_manager.game_mode == "ai"
        
        self.paddle1 = Paddle(1, is_ai=False, color=self.theme.paddle1_color)
        self.paddle2 = Paddle(2, is_ai=is_ai, color=self.theme.paddle2_color)
        self.ball = Ball()
        self.ball.image.fill(self.theme.ball_color)
        
        self.all_sprites = pygame.sprite.Group(
            self.paddle1, 
            self.paddle2, 
            self.ball
        )
        self.powerups = pygame.sprite.Group()
        
        # Set AI difficulty
        if is_ai:
            difficulty = self.state_manager.difficulty
            from PyPong.core.config import DIFFICULTY_LEVELS
            self.paddle2.set_speed(DIFFICULTY_LEVELS[difficulty]["ai_speed"])
        
        # Reset input state
        self.input_handler.reset_input()
    
    def cleanup_game_objects(self) -> None:
        """Очистить игровые объекты"""
        if self.all_sprites:
            self.all_sprites.empty()
        if self.powerups:
            self.powerups.empty()
        if self.particles:
            if isinstance(self.particles, ParticlePool):
                self.particles.clear()
        if self.trails:
            self.trails.empty()

        self.paddle1 = None
        self.paddle2 = None
        self.ball = None
        self.all_sprites = None
        self.powerups = None
        self.particles = None
    
    def update(self) -> None:
        """
        Обновить игровую логику.
        Вызывается каждый кадр когда состояние PLAYING
        """
        if self.state_manager.state != GameState.PLAYING:
            return
        
        self._update_paddles()
        self._update_ball()
        self._update_effects()
    
    def _update_paddles(self) -> None:
        """Обновить движение ракеток"""
        # Apply touch input
        if self.settings.get("touch_controls", False):
            self._apply_touch_input()
        
        # Apply gamepad input
        self._apply_gamepad_input()
        
        # Move paddle 1
        input_state = self.input_handler.get_input_state()
        self.paddle1.move(input_state["up1"], input_state["down1"])
        
        # Move paddle 2
        if self.state_manager.game_mode == "ai":
            predicted_y = self.paddle2.predict_ball_position(
                self.ball.rect.centerx,
                self.ball.rect.centery,
                self.ball.velocity_x,
                self.ball.velocity_y
            )
            self.paddle2.move(False, False, predicted_y)
        else:
            self.paddle2.move(input_state["up2"], input_state["down2"])
    
    def _apply_touch_input(self) -> None:
        """Применить сенсорный ввод"""
        touch_input1 = self.touch.get_input(1)
        input_state = self.input_handler.get_input_state()
        input_state["up1"] = input_state["up1"] or touch_input1["up"]
        input_state["down1"] = input_state["down1"] or touch_input1["down"]
        
        if self.state_manager.game_mode == "pvp":
            touch_input2 = self.touch.get_input(2)
            input_state["up2"] = input_state["up2"] or touch_input2["up"]
            input_state["down2"] = input_state["down2"] or touch_input2["down"]
        
        # Update input handler state
        for key, value in input_state.items():
            self.input_handler.set_input(key, value)
    
    def _apply_gamepad_input(self) -> None:
        """Применить ввод с геймпада"""
        input_state = self.input_handler.get_input_state()
        
        if self.gamepad.has_gamepad(1):
            gp_input = self.gamepad.get_input(1)
            input_state["up1"] = input_state["up1"] or gp_input["up"]
            input_state["down1"] = input_state["down1"] or gp_input["down"]
        
        if self.gamepad.has_gamepad(2) and self.state_manager.game_mode == "pvp":
            gp_input = self.gamepad.get_input(2)
            input_state["up2"] = input_state["up2"] or gp_input["up"]
            input_state["down2"] = input_state["down2"] or gp_input["down"]
        
        for key, value in input_state.items():
            self.input_handler.set_input(key, value)
    
    def _update_ball(self) -> None:
        """Обновить мяч и обработки коллизий"""
        # Move ball
        self.ball.move()
        
        # Create trail
        self._spawn_trail()
        
        # Wall collision
        self.ball.bounce_wall()
        
        # Paddle collisions
        self._handle_paddle_collisions()
        
        # Check scoring
        self._check_scoring()
        
        # Power-up collisions
        self._handle_powerup_collisions()
    
    def _spawn_trail(self) -> None:
        """Создать шлейф мяча"""
        from random import randint
        if len(self.trails) < MAX_TRAILS:
            if randint(1, TRAIL_SPAWN_CHANCE) == 1:
                from PyPong.ui.effects import Trail
                trail = Trail(self.ball.rect.centerx, self.ball.rect.centery)
                self.trails.add(trail)
    
    def _handle_paddle_collisions(self) -> None:
        """Обработать коллизии с ракетками"""
        for paddle in [self.paddle1, self.paddle2]:
            if self.collision_manager.check_paddle_collision(self.ball, paddle):
                should_play_sound, _ = self.collision_manager.handle_paddle_collision(
                    self.ball, 
                    paddle
                )
                
                if should_play_sound:
                    self.audio.play_sound("beep")
                    self._create_particles(
                        self.ball.rect.centerx, 
                        self.ball.rect.centery, 
                        self.theme.accent_color
                    )
                    intensity = self.collision_manager.get_shake_intensity(is_goal=False)
                    self.shake.start(*intensity)
    
    def _check_scoring(self) -> None:
        """Проверить забитый гол"""
        scorer = self.collision_manager.check_score(self.ball, WINDOW_WIDTH)
        
        if scorer:
            self.state_manager.add_score(scorer)
            self.audio.play_sound("score")
            self.goal_anim.start(scorer)
            
            intensity = self.collision_manager.get_shake_intensity(is_goal=True)
            self.shake.start(*intensity)
            
            if self.state_manager.state == GameState.PLAYING:
                self.ball.reset_ball()
    
    def _handle_powerup_collisions(self) -> None:
        """Обработать коллизии с power-up"""
        for powerup in self.powerups:
            # Collision with paddles
            for paddle in [self.paddle1, self.paddle2]:
                if self.collision_manager.check_powerup_collision(powerup, paddle):
                    powerup.activate(paddle)
                    self.audio.play_sound("powerup")
                    self._create_particles(
                        powerup.rect.centerx, 
                        powerup.rect.centery, 
                        self.theme.accent_color
                    )
                    self._handle_powerup_effect(powerup, paddle)
            
            # Collision with ball (for slow_ball)
            if self.collision_manager.check_ball_powerup_collision(powerup, self.ball):
                powerup.apply_to_ball(self.ball)
                self.audio.play_sound("powerup")
                self._create_particles(
                    powerup.rect.centerx, 
                    powerup.rect.centery, 
                    self.theme.accent_color
                )
                powerup.deactivate()
        
        # Update powerups
        self.powerups.update()
    
    def _handle_powerup_effect(self, powerup: PowerUp, collector: Paddle) -> None:
        """Обработать эффект power-up"""
        if powerup.type == "multi_ball":
            self._create_extra_ball()
        elif powerup.type == "shrink_opponent":
            opponent = self.paddle2 if collector == self.paddle1 else self.paddle1
            opponent.resize(50)
    
    def _create_extra_ball(self) -> None:
        """Создать дополнительный мяч"""
        new_ball = Ball()
        new_ball.rect.center = self.ball.rect.center
        new_ball.velocity_x = -self.ball.velocity_x
        new_ball.velocity_y = self.ball.velocity_y
        new_ball.image.fill(self.theme.ball_color)
        self.all_sprites.add(new_ball)
    
    def _create_particles(self, x: int, y: int, color: tuple) -> None:
        """Создать частицы с использованием ParticlePool"""
        if isinstance(self.particles, ParticlePool):
            # Используем оптимизированный пул
            self.particles.emit(x, y, color, PARTICLES_PER_HIT)
        else:
            # Fallback для обычного sprite.Group
            from random import randint
            if len(self.particles) < MAX_PARTICLES:
                for _ in range(PARTICLES_PER_HIT):
                    particle = Particle(x, y, color)
                    self.particles.add(particle)
    
    def _update_effects(self) -> None:
        """Обновить эффекты"""
        if self.particles:
            # Поддержка как ParticlePool, так и sprite.Group
            if isinstance(self.particles, ParticlePool):
                self.particles.update()
            else:
                self.particles.update()
        if self.trails:
            self.trails.update()
        if self.shake:
            self.shake.update()
        if self.goal_anim:
            self.goal_anim.update()
