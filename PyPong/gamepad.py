import pygame

class GamepadManager:
    def __init__(self):
        pygame.joystick.init()
        self.joysticks = []
        self.detect_joysticks()

    def detect_joysticks(self):
        self.joysticks = []
        for i in range(pygame.joystick.get_count()):
            joystick = pygame.joystick.Joystick(i)
            joystick.init()
            self.joysticks.append(joystick)

    def get_input(self, player):
        if player == 1 and len(self.joysticks) > 0:
            return self._get_joystick_input(self.joysticks[0])
        elif player == 2 and len(self.joysticks) > 1:
            return self._get_joystick_input(self.joysticks[1])
        return {"up": False, "down": False}

    def _get_joystick_input(self, joystick):
        axis_y = joystick.get_axis(1)
        deadzone = 0.3
        
        up = axis_y < -deadzone or joystick.get_button(11)
        down = axis_y > deadzone or joystick.get_button(12)
        
        return {"up": up, "down": down}

    def has_gamepad(self, player):
        if player == 1:
            return len(self.joysticks) > 0
        elif player == 2:
            return len(self.joysticks) > 1
        return False
