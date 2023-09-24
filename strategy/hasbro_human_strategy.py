# This is a simple human strategy:
# 6 Marksman, 6 Medics, and 4 Traceurs
# Move as far away from the closest zombie as possible
# If there are any zombies in attack range, attack the closest
# If a Medic's ability is available, heal a human in range with the least health

import random
from game.character.action.ability_action import AbilityAction
from game.character.action.ability_action_type import AbilityActionType
from game.character.action.attack_action import AttackAction
from game.character.action.attack_action_type import AttackActionType
from game.character.action.move_action import MoveAction
from game.character.character_class_type import CharacterClassType
from game.game_state import GameState
from game.util.position import Position
from strategy.strategy import Strategy

import heapq


class HasbroHumanStrategy(Strategy):
    def decide_character_classes(
            self,
            possible_classes: list[CharacterClassType],
            num_to_pick: int,
            max_per_same_class: int,
    ) -> dict[CharacterClassType, int]:
        # The maximum number of special classes we can choose is 16
        # Selecting 6 Marksmen, 6 Medics, and 4 Traceurs
        # The other 4 humans will be regular class
        choices = {
            CharacterClassType.MARKSMAN: 1,
            CharacterClassType.MEDIC: 1,
            CharacterClassType.BUILDER: 4,
            CharacterClassType.TRACEUR: 5,
            CharacterClassType.DEMOLITIONIST: 5,
        }
        return choices

    def decide_moves(
            self,
            possible_moves: dict[str, list[MoveAction]],
            game_state: GameState
    ) -> list[MoveAction]:

        choices = []

        for [character_id, moves] in possible_moves.items():
            if len(moves) == 0:  # No choices... Next!
                continue

            pos = game_state.characters[character_id].position  # position of the human
            closest_zombie_pos = pos  # default position is zombie's pos
            closest_zombie_distance = 1234  # large number, map isn't big enough to reach this distance

            # Iterate through every zombie to find the closest one
            for c in game_state.characters.values():
                if not c.is_zombie:
                    continue  # Fellow humans are frens :D, ignore them

                distance = abs(c.position.x - pos.x) + abs(
                    c.position.y - pos.y)  # calculate manhattan distance between human and zombie
                if distance < closest_zombie_distance:  # If distance is closer than current closest, replace it!
                    closest_zombie_pos = c.position
                    closest_zombie_distance = distance


            # Move as close to the human as possible
            move_distance = 1337  # Distance between the move action's destination and the closest human
            move_choice = moves[0]  # The move action the zombie will be taking
            target_position = Position(49, 58)


            # WATER STRAT (TRACEUR)
            if game_state.characters[character_id].class_type == CharacterClassType.TRACEUR:
                if pos.y >= 58:
                    target_position = Position(24, 77)
                    if pos.x == 24 and pos.y == 77:
                        target_position = Position(20, 77)
                if pos.x <= 21:
                    target_position = Position(2, 74)

                if game_state.turn >= 50:
                    for c in game_state.characters.values():
                        if not c.is_zombie:
                            continue  # Fellow humans are frens :D, ignore them
                        zom_pos = c.position
                        if zom_pos.x <= 15 and zom_pos.y >= 76:
                            target_position = Position(5, 98)

                if pos.y >= 98:
                    target_position = Position(20, 98)

                if game_state.turn >= 75 and pos.x >= 20:
                    target_position = Position(26, 78)

                if game_state.turn >= 75 and (pos.y <= 78 or pos.x >= 26):
                    # Move as far away from the zombie as possible
                    move_distance = -1  # Distance between the move action's destination and the closest zombie
                    move_choice = moves[0]  # The move action the human will be taking

                    for m in moves:
                        distance = abs(m.destination.x - closest_zombie_pos.x) + abs(
                            m.destination.y - closest_zombie_pos.y)  # calculate manhattan distance

                        if distance > move_distance:  # If distance is further, that's our new choice!
                            move_distance = distance
                            move_choice = m

                    target_position = move_choice.destination

            # WATER STRAT (BUILDER/MARKSMEN/NORMAL)
            if game_state.characters[character_id].class_type == CharacterClassType.BUILDER or \
                    game_state.characters[character_id].class_type == CharacterClassType.MARKSMAN or \
                    game_state.characters[character_id].class_type == CharacterClassType.MEDIC or \
                    game_state.characters[character_id].class_type == CharacterClassType.NORMAL:
                if pos.y >= 58:
                    target_position = Position(24, 77)
                    if pos.y >= 77:
                        target_position = Position(19, 98)
                        if pos.x <= 19 and pos.y == 98:
                            target_position = Position(9, 98)
                if pos == Position(9, 98):
                    target_position = Position(11, 99)
                if pos == Position(11, 99):
                    target_position = Position(14, 99)
                if game_state.turn >= 70:
                    target_position = Position(14, 99)

                if game_state.turn >= 70:
                    for c in game_state.characters.values():
                        if not c.is_zombie:
                            continue  # Fellow humans are frens :D, ignore them
                        zom_pos = c.position
                        if zom_pos.x <= 15 and zom_pos.y >= 76:
                            target_position = Position(26, 78)

                if game_state.turn >= 75 and (pos.y <= 78 or pos.x >= 26):
                    # Move as far away from the zombie as possible
                    move_distance = -1  # Distance between the move action's destination and the closest zombie
                    move_choice = moves[0]  # The move action the human will be taking

                    for m in moves:
                        distance = abs(m.destination.x - closest_zombie_pos.x) + abs(
                            m.destination.y - closest_zombie_pos.y)  # calculate manhattan distance

                        if distance > move_distance:  # If distance is further, that's our new choice!
                            move_distance = distance
                            move_choice = m

                    target_position = move_choice.destination



            # SACRIFICE
            if game_state.characters[character_id].class_type == CharacterClassType.DEMOLITIONIST:
                target_position = Position(0, 48)

            # TRACEUR WALL STRAT
            # if game_state.characters[character_id].class_type == CharacterClassType.TRACEUR:
            #     target_position = Position(50, 58)
            #     if pos.y >= 58:
            #         target_position = Position(79, 99)
            # for x in range(20):
            #     # check if in position
            #     if pos.x == 79 + x and pos.y == 99 - x:
            #         # check for nearby zombies
            #         for c in game_state.characters.values():
            #             if not c.is_zombie:
            #                 continue  # Fellow humans are frens :D, ignore them
            #
            #             if (c.position.y == 99 - x and c.position.x == 79 + x - 2) or \
            #                     (c.position.y == 99 - x - 1 and c.position.x == 79 + x - 1):
            #                 target_position = Position(pos.x + 1, pos.y - 1)
            #             elif c.position.y == 99 - x - 2 and c.position.x == 79 + x:
            #                 target_position = Position(pos.x + 2, pos.y - 2)
            #             else:
            #                 target_position = Position(pos.x, pos.y)

            # Move finder
            for m in moves:
                distance = abs(m.destination.x - target_position.x) + abs(
                    m.destination.y - target_position.y)  # calculate manhattan distance

                # If distance is closer, that's our new choice!
                if distance < move_distance:
                    move_distance = distance
                    move_choice = m

            choices.append(move_choice)  # add the choice to the list

        return choices


        #     # Move as far away from the zombie as possible
        #     move_distance = -1  # Distance between the move action's destination and the closest zombie
        #     move_choice = moves[0]  # The move action the human will be taking
        #
        #     for m in moves:
        #         distance = abs(m.destination.x - closest_zombie_pos.x) + abs(
        #             m.destination.y - closest_zombie_pos.y)  # calculate manhattan distance
        #
        #         if distance > move_distance:  # If distance is further, that's our new choice!
        #             move_distance = distance
        #             move_choice = m
        #
        #     choices.append(move_choice)  # add the choice to the list
        #
        # return choices

    def decide_attacks(
            self,
            possible_attacks: dict[str, list[AttackAction]],
            game_state: GameState
    ) -> list[AttackAction]:
        choices = []

        for [character_id, attacks] in possible_attacks.items():
            if len(attacks) == 0:  # No choices... Next!
                continue

            pos = game_state.characters[character_id].position  # position of the human
            closest_zombie = None  # Closest zombie in range
            closest_zombie_distance = 404  # Distance between closest zombie and human

            # Iterate through zombies in range and find the closest one
            for a in attacks:
                if a.type is AttackActionType.CHARACTER:
                    attackee_pos = game_state.characters[a.attacking_id].position  # Get position of zombie in question

                    distance = abs(attackee_pos.x - pos.x) + abs(attackee_pos.y - pos.y)  # Get distance between the two

                    if distance < closest_zombie_distance:  # Closer than current? New target!
                        closest_zombie = a
                        closest_zombie_distance = distance

            if closest_zombie:  # Attack the closest zombie, if there is one
                choices.append(closest_zombie)

            wallmove = None
            # breaking walls
            if not closest_zombie:
                for a in attacks:
                    if a.type is AttackActionType.TERRAIN:
                        if not (game_state.terrains[a.attacking_id].position.x <= 20 and \
                                game_state.terrains[a.attacking_id].position.y >= 85):
                            wallmove = a

                if wallmove:
                    choices.append(wallmove)

        return choices

    def decide_abilities(
            self,
            possible_abilities: dict[str, list[AbilityAction]],
            game_state: GameState
    ) -> list[AbilityAction]:
        choices = []

        for [character_id, abilities] in possible_abilities.items():
            if len(abilities) == 0:  # No choices? Next!
                continue

            # BUILDING
            for a in abilities:
                if a.type == AbilityActionType.BUILD_BARRICADE:
                    self_pos = game_state.characters[a.executing_character_id].position
                    if a.positional_target == Position(8, 98) or a.positional_target == Position(8, 99):
                        choices.append(a)
                    elif self_pos == Position(11, 99):
                        if a.positional_target == Position(10, 98) or a.positional_target == Position(10, 99):
                            choices.append(a)

            # # HEALING
            least_health = 999  # The health of the human being targeted
            for a in abilities:
                if a.type == AbilityActionType.HEAL:
                    human_target = abilities[0]  # the human that'll be healed
                    health = game_state.characters[a.character_id_target].health  # Health of human in question
                    if health < least_health:  # If they have less health, they are the new patient!
                        human_target = a
                        least_health = health
                    if human_target:  # Give the human a cookie
                        choices.append(human_target)

        return choices

