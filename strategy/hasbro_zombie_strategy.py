# This is a simple zombie strategy:
# Move directly towards the closest human. If there are any humans in attacking range, attack a random one.
# If there are no humans in attacking range but there are obstacles, attack a random obstacle.

import random
from game.character.action.ability_action import AbilityAction
from game.character.action.attack_action import AttackAction
from game.character.action.move_action import MoveAction
from game.game_state import GameState
from game.character.action.attack_action_type import AttackActionType
from strategy.strategy import Strategy


class HasbroZombieStrategy(Strategy):
    def decide_moves(
            self,
            possible_moves: dict[str, list[MoveAction]],
            game_state: GameState
    ) -> list[MoveAction]:

        choices = []

        for [character_id, moves] in possible_moves.items():
            if len(moves) == 0:  # No choices... Next!
                continue

            pos = game_state.characters[character_id].position  # position of the zombie
            closest_human_pos = pos  # default position is zombie's pos
            closest_human_distance = 1984  # large number, map isn't big enough to reach this distance

            # Iterate through every human to find the closest one
            for c in game_state.characters.values():
                if c.is_zombie:
                    continue  # Fellow zombies are frens :D, ignore them

                distance = abs(c.position.x - pos.x) + abs(
                    c.position.y - pos.y)  # calculate manhattan distance between human and zombie
                if distance < closest_human_distance:  # If distance is closer than current closest, replace it!
                    closest_human_pos = c.position
                    closest_human_distance = distance

            # Move as close to the human as possible
            move_distance = 1337  # Distance between the move action's destination and the closest human
            move_choice = moves[0]  # The move action the zombie will be taking
            for m in moves:
                distance = abs(m.destination.x - closest_human_pos.x) + abs(
                    m.destination.y - closest_human_pos.y)  # calculate manhattan distance

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


    # def heuristic(node, goal):
    #     # Calculate the Manhattan distance between the current node and the goal node
    #     return abs(node.x - goal.x) + abs(node.y - goal.y)
    #
    # def a_star(grid, start, goal):
    #     open_set = []
    #     closed_set = set()
    #
    #     start_node = Node(*start)
    #     goal_node = Node(*goal)
    #
    #     start_node.g = 0
    #     start_node.h = heuristic(start_node, goal_node)
    #
    #     heapq.heappush(open_set, start_node)
    #
    #     while open_set:
    #         current_node = heapq.heappop(open_set)
    #
    #         if current_node.x == goal_node.x and current_node.y == goal_node.y:
    #             path = []
    #             while current_node:
    #                 path.append((current_node.x, current_node.y))
    #                 current_node = current_node.parent
    #             return path[::-1]
    #
    #         closed_set.add((current_node.x, current_node.y))
    #
    #         for dx, dy in [(0, 1), (1, 0), (0, -1), (-1, 0)]:
    #             neighbor_x, neighbor_y = current_node.x + dx, current_node.y + dy
    #             if (
    #                 0 <= neighbor_x < len(grid) and
    #                 0 <= neighbor_y < len(grid[0]) and
    #                 grid[neighbor_x][neighbor_y] != 1 and
    #                 (neighbor_x, neighbor_y) not in closed_set
    #             ):
    #                 neighbor_node = Node(neighbor_x, neighbor_y)
    #                 tentative_g = current_node.g + 1  # Assuming a uniform cost of 1 for each step
    #
    #                 if tentative_g < neighbor_node.g:
    #                     neighbor_node.parent = current_node
    #                     neighbor_node.g = tentative_g
    #                     neighbor_node.h = heuristic(neighbor_node, goal_node)
    #
    #                     if neighbor_node not in open_set:
    #                         heapq.heappush(open_set, neighbor_node)
    #
    #     return None  # No path found
    #
    # # Create a 100x100 grid (assuming 0 is open space and 1 is an obstacle)
    # grid = [[0 for _ in range(100)] for _ in range(100)]
    #
    # # Define the start and goal coordinates
    # start = (0, 0)
    # goal = (99, 99)
    #
    # # Find the path using A* algorithm
    # path = a_star(grid, start, goal)
    #
    # if path:
    #     print("Path found:")
    #     for step, (x, y) in enumerate(path):
    #         print(f"Step {step}: ({x}, {y})")
    # else:
    #     print("No path found.")