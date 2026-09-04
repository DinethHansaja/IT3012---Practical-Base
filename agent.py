# agent.py
from collections import deque
import heapq
import math

class GreedyGridAgent:
    """A simple agent that tries to move around systematically to clear the grid."""

    def __init__(self):
        self.actions_pool = ['Up', 'Down', 'Left', 'Right']

    def sense_and_act(self, percept: dict) -> str:
        # If standing directly on food, or just wander / move towards coordinates
        pos = percept['agent_pos']
        # Simple heuristic or fallback random sweep
        return random.choice(self.actions_pool)

class SearchAgent:
    def __init__(self):
        self.actions = ['Up', 'Down', 'Left', 'Right']
        
        # Search plan
        self.plan = []

        # Active search algorithm
        self.active_algo = 'AStar'

    def get_neighbors(self, state, grid_size, walls):
        """
        Return all valid neighboring states.

        state: (x, y)
        """
        x, y = state
        width, height = grid_size

        neighbors = []

        moves = {
            'Up': (0, 1),
            'Down': (0, -1),
            'Left': (-1, 0),
            'Right': (1, 0)
        }

        for action, (dx, dy) in moves.items():
            nx = x + dx
            ny = y + dy

            # Check grid boundaries
            if 0 <= nx < width and 0 <= ny < height:
                # Check walls
                if (nx, ny) not in walls:
                    neighbors.append(((nx, ny), action))

        return neighbors

    #BFS
    def bfs_search(self, start, goal, grid_size, walls):
            """
            Breadth-First Search using a FIFO queue.
            """
    
            queue = deque()
            queue.append((start, []))
    
            reached = {start}
    
            while queue:
                state, path = queue.popleft()
    
                if state == goal:
                    return path
    
                for next_state, action in self.get_neighbors(
                        state, grid_size, walls):
    
                    if next_state not in reached:
                        reached.add(next_state)
    
                        new_path = path + [action]
                        queue.append((next_state, new_path))
                        
            return None

    #DFS
    def dfs_search(self, start, goal, grid_size, walls):
            """
            Depth-First Search using a LIFO stack.
            """
    
            stack = []
            stack.append((start, []))
    
            reached = {start}
    
            while stack:
                state, path = stack.pop()
    
                if state == goal:
                    return path
    
                for next_state, action in self.get_neighbors(
                        state, grid_size, walls):
    
                    if next_state not in reached:
                        reached.add(next_state)
    
                        new_path = path + [action]
                        stack.append((next_state, new_path))
                        
                return None

    #UCS
     def ucs_search(self, start, goal, grid_size, walls):
            """
            Uniform-Cost Search using a priority queue.
            Priority is the total path cost g(n).
            """
    
            priority_queue = []
    
            # (cost, state, path)
            heapq.heappush(priority_queue, (0, start, []))
    
            reached = {start: 0}
    
            while priority_queue:
                cost, state, path = heapq.heappop(priority_queue)
    
                if state == goal:
                    return path
    
                # Ignore outdated queue entries
                if cost > reached[state]:
                    continue
    
                for next_state, action in self.get_neighbors(
                        state, grid_size, walls):
    
                    step_cost = 1
                    new_cost = cost + step_cost
    
                    if (next_state not in reached or
                            new_cost < reached[next_state]):
    
                        reached[next_state] = new_cost
    
                        new_path = path + [action]
    
                        heapq.heappush(
                            priority_queue,
                            (new_cost, next_state, new_path)
                        )
    
            return None

    #method to find the closest food
    def find_closest_food(self, start, food_positions):
        if not food_positions:
            return None
    
        return min(
            food_positions,
            key=lambda food:
                abs(food[0] - start[0]) +
                abs(food[1] - start[1])
        )
    
    def sense_and_act(self, percept):
    
        # If there is no existing plan, create a new one
        if not self.plan:
    
            start = percept['agent_pos']
            all_food = percept['all_food']
            grid_size = percept['grid_size']
            walls = set(tuple(wall) for wall in percept['walls'])
    
            # If there is no food left
            if not all_food:
                return 'Stay'
    
            # Find the closest food pellet
            goal = self.find_closest_food(start, all_food)
    
            # Execute the selected search algorithm
            if self.active_algo == 'BFS':
                self.plan = self.bfs_search(
                    start,
                    goal,
                    grid_size,
                    walls
                )
    
            elif self.active_algo == 'DFS':
                self.plan = self.dfs_search(
                    start,
                    goal,
                    grid_size,
                    walls
                )
    
            elif self.active_algo == 'UCS':
                self.plan = self.ucs_search(
                    start,
                    goal,
                    grid_size,
                    walls
                )

            elif self.active_algo == 'AStar':
                self.plan = self.astar_search(
                    start,
                    goal,
                    walls,
                    grid_size,
                    heuristic_type='manhattan'
                )
    
            # Search could not find a path
            if self.plan is None:
                self.plan = []
                return 'Right'
    
        # Execute the first action in the plan
        return self.plan.pop(0)

    def manhattan_distance(self, pos, goal):
    x1, y1 = pos
    x2, y2 = goal

    return abs(x1 - x2) + abs(y1 - y2)

    def euclidean_distance(self, pos, goal):
        x1, y1 = pos
        x2, y2 = goal
    
        return math.sqrt(
            (x1 - x2) ** 2 +
            (y1 - y2) ** 2
        )

    def astar_search(self, start_pos, goal_pos, walls, grid_size,
                 heuristic_type='manhattan'):

    # Priority queue
    priority_queue = []

    # States that have already been explored
    reached_states = set()

    # Select heuristic
    if heuristic_type == 'manhattan':
        h_cost = self.manhattan_distance(start_pos, goal_pos)
    else:
        h_cost = self.euclidean_distance(start_pos, goal_pos)

    # Starting node
    g_cost = 0
    f_cost = g_cost + h_cost

    # (f_cost, g_cost, current_pos, path_taken)
    heapq.heappush(
        priority_queue,
        (f_cost, g_cost, start_pos, [])
    )

    # Four possible movements
    moves = {
        'Up': (0, 1),
        'Down': (0, -1),
        'Left': (-1, 0),
        'Right': (1, 0)
    }

    width, height = grid_size

    while priority_queue:

        # Get node with lowest f(n)
        f_cost, g_cost, current_pos, path_taken = heapq.heappop(
            priority_queue
        )

        # Goal reached
        if current_pos == goal_pos:
            return path_taken

        # Already explored
        if current_pos in reached_states:
            continue

        # Mark current state as reached
        reached_states.add(current_pos)

        # Expand neighboring cells
        for action, (dx, dy) in moves.items():

            new_x = current_pos[0] + dx
            new_y = current_pos[1] + dy

            new_pos = (new_x, new_y)

            # Check boundaries
            if not (0 <= new_x < width and
                    0 <= new_y < height):
                continue

            # Check walls
            if new_pos in walls:
                continue

            # Check reached states
            if new_pos in reached_states:
                continue

            # Calculate costs
            g_new = g_cost + 1

            if heuristic_type == 'manhattan':
                h_new = self.manhattan_distance(
                    new_pos,
                    goal_pos
                )
            else:
                h_new = self.euclidean_distance(
                    new_pos,
                    goal_pos
                )

            f_new = g_new + h_new

            # Add action to path
            new_path = path_taken + [action]

            # Add new node to priority queue
            heapq.heappush(
                priority_queue,
                (
                    f_new,
                    g_new,
                    new_pos,
                    new_path
                )
            )

    # No path found
    return None
