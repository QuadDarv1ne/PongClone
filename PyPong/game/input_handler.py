"""
Input handler for game events
"""
from typing import Callable, Dict, Optional

from pygame.locals import (
    K_1,
    K_2,
    K_3,
    K_4,
    K_DOWN,
    K_ESCAPE,
    K_F1,
    K_RETURN,
    K_UP,
    K_a,
    K_o,
    K_s,
    K_t,
    K_z,
)

from PyPong.core.game_state import GameState


class InputHandler:
    """
    Обрабатывает ввод пользователя для игры.
    """

    def __init__(self) -> None:
        self.input_state: Dict[str, bool] = {
            "up1": False,
            "down1": False,
            "up2": False,
            "down2": False,
        }

        # State transitions for ESC
        self._escape_transitions: Dict[GameState, Optional[GameState]] = {
            GameState.PLAYING: GameState.PAUSED,
            GameState.PAUSED: GameState.MENU,
            GameState.STATS: GameState.MENU,
            GameState.SETTINGS: GameState.MENU,
            GameState.HELP: GameState.MENU,
            GameState.MODE_SELECT: GameState.MENU,
        }

        # State transitions for ENTER
        self._enter_transitions: Dict[GameState, Optional[GameState]] = {
            GameState.MENU: GameState.MODE_SELECT,
            GameState.MODE_SELECT: GameState.PLAYING,
            GameState.PAUSED: GameState.PLAYING,
            GameState.GAME_OVER: GameState.MENU,
            GameState.TOURNAMENT_COMPLETE: GameState.MENU,
        }

    def get_input_state(self) -> Dict[str, bool]:
        """Получить текущее состояние ввода"""
        return self.input_state.copy()

    def reset_input(self) -> None:
        """Сбросить состояние ввода"""
        self.input_state = {
            "up1": False,
            "down1": False,
            "up2": False,
            "down2": False,
        }

    def set_input(self, key: str, value: bool) -> None:
        """
        Установить состояние клавиши.

        Args:
            key: Название клавиши (up1, down1, up2, down2)
            value: Состояние (нажата/отпущена)
        """
        if key in self.input_state:
            self.input_state[key] = value

    def handle_keydown(self, key: int, current_state: GameState) -> tuple:
        """
        Обработать нажатие клавиши.

        Args:
            key: Код клавиши
            current_state: Текущее состояние игры

        Returns:
            tuple: (new_state, should_quit, action_data)
        """
        # ESC handling
        if key == K_ESCAPE:
            new_state = self._escape_transitions.get(current_state)
            if new_state is None:
                return (current_state, True, {})  # Quit
            return (new_state, False, {})

        # ENTER handling
        if key == K_RETURN:
            new_state = self._enter_transitions.get(current_state)
            if new_state:
                action_data = {
                    "play_music": new_state == GameState.PLAYING,
                    "cleanup": new_state == GameState.MENU and current_state == GameState.GAME_OVER,
                    "reset_tournament": current_state == GameState.TOURNAMENT_COMPLETE,
                }
                return (new_state, False, action_data)
            return (current_state, False, {})

        # Menu shortcuts
        if current_state == GameState.MENU:
            if key == K_s:
                return (GameState.STATS, False, {})
            elif key == K_o:
                return (GameState.SETTINGS, False, {})
            elif key == K_F1:
                return (GameState.HELP, False, {})

        # Mode select keys
        if current_state == GameState.MODE_SELECT:
            return self._handle_mode_select_keys(key)

        # Movement input
        return self._handle_movement_input(key, is_pressed=True)

    def handle_keyup(self, key: int, current_state: GameState) -> tuple:
        """
        Обработать отпускание клавиши.

        Args:
            key: Код клавиши
            current_state: Текущее состояние игры

        Returns:
            tuple: (new_state, should_quit, action_data)
        """
        return self._handle_movement_input(key, is_pressed=False)

    def _handle_mode_select_keys(self, key: int) -> tuple:
        """Обработать клавиши выбора режима"""
        action_data = {}

        if key == K_1:
            action_data["game_mode"] = "ai"
        elif key == K_2:
            action_data["game_mode"] = "pvp"
        elif key == K_3:
            action_data["difficulty"] = "Easy"
        elif key == K_4:
            action_data["difficulty"] = "Medium"
        elif key == K_t:
            action_data["toggle_tournament"] = True

        return (GameState.MODE_SELECT, False, action_data)

    def _handle_movement_input(self, key: int, is_pressed: bool) -> tuple:
        """Обработать ввод движения"""
        key_map = {
            K_a: "up1",
            K_z: "down1",
            K_UP: "up2",
            K_DOWN: "down2",
        }

        if key in key_map:
            self.set_input(key_map[key], is_pressed)

        return (None, False, {})

    def apply_action_data(self, action_data: dict, game_context: dict) -> None:
        """
        Применить данные действия к контексту игры.

        Args:
            action_data: Данные действия от обработчика
            game_context: Контекст игры для обновления
        """
        if "game_mode" in action_data:
            game_context["game_mode"] = action_data["game_mode"]

        if "difficulty" in action_data:
            game_context["difficulty"] = action_data["difficulty"]

        if "toggle_tournament" in action_data:
            game_context["tournament_mode"] = not game_context.get("tournament_mode", False)
