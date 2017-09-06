import melee
import globals
from melee.enums import Action, Button
from Chains.chain import Chain

# Edgestall
class Edgestall(Chain):
    def step(self):
        controller = globals.controller
        smashbot_state = globals.smashbot_state
        opponent_state = globals.opponent_state

        # If we just grabbed the edge, wait
        if smashbot_state.action == Action.EDGE_CATCHING:
            self.interruptible = True
            controller.empty_input()
            return

        # If we are able to let go of the edge, do it
        if smashbot_state.action == Action.EDGE_HANGING:
            # If we already pressed back last frame, let go
            if controller.prev.main_stick != (0.5, 0.5):
                controller.empty_input()
                return
            x = 1
            if smashbot_state.x < 0:
                x = 0
            self.interruptible = False
            controller.tilt_analog(Button.BUTTON_MAIN, x, 0.5)
            return

            # Once we're falling, jump
            if smashbot_state.action == Action.FALLING:
                self.interruptible = False
                controller.press_button(Button.BUTTON_Y)
                return

            # Once we've started jumping Up B to stall
            if smashbot_state.action == Action.JUMPING_ARIAL_FORWARD:
                controller.tilt_analog(Button.BUTTON_MAIN, 0.5, 1)
                controller.press_button(Button.BUTTON_B)
                return

        self.interruptible = True
        controller.empty_input()
