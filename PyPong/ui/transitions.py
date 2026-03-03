"""
UI transitions for smooth animations
"""
from enum import Enum
from typing import Any, Callable, Optional

import pygame


class TransitionType(Enum):
    """Типы анимаций переходов"""

    FADE_IN = "fade_in"
    FADE_OUT = "fade_out"
    SLIDE_LEFT = "slide_left"
    SLIDE_RIGHT = "slide_right"
    SLIDE_UP = "slide_up"
    SLIDE_DOWN = "slide_down"
    ZOOM_IN = "zoom_in"
    ZOOM_OUT = "zoom_out"


class EasingFunction:
    """Функции плавности для анимаций"""

    @staticmethod
    def linear(t: float) -> float:
        return t

    @staticmethod
    def ease_in(t: float) -> float:
        return t * t

    @staticmethod
    def ease_out(t: float) -> float:
        return t * (2 - t)

    @staticmethod
    def ease_in_out(t: float) -> float:
        if t < 0.5:
            return 2 * t * t
        return -1 + (4 - 2 * t) * t

    @staticmethod
    def bounce(t: float) -> float:
        if t < 1 / 2.75:
            return 7.5625 * t * t
        elif t < 2 / 2.75:
            t -= 1.5 / 2.75
            return 7.5625 * t * t + 0.75
        elif t < 2.5 / 2.75:
            t -= 2.25 / 2.75
            return 7.5625 * t * t + 0.9375
        else:
            t -= 2.625 / 2.75
            return 7.5625 * t * t + 0.984375


class UITransition:
    """
    Анимация перехода для UI.
    """

    def __init__(
        self,
        transition_type: TransitionType = TransitionType.FADE_IN,
        duration: float = 0.3,
        easing: Callable[[float], float] = EasingFunction.ease_in_out,
    ) -> None:
        self.transition_type = transition_type
        self.duration = duration  # секунды
        self.easing = easing

        self.progress = 0.0
        self.running = False
        self.on_complete: Optional[Callable[[], None]] = None

    def start(self) -> None:
        """Запустить анимацию"""
        self.progress = 0.0
        self.running = True

    def update(self, dt: float) -> bool:
        """
        Обновить анимацию.

        Args:
            dt: Время с последнего кадра (секунды)

        Returns:
            bool: True если анимация завершена
        """
        if not self.running:
            return True

        self.progress += dt / self.duration

        if self.progress >= 1.0:
            self.progress = 1.0
            self.running = False
            if self.on_complete:
                self.on_complete()
            return True

        return False

    def get_alpha(self) -> int:
        """Получить текущую прозрачность (0-255)"""
        if self.transition_type in [TransitionType.FADE_IN, TransitionType.FADE_OUT]:
            t = self.easing(self.progress)
            if self.transition_type == TransitionType.FADE_OUT:
                t = 1.0 - t
            return int(255 * t)
        return 255

    def get_offset(self, width: int, height: int) -> tuple:
        """Получить смещение для слайд-переходов"""
        t = self.easing(self.progress)

        if self.transition_type == TransitionType.SLIDE_LEFT:
            return (int(width * (1 - t)), 0)
        elif self.transition_type == TransitionType.SLIDE_RIGHT:
            return (int(-width * (1 - t)), 0)
        elif self.transition_type == TransitionType.SLIDE_UP:
            return (0, int(height * (1 - t)))
        elif self.transition_type == TransitionType.SLIDE_DOWN:
            return (0, int(-height * (1 - t)))

        return (0, 0)

    def get_scale(self) -> float:
        """Получить текущий масштаб для zoom-переходов"""
        t = self.easing(self.progress)

        if self.transition_type == TransitionType.ZOOM_IN:
            return t
        elif self.transition_type == TransitionType.ZOOM_OUT:
            return 2.0 - t

        return 1.0


class TransitionManager:
    """
    Менеджер переходов между экранами.
    """

    def __init__(self) -> None:
        self.active_transition: Optional[UITransition] = None
        self.surface: Optional[pygame.Surface] = None
        self.transition_surface: Optional[pygame.Surface] = None

    def start_transition(
        self,
        transition_type: TransitionType = TransitionType.FADE_IN,
        duration: float = 0.3,
        easing: Callable[[float], float] = EasingFunction.ease_in_out,
    ) -> None:
        """
        Начать переход.

        Args:
            transition_type: Тип перехода
            duration: Длительность в секундах
            easing: Функция плавности
        """
        self.active_transition = UITransition(transition_type, duration, easing)
        self.active_transition.start()

    def update(self, dt: float) -> bool:
        """
        Обновить переход.

        Args:
            dt: Время с последнего кадра (секунды)

        Returns:
            bool: True если переход завершён
        """
        if self.active_transition:
            return self.active_transition.update(dt)
        return True

    def draw(self, screen: pygame.Surface, content_surface: pygame.Surface) -> None:
        """
        Отрисовать переход.

        Args:
            screen: Целевой экран
            content_surface: Поверхность с контентом
        """
        if not self.active_transition:
            screen.blit(content_surface, (0, 0))
            return

        # Применяем эффекты перехода
        alpha = self.active_transition.get_alpha()
        offset = self.active_transition.get_offset(content_surface.get_width(), content_surface.get_height())
        scale = self.active_transition.get_scale()

        # Копируем поверхность для применения эффектов
        temp_surface = content_surface.copy()

        # Применяем масштаб
        if scale != 1.0:
            new_size = (int(temp_surface.get_width() * scale), int(temp_surface.get_height() * scale))
            temp_surface = pygame.transform.scale(temp_surface, new_size)

        # Применяем прозрачность
        if alpha < 255:
            temp_surface.set_alpha(alpha)

        # Отрисовываем со смещением
        screen.blit(temp_surface, offset)

    def is_transitioning(self) -> bool:
        """Проверить активный переход"""
        return self.active_transition is not None and self.active_transition.running
