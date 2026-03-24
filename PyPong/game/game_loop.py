"""
Main game loop manager
"""
from random import randint
from typing import Any, Optional, Union

import pygame

from PyPong.core.config import (
    DIFFICULTY_LEVELS,
    MAX_PARTICLES,
    MAX_TRAILS,
    PARTICLES_PER_HIT,
    TRAIL_SPAWN_CHANCE,
    WINDOW_HEIGHT,
    WINDOW_WIDTH,
)
from PyPong.core.entities import Ball, Paddle, PowerUp
from PyPong.core.entity_pools import get_ball_pool, get_powerup_pool
from PyPong.core.event_bus import GameEvent, get_event_bus
from PyPong.core.game_state import GameState, GameStateManager
from PyPong.core.logger import logger
from PyPong.game.collision_manager import CollisionManager
from PyPong.game.input_handler import InputHandler
from PyPong.ui.accessibility import VisualIndicator
from PyPong.ui.effects import Particle, ParticlePool, Trail


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

        # Event bus
        self.event_bus = get_event_bus()

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
        self.visual_indicators: Optional[VisualIndicator] = None

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
        self.visual_indicators = VisualIndicator(WINDOW_WIDTH, WINDOW_HEIGHT)

    def init_game_objects(self) -> None:
        """Инициализировать игровые объекты"""
        is_ai = self.state_manager.game_mode == "ai"

        self.paddle1 = Paddle(1, is_ai=False, color=self.theme.paddle1_color)
        self.paddle2 = Paddle(2, is_ai=is_ai, color=self.theme.paddle2_color)

        # Use entity pool for ball
        self.ball = get_ball_pool().acquire()
        self.ball.image.fill(self.theme.ball_color)

        # Используем RenderUpdates для оптимизации рендеринга
        self.all_sprites = pygame.sprite.RenderUpdates(self.paddle1, self.paddle2, self.ball)
        self.powerups = pygame.sprite.RenderUpdates()

        # Set AI difficulty
        if is_ai:
            difficulty = self.state_manager.difficulty
            self.paddle2.set_speed(DIFFICULTY_LEVELS[difficulty]["ai_speed"])

        # Reset input state
        self.input_handler.reset_input()

    def cleanup_game_objects(self) -> None:
        """Очистить игровые объекты"""
        # Return balls to pool
        if self.all_sprites:
            ball_pool = get_ball_pool()
            powerup_pool = get_powerup_pool()
            for sprite in list(self.all_sprites.sprites()):
                if isinstance(sprite, Ball):
                    ball_pool.release(sprite)
                elif isinstance(sprite, PowerUp):
                    powerup_pool.release(sprite)
            self.all_sprites.empty()

        if self.powerups:
            powerup_pool = get_powerup_pool()
            for powerup in list(self.powerups.sprites()):
                powerup_pool.release(powerup)
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
                self.ball.rect.centerx, self.ball.rect.centery, self.ball.velocity_x, self.ball.velocity_y
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
        if len(self.trails) < MAX_TRAILS and randint(1, TRAIL_SPAWN_CHANCE) == 1:
            trail = Trail(int(self.ball.rect.centerx), int(self.ball.rect.centery))
            self.trails.add(trail)

    def _handle_paddle_collisions(self) -> None:
        """Обработать коллизии с ракетками"""
        for paddle in [self.paddle1, self.paddle2]:
            if self.collision_manager.check_paddle_collision(self.ball, paddle):
                should_play_sound, _ = self.collision_manager.handle_paddle_collision(self.ball, paddle)

                if should_play_sound:
                    self.audio.play_sound("beep")
                    self._create_particles(self.ball.rect.centerx, self.ball.rect.centery, self.theme.accent_color)
                    intensity = self.collision_manager.get_shake_intensity(is_goal=False)
                    self.shake.start(*intensity)

                    # Visual indicator for deaf/hard of hearing players
                    if hasattr(self, 'accessibility') and self.accessibility.audio_cues:
                        self._show_visual_indicator("HIT!", self.ball.rect.center)

                    # Publish event
                    self.event_bus.publish(
                        GameEvent.BALL_HIT_PADDLE,
                        {"paddle": 1 if paddle == self.paddle1 else 2, "ball_pos": self.ball.rect.center},
                    )

    def _check_scoring(self) -> None:
        """Проверить забитый гол"""
        scorer = self.collision_manager.check_score(self.ball, WINDOW_WIDTH)

        if scorer:
            self.state_manager.add_score(scorer)
            self.audio.play_sound("score")
            self.goal_anim.start(scorer)

            intensity = self.collision_manager.get_shake_intensity(is_goal=True)
            self.shake.start(*intensity)

            # Publish event
            self.event_bus.publish(GameEvent.GOAL_SCORED, {"player": scorer, "score": self.state_manager.scores})

            # Visual indicator for goal
            if self.visual_indicators:
                goal_text = f"GOAL! P{scorer}"
                goal_pos = (WINDOW_WIDTH // 2 - 50, WINDOW_HEIGHT // 2 - 20)
                self.visual_indicators.add_indicator(goal_text, goal_pos, color=(0, 255, 0), duration=90)

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
                    self._create_particles(powerup.rect.centerx, powerup.rect.centery, self.theme.accent_color)
                    self._handle_powerup_effect(powerup, paddle)
                    # Publish event
                    self.event_bus.publish(
                        GameEvent.POWERUP_COLLECTED,
                        {"type": powerup.type, "player": 1 if paddle == self.paddle1 else 2},
                    )

            # Collision with ball (for slow_ball)
            if self.collision_manager.check_ball_powerup_collision(powerup, self.ball):
                powerup.apply_to_ball(self.ball)
                self.audio.play_sound("powerup")
                self._create_particles(powerup.rect.centerx, powerup.rect.centery, self.theme.accent_color)
                powerup.deactivate()

        # Update powerups
        self.powerups.update()

    def _handle_powerup_effect(self, powerup: PowerUp, collector: Paddle) -> None:
        """Обработать эффект power-up с визуальным индикатором"""
        player_num = 1 if collector == self.paddle1 else 2

        # Map powerup types to short display names
        powerup_names = {
            "speed_boost": "SPEED!",
            "large_paddle": "BIG!",
            "slow_ball": "SLOW!",
            "multi_ball": "x2 BALLS!",
            "shrink_opponent": "SHRINK!",
        }

        if powerup.type == "multi_ball":
            self._create_extra_ball()
        elif powerup.type == "shrink_opponent":
            opponent = self.paddle2 if collector == self.paddle1 else self.paddle1
            opponent.resize(50)
            pygame.time.set_timer(pygame.USEREVENT + 1, 5000, loops=1)  # type: ignore[attr-defined]

        # Show visual indicator for powerup collection
        if self.visual_indicators:
            display_name = powerup_names.get(powerup.type, powerup.type.upper())
            indicator_text = f"P{player_num}: {display_name}"
            x_pos = WINDOW_WIDTH // 4 if player_num == 1 else 3 * WINDOW_WIDTH // 4
            self.visual_indicators.add_indicator(indicator_text, (x_pos, WINDOW_HEIGHT // 4), color=(255, 255, 0), duration=120)

    def _create_extra_ball(self) -> None:
        """Создать дополнительный мяч (максимум 2)"""
        balls = [s for s in self.all_sprites if isinstance(s, Ball)]
        if len(balls) >= 2:
            return
        # Use entity pool for extra ball
        new_ball = get_ball_pool().acquire()
        new_ball.rect.center = self.ball.rect.center
        new_ball.velocity_x = -self.ball.velocity_x
        new_ball.velocity_y = self.ball.velocity_y
        new_ball.image.fill(self.theme.ball_color)
        self.all_sprites.add(new_ball)

    def _create_particles(self, x: float, y: float, color: tuple) -> None:
        """Создать частицы"""
        if isinstance(self.particles, ParticlePool):
            self.particles.emit(int(x), int(y), color, PARTICLES_PER_HIT)
        elif len(self.particles) < MAX_PARTICLES:
            for _ in range(PARTICLES_PER_HIT):
                particle = Particle(int(x), int(y), color)
                self.particles.add(particle)

    def _show_visual_indicator(self, text: str, position: Tuple[int, int], color: Tuple[int, int, int] = (255, 255, 0)) -> None:
        """Показать визуальный индикатор для событий"""
        if self.visual_indicators:
            self.visual_indicators.add_indicator(text, position, color, duration=60)

    def _update_visual_indicators(self) -> None:
        """Обновить визуальные индикаторы"""
        if self.visual_indicators:
            self.visual_indicators.update()

    def _update_effects(self) -> None:
        """Обновить эффекты"""
        if self.particles:
            self.particles.update()
        if self.trails:
            self.trails.update()
        if self.shake:
            self.shake.update()
        if self.goal_anim:
            self.goal_anim.update()
        if self.visual_indicators:
            self._update_visual_indicators()

    def spawn_powerup(self, x: Optional[int] = None, y: Optional[int] = None) -> Optional[PowerUp]:
        """
        Spawn a power-up from the pool

        Args:
            x: X position (random if not specified)
            y: Y position (random if not specified)

        Returns:
            PowerUp instance or None if pool is exhausted
        """
        powerup = get_powerup_pool().acquire()
        if powerup:
            # Set position
            if x is None:
                x = randint(WINDOW_WIDTH // 4, 3 * WINDOW_WIDTH // 4)
            if y is None:
                y = randint(50, WINDOW_HEIGHT - 50)
            powerup.rect.center = (x, y)

            # Add to sprite groups
            if self.powerups:
                self.powerups.add(powerup)
            if self.all_sprites:
                self.all_sprites.add(powerup)

            # Publish event
            self.event_bus.publish(GameEvent.POWERUP_SPAWNED, {"position": (x, y), "type": powerup.type})

            logger.debug(f"PowerUp spawned at ({x}, {y})")
        return powerup
