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
            CharacterClassType.MARKSMAN: 5,
            CharacterClassType.MEDIC: 5,
            CharacterClassType.TRACEUR: 5,
            CharacterClassType.DEMOLITIONIST: 1,
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


            # WATER STRAT
            if not game_state.characters[character_id].class_type == CharacterClassType.DEMOLITIONIST:
                if pos.y >= 58:
                    target_position = Position(24, 77)
                    if pos.x <= 24 and pos.y >= 77:
                        target_position = Position(2, 77)

            if pos.x == 2 and (pos.y <= 77 or pos.y >= 72):
                target_position = Position(2, 72)

            # SACRIFICE
            if game_state.characters[character_id].class_type == CharacterClassType.DEMOLITIONIST:
                target_position = Position(42, 48)

            # TRACEUR WALL STRAT
            if game_state.characters[character_id].class_type == CharacterClassType.TRACEUR:
                target_position = Position(50, 58)
                if pos.y >= 58:
                    target_position = Position(79, 99)
            for x in range(20):
                # check if in position
                if pos.x == 79 + x and pos.y == 99 - x:
                    # check for nearby zombies
                    for c in game_state.characters.values():
                        if not c.is_zombie:
                            continue  # Fellow humans are frens :D, ignore them

                        if (c.position.y == 99 - x and c.position.x == 79 + x - 2) or \
                                (c.position.y == 99 - x - 1 and c.position.x == 79 + x - 1):
                            target_position = Position(pos.x + 1, pos.y - 1)
                        elif c.position.y == 99 - x - 2 and c.position.x == 79 + x:
                            target_position = Position(pos.x + 2, pos.y - 2)
                        else:
                            target_position = Position(pos.x, pos.y)

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
            else:
                choices.append(attacks[0])

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

            # Since we only have medics, the choices must only be healing a nearby human
            human_target = abilities[0]  # the human that'll be healed
            least_health = 999  # The health of the human being targeted

            for a in abilities:
                health = game_state.characters[a.character_id_target].health  # Health of human in question

                if health < least_health:  # If they have less health, they are the new patient!
                    human_target = a
                    least_health = health

            if human_target:  # Give the human a cookie
                choices.append(human_target)

        return choices



class Node:
    def __init__(self, x, y):
        self.x = x
        self.y = y
        self.g = float('inf')  # Cost from start node to this node
        self.h = 0             # Heuristic (estimated cost from this node to goal)
        self.parent = None

    def __lt__(self, other):
        return (self.g + self.h) < (other.g + other.h)

    @staticmethod
    def heuristic(node, goal):
        # Calculate the Manhattan distance between the current node and the goal node
        return abs(node.x - goal.x) + abs(node.y - goal.y)

    @staticmethod
    def a_star(grid, start, goal):
        open_set = []
        closed_set = set()

        start_node = Node(*start)
        goal_node = Node(*goal)

        start_node.g = 0
        start_node.h = Node.heuristic(start_node, goal_node)

        heapq.heappush(open_set, start_node)

        while open_set:
            current_node = heapq.heappop(open_set)

            if current_node.x == goal_node.x and current_node.y == goal_node.y:
                path = []
                while current_node:
                    path.append((current_node.x, current_node.y))
                    current_node = current_node.parent
                return path[::-1]

            closed_set.add((current_node.x, current_node.y))

            for dx, dy in [(0, 1), (1, 0), (0, -1), (-1, 0)]:
                neighbor_x, neighbor_y = current_node.x + dx, current_node.y + dy
                if (
                    0 <= neighbor_x < len(grid) and
                    0 <= neighbor_y < len(grid[0]) and
                    grid[neighbor_x][neighbor_y] != 1 and
                    (neighbor_x, neighbor_y) not in closed_set
                ):
                    neighbor_node = Node(neighbor_x, neighbor_y)
                    tentative_g = current_node.g + 1  # Assuming a uniform cost of 1 for each step

                    if tentative_g < neighbor_node.g:
                        neighbor_node.parent = current_node
                        neighbor_node.g = tentative_g
                        # neighbor_node.h = heuristic(neighbor_node, goal_node)

                        if neighbor_node not in open_set:
                            heapq.heappush(open_set, neighbor_node)

        return None  # No path found
