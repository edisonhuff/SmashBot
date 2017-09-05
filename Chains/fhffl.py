import melee
import globals
from melee.enums import Action, Button
from Chains.chain import Chain
from enum import Enum

class FHFFL_DIRECTION(Enum):
    UP = 0
    DOWN = 1
    FORWARD = 2
    BACK = 3
    NEUTRAL = 4

class Fhffl(Chain):
    def __init__(self, direction):
        self.direction=direction

    def step(self, direction=FHFFL_DIRECTION.DOWN):
        smashbot_state = globals.smashbot_state
        opponent_state = globals.opponent_state
        controller = globals.controller

        # If we're in knee bend, let go of jump. But move toward opponent
        if smashbot_state.action == Action.KNEE_BEND:
            self.interruptible = False
            jumpdirection = 1
            if opponent_state.x < smashbot_state.x:
                jumpdirection = -1
            controller.tilt_analog(Button.BUTTON_MAIN, jumpdirection, .5)
            return

        # If we're on the ground, but NOT in knee bend, then jump
        if smashbot_state.on_ground:
            if controller.prev.button[Button.BUTTON_Y]:
                self.interruptible = True
                controller.empty_input()
            else:
                self.interruptible = False
                controller.press_button(Button.BUTTON_Y)
            return

        #if we're in the air try to follow the opponent
        if not smashbot_state.on_ground:
            jumpdirection = 1
            if opponent_state.x < smashbot_state.x:
                jumpdirection = -1
            controller.tilt_analog(Button.BUTTON_MAIN, jumpdirection, .5)

        # If we're falling, then press down hard to do a fast fall, and release y
        if smashbot_state.speed_y_self < 0:
            controller.release_button(Button.BUTTON_Y);
            self.interruptible = False
            controller.tilt_analog(Button.BUTTON_MAIN, .5, 0)

            # Once we're falling , do an attack
            if not globals.framedata.isattack(smashbot_state.character, smashbot_state.action):
                # If the C stick wasn't set to middle, then
                if controller.prev.c_stick != (.5, .5):
                    controller.tilt_analog(Button.BUTTON_C, .5, .5)
                    return

                if self.direction == FHFFL_DIRECTION.UP:
                    controller.tilt_analog(Button.BUTTON_C, .5, 1)
                if self.direction == FHFFL_DIRECTION.DOWN:
                    controller.tilt_analog(Button.BUTTON_C, .5, 0)
                if self.direction == FHFFL_DIRECTION.FORWARD:
                    controller.tilt_analog(Button.BUTTON_C, int(smashbot_state.facing), .5)
                if self.direction == FHFFL_DIRECTION.BACK:
                    controller.tilt_analog(Button.BUTTON_C, int(not smashbot_state.facing), .5)
                if self.direction == FHFFL_DIRECTION.NEUTRAL:
                    controller.press_button(Button.BUTTON_A)
                    controller.tilt_analog(Button.BUTTON_MAIN, .5, .5)

            # Hit L at the end of the attack
            if smashbot_state.action_frame == 16:
                controller.press_button(Button.BUTTON_L)
            return  

        elif smashbot_state.speed_y_self > 0:
            controller.empty_input()
            return

        self.interruptible = True
        controller.empty_input()
