# This is a simple zombie strategy:
# Move directly towards the closest human. If there are any humans in attacking range, attack a random one.
# If there are no humans in attacking range but there are obstacles, attack a random obstacle.

import random
import math
from game.character.action.ability_action import AbilityAction
from game.character.action.attack_action import AttackAction
from game.character.action.move_action import MoveAction
from game.game_state import GameState
from game.character.action.attack_action_type import AttackActionType
from strategy.strategy import Strategy

def f(x):
        if (x <= 24):
            return math.ceil(.5*x + 62)
        elif (x >= 25 and x <= 28):
            return x + 52
        else:
            return x + 49

class ShaanZombieStrategy(Strategy):

    def decide_moves(
            self, 
            possible_moves: dict[str, list[MoveAction]], 
            game_state: GameState
            ) -> list[MoveAction]:
        
        choices = []

        num_zombies = 0
        num_humans = 0

        for c in game_state.characters.values():
            if c.is_zombie:
                num_zombies += 1
            else:
                num_humans += 1

        taken_humans: dict[str, int] = {}
        
        # taken_humans[game_state.characters.keys()[0]] = 7
        for [ids, chars] in game_state.characters.items():
            if (not chars.is_zombie):
                taken_humans[ids] = 0

        max_zombies_on_target = math.ceil( float(num_zombies) / float(num_humans) )

        for [character_id, moves] in possible_moves.items():
            if len(moves) == 0:  # No choices... Next!
                continue

            pos = game_state.characters[character_id].position  # position of the zombie
            closest_human_pos = pos  # default position is zombie's pos
            closest_human_distance = 1984  # large number, map isn't big enough to reach this distance

            zombie_target_id = ""
            # Iterate through every human to find the closest one
            for [i, c] in game_state.characters.items():
                if c.is_zombie:
                    continue  # Fellow zombies are frens :D, ignore them

                distance = abs(c.position.x - pos.x) + abs(c.position.y - pos.y) # calculate manhattan distance between human and zombie
                if distance < closest_human_distance and taken_humans[i] < max_zombies_on_target:  # If distance is closer than current closest, replace it!
                    closest_human_pos = c.position
                    closest_human_distance = distance

                    taken_humans[i] += 1
                    if (zombie_target_id in taken_humans and taken_humans[zombie_target_id] > 0):
                        taken_humans[zombie_target_id] -= 1
                    zombie_target_id = i
                    
            # find radius from specific center point. Attraction only works outside the radius.
                    
            # if ( (f(pos.x) > pos.y and f(closest_human_pos.x) < closest_human_pos.y) or (f(pos.x) < pos.y and f(closest_human_pos.x) > closest_human_pos.y)):
            #     closest_human_pos.x = 

            # Move as close to the human as possible
            move_distance = 1337  # Distance between the move action's destination and the closest human
            move_choice = moves[0]  # The move action the zombie will be taking
            for m in moves:
                distance = abs(m.destination.x - closest_human_pos.x) + abs(m.destination.y - closest_human_pos.y)  # calculate manhattan distance

                # If distance is closer, that's our new choice!
                if distance < move_distance:  
                    move_distance = distance
                    move_choice = m

            choices.append(move_choice)  # add the choice to the list

        return choices

    def decide_attacks(
            self, 
            possible_attacks: dict[str, list[AttackAction]], 
            game_state: GameState
            ) -> list[AttackAction]:

        choices = []

        for [character_id, attacks] in possible_attacks.items():
            if len(attacks) == 0:  # No choices... Next!
                continue

            humans = []  # holds humans that are in range

            # Gather list of humans in range
            for a in attacks:
                if a.type is AttackActionType.CHARACTER:
                    humans.append(a)

            if humans:  # Attack a random human in range
                choices.append(random.choice(humans))
            else:  # No humans? Shame. The targets in range must be terrain. May as well attack one.
                choices.append(random.choice(attacks))

        return choices
