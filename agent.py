import random
from collections import deque
import heapq


# Greedy Grid Agent

class GreedyGridAgent:
    """
    A simple agent that moves around the grid.
    """

    def __init__(self):
        self.actions_pool = [
            "Up",
            "Down",
            "Left",
            "Right"
        ]

    def sense_and_act(self, percept: dict) -> str:

        # Get the agent position
        pos = percept["agent_pos"]

        # Choose a random movement
        return random.choice(
            self.actions_pool
        )


# Search Agent

class SearchAgent:
    """
    Search Agent that implements:
    - BFS
    - DFS
    - UCS

    The agent creates a plan and then
    executes the plan step by step.
    """

    def __init__(self):

        # Store the actions that the agent plans to execute
        self.plan = []

        # Select the search algorithm
        # Change this to "DFS" or "UCS" to test them
        self.active_algo = "BFS"

        # The agent starts at position (0, 0)
        self.relative_pos = (0, 0)

        # The game starts with the agent facing Right
        self.facing = "Right"


    # Find all valid neighbouring cells

    def get_successors(
        self,
        state,
        walls,
        grid_size
    ):

        # Get current x and y coordinates
        x, y = state

        # Get grid width and height
        width, height = grid_size

        # Possible movements
        possible_moves = [
            ("Up", (x, y + 1)),
            ("Down", (x, y - 1)),
            ("Left", (x - 1, y)),
            ("Right", (x + 1, y))
        ]

        successors = []

        # Check every possible movement
        for action, next_state in possible_moves:

            nx, ny = next_state

            # Check whether the position is inside the grid
            inside_grid = (
                0 <= nx < width
                and
                0 <= ny < height
            )

            # Add the position only if it is valid
            # and it is not a wall
            if (
                inside_grid
                and
                next_state not in walls
            ):

                successors.append(
                    (
                        action,
                        next_state
                    )
                )

        return successors


    # Breadth-First Search

    def bfs_search(
        self,
        start,
        goal,
        walls,
        grid_size
    ):

        # BFS uses a FIFO queue
        frontier = deque()

        # Add the starting position to the queue
        frontier.append(
            (
                start,
                []
            )
        )

        # Keep track of already explored states
        reached = {start}

        # Continue until the queue becomes empty
        while frontier:

            # Remove the first item from the queue
            current, path = frontier.popleft()

            # If we reached the goal, return the path
            if current == goal:

                return path

            # Find all valid neighbouring states
            for action, next_state in self.get_successors(
                current,
                walls,
                grid_size
            ):

                # Only visit states that we have not visited
                if next_state not in reached:

                    # Mark the state as visited
                    reached.add(
                        next_state
                    )

                    # Add the new state to the queue
                    frontier.append(
                        (
                            next_state,
                            path + [action]
                        )
                    )

        # Return None if no path exists
        return None


    # Depth-First Search

    def dfs_search(
        self,
        start,
        goal,
        walls,
        grid_size
    ):

        # DFS uses a LIFO stack
        frontier = []

        # Add the starting position to the stack
        frontier.append(
            (
                start,
                []
            )
        )

        # Keep track of visited states
        reached = {start}

        # Continue until the stack becomes empty
        while frontier:

            # Remove the last item from the stack
            current, path = frontier.pop()

            # If we reached the goal, return the path
            if current == goal:

                return path

            # Find all valid neighbouring states
            for action, next_state in self.get_successors(
                current,
                walls,
                grid_size
            ):

                # Only visit states that we have not visited
                if next_state not in reached:

                    # Mark the state as visited
                    reached.add(
                        next_state
                    )

                    # Add the state to the stack
                    frontier.append(
                        (
                            next_state,
                            path + [action]
                        )
                    )

        # Return None if no path exists
        return None


    # Uniform-Cost Search

    def ucs_search(
        self,
        start,
        goal,
        walls,
        grid_size
    ):

        # UCS uses a priority queue
        frontier = []

        # Counter helps when two nodes have the same cost
        counter = 0

        # Add the starting position with cost 0
        heapq.heappush(
            frontier,
            (
                0,
                counter,
                start,
                []
            )
        )

        # Store the cheapest cost found for each state
        reached = {
            start: 0
        }

        # Continue until the priority queue is empty
        while frontier:

            # Remove the state with the lowest cost
            cost, _, current, path = (
                heapq.heappop(frontier)
            )

            # If we reached the goal, return the path
            if current == goal:

                return path

            # Find all valid neighbouring states
            for action, next_state in self.get_successors(
                current,
                walls,
                grid_size
            ):

                # Every movement currently costs 1
                new_cost = cost + 1

                # Add the state if it is new
                # or if we found a cheaper path
                if (
                    next_state not in reached
                    or
                    new_cost < reached[next_state]
                ):

                    # Save the new cheapest cost
                    reached[next_state] = new_cost

                    counter += 1

                    # Add the state to the priority queue
                    heapq.heappush(
                        frontier,
                        (
                            new_cost,
                            counter,
                            next_state,
                            path + [action]
                        )
                    )

        # Return None if no path exists
        return None


    # Convert search directions into game actions

    def convert_plan_to_game_actions(
        self,
        direction_plan
    ):

        # This list represents the order of directions
        direction_order = [
            "Up",
            "Right",
            "Down",
            "Left"
        ]

        # Store the converted actions
        game_actions = []

        # Start with the current facing direction
        current_facing = self.facing

        # Process every direction in the search plan
        for desired_direction in direction_plan:

            # Find the current direction index
            current_index = direction_order.index(
                current_facing
            )

            # Find the desired direction index
            desired_index = direction_order.index(
                desired_direction
            )

            # Calculate how many 90-degree turns are needed
            difference = (
                desired_index - current_index
            ) % 4

            # Already facing the correct direction
            if difference == 0:

                game_actions.append(
                    "Forward"
                )

            # Need to turn right
            elif difference == 1:

                game_actions.append(
                    "TurnRight"
                )

                game_actions.append(
                    "Forward"
                )

                current_facing = desired_direction

            # Need to turn around
            elif difference == 2:

                game_actions.append(
                    "TurnRight"
                )

                game_actions.append(
                    "TurnRight"
                )

                game_actions.append(
                    "Forward"
                )

                current_facing = desired_direction

            # Need to turn left
            elif difference == 3:

                game_actions.append(
                    "TurnLeft"
                )

                game_actions.append(
                    "Forward"
                )

                current_facing = desired_direction

        return game_actions


    # Update the agent's internal position

    def update_internal_position(
        self,
        action
    ):

        # Get the current position
        x, y = self.relative_pos

        # If the agent turns left
        if action == "TurnLeft":

            turn_left = {
                "Up": "Left",
                "Left": "Down",
                "Down": "Right",
                "Right": "Up"
            }

            self.facing = turn_left[
                self.facing
            ]

        # If the agent turns right
        elif action == "TurnRight":

            turn_right = {
                "Up": "Right",
                "Right": "Down",
                "Down": "Left",
                "Left": "Up"
            }

            self.facing = turn_right[
                self.facing
            ]

        # If the agent moves forward
        elif action == "Forward":

            if self.facing == "Up":
                y += 1

            elif self.facing == "Down":
                y -= 1

            elif self.facing == "Left":
                x -= 1

            elif self.facing == "Right":
                x += 1

            # Save the new position
            self.relative_pos = (
                x,
                y
            )


    # Sense the environment and choose an action

    def sense_and_act(
        self,
        percept: dict
    ):

        # If food is directly under the agent,
        # collect it first
        if percept["food_here"]:

            return "Suck"


        # Create a new plan only when
        # there is no existing plan
        if not self.plan:

            # Get the grid size from the percept
            grid_size = percept["grid_size"]

            # Get the wall positions
            walls = set(
                percept["walls"]
            )

            # Get all food positions
            all_food = percept["all_food"]

            # If there is no food left,
            # there is no target to search for
            if not all_food:

                return "TurnLeft"


            # Current agent position
            start = self.relative_pos

            # Find the closest food using
            # Manhattan distance
            closest_food = min(
                all_food,
                key=lambda food: (
                    abs(food[0] - start[0])
                    +
                    abs(food[1] - start[1])
                )
            )


            # Choose the search algorithm

            if self.active_algo == "BFS":

                direction_plan = self.bfs_search(
                    start,
                    closest_food,
                    walls,
                    grid_size
                )

            elif self.active_algo == "DFS":

                direction_plan = self.dfs_search(
                    start,
                    closest_food,
                    walls,
                    grid_size
                )

            elif self.active_algo == "UCS":

                direction_plan = self.ucs_search(
                    start,
                    closest_food,
                    walls,
                    grid_size
                )

            else:

                # Show an error if an invalid
                # algorithm name is provided
                raise ValueError(
                    "Unknown search algorithm: "
                    + self.active_algo
                )


            # If no path can be found
            if direction_plan is None:

                return "TurnLeft"


            # Convert the search directions
            # into actions understood by the game
            self.plan = (
                self.convert_plan_to_game_actions(
                    direction_plan
                )
            )


        # Take the first action from the plan
        action = self.plan.pop(0)

        # Update the internal model
        self.update_internal_position(
            action
        )

        # Return the action to the environment
        return action