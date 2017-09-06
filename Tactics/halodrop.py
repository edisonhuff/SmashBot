import melee
import globals
import Chains
import random
from melee.enums import Action
from Tactics.tactic import Tactic
from Chains.di import DI
from Chains.nothing import Nothing

class HaloDrop(Tactic):
    # Do we need to recover?
    def onHalo():
        if globals.smashbot_state.action == Action.ON_HALO_WAIT:
            return True
        return False


    def step(self):
        if globals.smashbot_state.action == Action.ON_HALO_WAIT:
          self.pickchain(Chains.DI, [0.5, 0])
          return

        self.chain = None
        self.pickchain(Chains.Nothing)