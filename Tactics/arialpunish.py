import melee
import globals
import Chains
import math
from melee.enums import Action, Button
from Tactics.tactic import Tactic
from Chains.shffl import SHFFL_DIRECTION
from Chains.fhffl import FHFFL_DIRECTION

class Arialpunish(Tactic):
    # How many frames do we have to work with for the punish
    def framesleft():
        opponent_state = globals.opponent_state

        # For some dumb reason, the game shows the standing animation as having a large hitstun
        #   manually account for this
        if opponent_state.action == Action.STANDING:
            return 1

        # Is opponent attacking?
        if globals.framedata.isattack(opponent_state.character, opponent_state.action):
            # What state of the attack is the opponent in?
            # Windup / Attacking / Cooldown
            attackstate = globals.framedata.attackstate_simple(opponent_state)
            if attackstate == melee.enums.AttackState.WINDUP:
                # Don't try to punish opponent in windup when they're invulnerable
                if opponent_state.invulnerability_left > 0:
                    return 0
                # Don't try to punish standup attack windup
                if opponent_state.action in [Action.GROUND_ATTACK_UP, Action.GETUP_ATTACK]:
                    return 0
                frame = globals.framedata.firsthitboxframe(opponent_state.character, opponent_state.action)
                return max(0, frame - opponent_state.action_frame - 1)
            if attackstate == melee.enums.AttackState.ATTACKING:
                return 0
            if attackstate == melee.enums.AttackState.COOLDOWN:
                frame = globals.framedata.iasa(opponent_state.character, opponent_state.action)
                return max(0, frame - opponent_state.action_frame)
        if globals.framedata.isroll(opponent_state.character, opponent_state.action):
            frame = globals.framedata.lastrollframe(opponent_state.character, opponent_state.action)
            return max(0, frame - opponent_state.action_frame)

        # Opponent is in hitstun
        if opponent_state.hitstun_frames_left > 0:
            # Special case here for lying on the ground.
            #   For some reason, the hitstun count is totally wrong for these actions
            if opponent_state.action in [Action.LYING_GROUND_UP, Action.LYING_GROUND_DOWN]:
                return 1

            return opponent_state.hitstun_frames_left

        # Opponent is in helpless fall
        if opponent_state.action in [Action.DEAD_FALL, Action.SPECIAL_FALL_FORWARD, \
                Action.SPECIAL_FALL_BACK]:
            return int(opponent_state.y / opponent_state.speed_y_self)

        # Opponent is in a lag state
        if opponent_state.action in [Action.UAIR_LANDING, Action.FAIR_LANDING, \
                Action.DAIR_LANDING, Action.BAIR_LANDING, Action.NAIR_LANDING]:
            # TODO: DO an actual lookup to see how many frames this is
            return 5

        return 1

    # Static function that returns whether we have enough time to run in and punish,
    # given the current gamestate. Either a shine or upsmash
    def canpunish():
        smashbot_state = globals.smashbot_state
        opponent_state = globals.opponent_state

        # Only looking to punish opponent in air
        if opponent_state.on_ground:
            return False

        # Don't do this on the ledge
        if smashbot_state.action in [Action.EDGE_HANGING, Action.EDGE_CATCHING]:
            return False

        # Don't go for offstage opponents
        if melee.stages.edgeposition(globals.gamestate.stage) < \
                (abs(opponent_state.x) - 2):
            return False

        left = Arialpunish.framesleft()
        # Will our opponent be invulnerable for the entire punishable window?
        if left <= opponent_state.invulnerability_left:
            return False

        if left < 5:
            return False

        #TODO: Wrap the shine range into a helper
        falcoshinerange = 9

        #TODO: Wrap this up into a helper
        falcojumpspeedx = 0.83
        # calculate how far we can go horizontally
        potentialjumpdistancex = (left-1) * falcojumpspeedx

        distance = abs(opponent_state.x - smashbot_state.x)
        speed = abs(opponent_state.speed_x_attack)
        # Loop through each frame and count the distanes horizontally
        for i in range(left - 1):
            distance += speed

        if distance < potentialjumpdistancex:
            return True
        
        return False

    def step(self):
        smashbot_state = globals.smashbot_state
        opponent_state = globals.opponent_state
        #If we can't interrupt the chain, just continue it
        if self.chain != None and not self.chain.interruptible:
            self.chain.step()
            return

        # TODO: This should be all inactionalbe animations, actually
        if smashbot_state.action == Action.THROW_DOWN:
            self.pickchain(Chains.Nothing)
            return

        # Can we punish right now?
        framesleft = Arialpunish.framesleft()
        if globals.logger:
            globals.logger.log("Notes", "framesleft: " + str(framesleft) + " ", concat=True)

        facing = smashbot_state.facing == (smashbot_state.x < opponent_state.x)
        # Remember that if we're turning, the attack will come out the opposite way
        if smashbot_state.action == Action.TURNING:
            facing = not facing

        # calculate how far up they will go
        apex = opponent_state.y
        speed = opponent_state.speed_y_attack
        gravity = globals.framedata.characterdata[opponent_state.character]["Gravity"]
        termvelocity = globals.framedata.characterdata[opponent_state.character]["TerminalVelocity"]

        # if not going up set speed to speed y self
        if opponent_state.speed_y_attack == 0:
            speed = opponent_state.speed_y_self

        # Loop through each frame and count the distances
        for i in range(framesleft - 1):
            speed -= gravity
            # We can't go faster than termvelocity downwards
            speed = max(speed, -termvelocity)
            apex += speed
            apex = max(apex, 0)


        #if their final apex is less than 0.9 dash to their position (and shine)
        if apex <= 9:
            self.chain = None
            self.pickchain(Chains.DashDance, [opponent_state.x])
            return

        # if height > 12:
        #     print('fhffl: height', height,'framesleft',framesleft)
        #     if opponent_state.percent > 70:
        #         if facing:
        #             print('Full Hop Nair')
        #             self.pickchain(Chains.Fhffl, [FHFFL_DIRECTION.NEUTRAL])
        #             return
        #         print('Full Hop Bair')
        #         self.pickchain(Chains.Fhffl, [FHFFL_DIRECTION.BACK])
        #         return
        #     print('Full Hop Dair')
        #     self.pickchain(Chains.Fhffl, [FHFFL_DIRECTION.DOWN])
        #     return

        # print('shffl: height', height,'framesleft',framesleft)
        if framesleft < 10:
            if opponent_state.percent > 70:
                if facing:
                    print('Short Hop Nair')
                    self.pickchain(Chains.Shffl, [FHFFL_DIRECTION.NEUTRAL])
                    return
                print('Short Hop Bair')
                self.pickchain(Chains.Shffl, [SHFFL_DIRECTION.BACK])
                return
            print('Short Hop Dair')
            self.pickchain(Chains.Shffl, [SHFFL_DIRECTION.DOWN])
            return

        self.chain = None
        self.pickchain(Chains.DashDance, [opponent_state.x])
        return