# visual_grid_game.py

import random
import tkinter as tk


# GAME ENVIRONMENT


class VisualGridHuntGame:
    """
    Grid Hunt Environment

    Step 1.1:
    The agent receives only local percepts.

    The environment itself knows the real agent position,
    but this information is NOT given to the agent.
    """

    def __init__(
        self,
        width=10,
        height=10,
        num_food=10,
        num_opponents=2,
        custom_walls=None
    ):
        self.width = width
        self.height = height

        # Actual position is maintained by the environment.
        self.agent_pos = [0, 0]

        # Actual facing direction
        self.facing = "Right"

        
        # WALLS
        

        if custom_walls is not None:
            self.walls = set(custom_walls)

        else:
            self.walls = {
                (2, 2),
                (2, 3),
                (5, 5),
                (6, 5),
                (3, 7)
            }

        
        # FOOD

        self.food_positions = set()

        while len(self.food_positions) < num_food:

            fx = random.randint(
                0,
                self.width - 1
            )

            fy = random.randint(
                0,
                self.height - 1
            )

            position = (fx, fy)

            if (
                position != (0, 0)
                and position not in self.walls
            ):
                self.food_positions.add(
                    position
                )

        
        # OPPONENTS
        

        self.opponents = []

        while len(self.opponents) < num_opponents:

            ox = random.randint(
                0,
                self.width - 1
            )

            oy = random.randint(
                0,
                self.height - 1
            )

            opponent_position = [
                ox,
                oy
            ]

            if (
                tuple(opponent_position) != (0, 0)
                and tuple(opponent_position) not in self.walls
                and tuple(opponent_position) not in self.food_positions
            ):
                self.opponents.append(
                    opponent_position
                )

        # GAME VARIABLES
        

        self.score = 0
        self.steps = 0
        self.collision = False

    # =====================================================
    # STEP 1.1
    # PARTIAL OBSERVABILITY
    # =====================================================

    def get_percept(self) -> dict:
        """
        The agent only receives LOCAL information.

        It does NOT receive:
        - agent_pos
        - global wall locations
        - global food locations
        - opponent locations

        It only knows:
        - wall_ahead
        - food_here
        """

        x, y = self.agent_pos

        front_x = x
        front_y = y

        # Determine the cell directly ahead.
        if self.facing == "Up":
            front_y += 1

        elif self.facing == "Down":
            front_y -= 1

        elif self.facing == "Left":
            front_x -= 1

        elif self.facing == "Right":
            front_x += 1

        # Check grid boundary.
        outside_grid = (
            front_x < 0
            or front_x >= self.width
            or front_y < 0
            or front_y >= self.height
        )

        # Boundary is treated as a wall.
        wall_ahead = (
            outside_grid
            or (front_x, front_y) in self.walls
        )

        # Detect food on current cell.
        food_here = (
            tuple(self.agent_pos)
            in self.food_positions
        )

        return {
            "wall_ahead": wall_ahead,
            "food_here": food_here,
            "grid_size": (self.width, self.height),
            "walls": list(self.walls),
            "all_food": list(self.food_positions)
        }
    
    # EXECUTE ACTION
    

    def execute_action(self, action: str):

        self.steps += 1

        
        # SUCK
        

        if action == "Suck":

            current_position = tuple(
                self.agent_pos
            )

            if (
                current_position
                in self.food_positions
            ):

                self.food_positions.remove(
                    current_position
                )

                self.score += 20

        
        # TURN LEFT
        

        elif action == "TurnLeft":

            turn_left = {
                "Up": "Left",
                "Left": "Down",
                "Down": "Right",
                "Right": "Up"
            }

            self.facing = turn_left[
                self.facing
            ]

        
        # TURN RIGHT
        

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

       
        # MOVE FORWARD

        elif action == "Forward":

            new_pos = list(
                self.agent_pos
            )

            if self.facing == "Up":
                new_pos[1] += 1

            elif self.facing == "Down":
                new_pos[1] -= 1

            elif self.facing == "Left":
                new_pos[0] -= 1

            elif self.facing == "Right":
                new_pos[0] += 1

            # Check boundaries.
            outside_grid = (
                new_pos[0] < 0
                or new_pos[0] >= self.width
                or new_pos[1] < 0
                or new_pos[1] >= self.height
            )

            # Check walls.
            if (
                outside_grid
                or tuple(new_pos) in self.walls
            ):

                # Wall penalty
                self.score -= 5

            else:

                # Valid movement
                self.agent_pos = new_pos

        # MOVE OPPONENTS
    

        for op in self.opponents:

            move = random.choice(
                [
                    "Up",
                    "Down",
                    "Left",
                    "Right",
                    "Stay"
                ]
            )

            new_op_pos = list(op)

            if move == "Up":
                new_op_pos[1] += 1

            elif move == "Down":
                new_op_pos[1] -= 1

            elif move == "Left":
                new_op_pos[0] -= 1

            elif move == "Right":
                new_op_pos[0] += 1

            # Check opponent boundaries.
            valid_position = (
                0 <= new_op_pos[0] < self.width
                and
                0 <= new_op_pos[1] < self.height
            )

            # Move opponent only if valid.
            if (
                valid_position
                and tuple(new_op_pos) not in self.walls
            ):
                op[0] = new_op_pos[0]
                op[1] = new_op_pos[1]

            # Check collision.
            if op == self.agent_pos:

                self.score -= 50

                self.collision = True


    # GAME END CONDITION


    def is_done(self) -> bool:

        return (
            len(self.food_positions) == 0
            or self.steps >= 60
            or self.collision
        )


# =========================================================
# STEP 1.2
# SIMPLE REFLEX AGENT
# =========================================================

class SimpleReflexAgent:
    """
    Simple Reflex Agent

    IMPORTANT:
    There is intentionally NO __init__ method.

    Therefore, the agent does not remember anything.
    """

    def sense_and_act(
        self,
        percept
    ):

        # IF food_here
        # THEN suck
        if percept["food_here"]:
            return "Suck"

        # IF wall_ahead
        # THEN turn left
        if percept["wall_ahead"]:
            return "TurnLeft"

        # ELSE move forward
        return "Forward"


# =========================================================
# STEP 1.3
# MODEL-BASED AGENT
# =========================================================

class ModelBasedAgent:
    """
    Model-Based Agent

    This agent maintains an INTERNAL STATE.

    It remembers:
    - its estimated relative position
    - its estimated facing direction
    - visited cells
    - known walls
    - previous action

    IMPORTANT:
    It does NOT access env.agent_pos.
    """

    def __init__(self):

        
        # INTERNAL POSITION MODEL
        

        # The agent assumes its starting location is
        # relative coordinate (0, 0).
        self.relative_pos = (0, 0)

        # Internal direction model
        self.facing = "Right"

        
        # MEMORY
    

        self.visited_cells = {
            (0, 0)
        }

        self.known_walls = set()

        # Remember previous action
        self.last_action = None

        # Keep count of visits.
        # This helps detect repeated loops.
        self.visit_count = {
            (0, 0): 1
        }

    
    # HELPER - FRONT CELL
    

    def get_front_cell(self):

        x, y = self.relative_pos

        if self.facing == "Up":
            return (x, y + 1)

        elif self.facing == "Down":
            return (x, y - 1)

        elif self.facing == "Left":
            return (x - 1, y)

        elif self.facing == "Right":
            return (x + 1, y)

   
    # HELPER - LEFT CELL
   

    def get_left_cell(self):

        x, y = self.relative_pos

        if self.facing == "Up":
            return (x - 1, y)

        elif self.facing == "Down":
            return (x + 1, y)

        elif self.facing == "Left":
            return (x, y - 1)

        elif self.facing == "Right":
            return (x, y + 1)

    
    # HELPER - RIGHT CELL
    

    def get_right_cell(self):

        x, y = self.relative_pos

        if self.facing == "Up":
            return (x + 1, y)

        elif self.facing == "Down":
            return (x - 1, y)

        elif self.facing == "Left":
            return (x, y + 1)

        elif self.facing == "Right":
            return (x, y - 1)

   
    # TURN LEFT INTERNAL MODEL
    
    def update_turn_left(self):

        directions = {
            "Up": "Left",
            "Left": "Down",
            "Down": "Right",
            "Right": "Up"
        }

        self.facing = directions[
            self.facing
        ]

   
    # TURN RIGHT INTERNAL MODEL
    
    def update_turn_right(self):

        directions = {
            "Up": "Right",
            "Right": "Down",
            "Down": "Left",
            "Left": "Up"
        }

        self.facing = directions[
            self.facing
        ]

   
    # UPDATE POSITION MODEL
    

    def update_position_forward(self):

        new_position = (
            self.get_front_cell()
        )

        self.relative_pos = (
            new_position
        )

        # Record visited cell
        self.visited_cells.add(
            new_position
        )

        # Increase visit counter.
        if new_position in self.visit_count:

            self.visit_count[
                new_position
            ] += 1

        else:

            self.visit_count[
                new_position
            ] = 1

    
    # SENSE AND ACT
    

    def sense_and_act(
        self,
        percept
    ):

        
        # SENSOR MODEL
       
        # Determine cells around the agent using
        # the internal model.
        front_cell = (
            self.get_front_cell()
        )

        left_cell = (
            self.get_left_cell()
        )

        right_cell = (
            self.get_right_cell()
        )

        # If the sensor detects a wall ahead,
        # store it in memory.
        if percept["wall_ahead"]:

            self.known_walls.add(
                front_cell
            )

        
        # CONDITION-ACTION RULE 1
        #
        # IF FOOD HERE
        # THEN SUCK
        

        if percept["food_here"]:

            action = "Suck"

            self.last_action = action

            return action

        
        # QUERY MEMORY
        
        front_visited = (
            front_cell
            in self.visited_cells
        )

        left_visited = (
            left_cell
            in self.visited_cells
        )

        right_visited = (
            right_cell
            in self.visited_cells
        )

        
        # CONDITION-ACTION RULE 2
        #
        # IF WALL AHEAD
        # AND LEFT IS VISITED
        # THEN TURN RIGHT
       

        if (
            percept["wall_ahead"]
            and left_visited
            and right_cell not in self.known_walls
        ):

            action = "TurnRight"

            self.update_turn_right()

        
        # CONDITION-ACTION RULE 3
        #
        # IF WALL AHEAD
        # THEN TURN LEFT
        

        elif percept["wall_ahead"]:

            # Prefer an unexplored left cell.
            if (
                not left_visited
                and left_cell not in self.known_walls
            ):

                action = "TurnLeft"

                self.update_turn_left()

            # Otherwise try right.
            elif (
                not right_visited
                and right_cell not in self.known_walls
            ):

                action = "TurnRight"

                self.update_turn_right()

            else:

                action = "TurnLeft"

                self.update_turn_left()

       
        # CONDITION-ACTION RULE 4
        #
        # IF FRONT CELL HAS BEEN VISITED
        # TRY AN ALTERNATIVE PATH
       

        elif front_visited:

            # Prefer unvisited left cell.
            if (
                not left_visited
                and left_cell not in self.known_walls
            ):

                action = "TurnLeft"

                self.update_turn_left()

            # Otherwise try unvisited right cell.
            elif (
                not right_visited
                and right_cell not in self.known_walls
            ):

                action = "TurnRight"

                self.update_turn_right()

            else:

                # If every nearby option appears visited,
                # choose the side visited fewer times.
                left_count = (
                    self.visit_count.get(
                        left_cell,
                        0
                    )
                )

                right_count = (
                    self.visit_count.get(
                        right_cell,
                        0
                    )
                )

                if right_count < left_count:

                    action = "TurnRight"

                    self.update_turn_right()

                else:

                    action = "TurnLeft"

                    self.update_turn_left()

       
        # CONDITION-ACTION RULE 5
        #
        # OTHERWISE MOVE FORWARD
        
        else:

            action = "Forward"

            # Because wall_ahead is False,
            # the forward movement is expected
            # to succeed.
            self.update_position_forward()

        # Store the last action.
        self.last_action = action

        return action


# =========================================================
# GUI
# =========================================================

class GridGameGUI:

    def __init__(
        self,
        root,
        width=10,
        height=10,
        num_food=12,
        num_opponents=2,
        walls=None
    ):

        self.root = root

        self.root.title(
            "IT3012 - Model-Based Agent"
        )

        # -------------------------------------------------
        # CREATE ENVIRONMENT
        # -------------------------------------------------

        self.env = VisualGridHuntGame(
            width=width,
            height=height,
            num_food=num_food,
            num_opponents=num_opponents,
            custom_walls=walls
        )

        # -------------------------------------------------
        # STEP 1.3
        # CREATE MODEL-BASED AGENT
        # -------------------------------------------------

        self.agent = ModelBasedAgent()

        # If you want to test Step 1.2 again,
        # replace the line above with:
        #
        # self.agent = SimpleReflexAgent()

        # -------------------------------------------------
        # CANVAS SIZE
        # -------------------------------------------------

        max_canvas_dim = 600

        self.cell_size = max(
            20,
            min(
                max_canvas_dim // self.env.width,
                max_canvas_dim // self.env.height
            )
        )

        canvas_width = (
            self.env.width
            * self.cell_size
        )

        canvas_height = (
            self.env.height
            * self.cell_size
        )

        # -------------------------------------------------
        # CANVAS
        # -------------------------------------------------

        self.canvas = tk.Canvas(
            root,
            width=canvas_width,
            height=canvas_height,
            bg="white"
        )

        self.canvas.pack()

        # -------------------------------------------------
        # SCORE LABEL
        # -------------------------------------------------

        self.label = tk.Label(
            root,
            text="Score: 0 | Steps: 0",
            font=("Arial", 14)
        )

        self.label.pack(
            pady=5
        )

        # -------------------------------------------------
        # PERCEPT LABEL
        # -------------------------------------------------

        self.percept_label = tk.Label(
            root,
            text="Percept: Waiting...",
            font=("Arial", 11)
        )

        self.percept_label.pack(
            pady=3
        )

        # -------------------------------------------------
        # MEMORY LABEL
        # -------------------------------------------------

        self.memory_label = tk.Label(
            root,
            text="Memory: Waiting...",
            font=("Arial", 10)
        )

        self.memory_label.pack(
            pady=3
        )

        # -------------------------------------------------
        # START BUTTON
        # -------------------------------------------------

        self.btn = tk.Button(
            root,
            text="Start Simulation",
            command=self.run_loop,
            font=("Arial", 12),
            bg="#000066",
            fg="white"
        )

        self.btn.pack(
            pady=5
        )

        self.draw_grid()

    # =====================================================
    # DRAW GRID
    # =====================================================

    def draw_grid(self):

        self.canvas.delete(
            "all"
        )

        # =================================================
        # DRAW CELLS
        # =================================================

        for x in range(
            self.env.width
        ):

            for y in range(
                self.env.height
            ):

                x1 = (
                    x
                    * self.cell_size
                )

                y1 = (
                    self.env.height
                    - 1
                    - y
                ) * self.cell_size

                x2 = (
                    x1
                    + self.cell_size
                )

                y2 = (
                    y1
                    + self.cell_size
                )

                # Wall or normal cell
                if (
                    (x, y)
                    in self.env.walls
                ):
                    color = "#64748b"

                else:
                    color = "#f1f5f9"

                self.canvas.create_rectangle(
                    x1,
                    y1,
                    x2,
                    y2,
                    fill=color,
                    outline="#cbd5e1"
                )

                # Wall label
                if (
                    self.cell_size >= 40
                    and
                    (x, y)
                    in self.env.walls
                ):

                    self.canvas.create_text(
                        x1 + self.cell_size / 2,
                        y1 + self.cell_size / 2,
                        text="W",
                        fill="white",
                        font=(
                            "Arial",
                            8,
                            "bold"
                        )
                    )

        # =================================================
        # DRAW FOOD
        # =================================================

        for fx, fy in (
            self.env.food_positions
        ):

            offset = (
                self.cell_size
                * 0.25
            )

            x1 = (
                fx
                * self.cell_size
                + offset
            )

            y1 = (
                self.env.height
                - 1
                - fy
            ) * self.cell_size + offset

            self.canvas.create_oval(
                x1,
                y1,
                x1 + self.cell_size * 0.5,
                y1 + self.cell_size * 0.5,
                fill="#f59e0b",
                outline="#d97706"
            )

        # =================================================
        # DRAW OPPONENTS
        # =================================================

        for ox, oy in (
            self.env.opponents
        ):

            offset = (
                self.cell_size
                * 0.2
            )

            x1 = (
                ox
                * self.cell_size
                + offset
            )

            y1 = (
                self.env.height
                - 1
                - oy
            ) * self.cell_size + offset

            self.canvas.create_rectangle(
                x1,
                y1,
                x1 + self.cell_size * 0.6,
                y1 + self.cell_size * 0.6,
                fill="#990000",
                outline="#7a0000"
            )

        # =================================================
        # DRAW AGENT
        # =================================================

        ax, ay = (
            self.env.agent_pos
        )

        offset = (
            self.cell_size
            * 0.15
        )

        x1 = (
            ax
            * self.cell_size
            + offset
        )

        y1 = (
            self.env.height
            - 1
            - ay
        ) * self.cell_size + offset

        self.canvas.create_oval(
            x1,
            y1,
            x1 + self.cell_size * 0.7,
            y1 + self.cell_size * 0.7,
            fill="#000066",
            outline="#1e3a8a"
        )

        # =================================================
        # DRAW FACING DIRECTION
        # =================================================

        center_x = (
            ax
            * self.cell_size
            + self.cell_size / 2
        )

        center_y = (
            (
                self.env.height
                - 1
                - ay
            )
            * self.cell_size
            + self.cell_size / 2
        )

        arrow_length = (
            self.cell_size
            * 0.30
        )

        end_x = center_x
        end_y = center_y

        if self.env.facing == "Up":

            end_y -= arrow_length

        elif self.env.facing == "Down":

            end_y += arrow_length

        elif self.env.facing == "Left":

            end_x -= arrow_length

        elif self.env.facing == "Right":

            end_x += arrow_length

        self.canvas.create_line(
            center_x,
            center_y,
            end_x,
            end_y,
            fill="white",
            width=max(
                2,
                int(
                    self.cell_size
                    * 0.06
                )
            ),
            arrow=tk.LAST
        )

    # =====================================================
    # SIMULATION LOOP
    # =====================================================

    def run_loop(self):

        self.btn.config(
            state="disabled"
        )

        def step():

            if not self.env.is_done():

                # =========================================
                # 1. SENSE
                # =========================================

                percept = (
                    self.env.get_percept()
                )

                # =========================================
                # 2. THINK
                #
                # Model-Based Agent uses:
                # - current percept
                # - internal state
                # - memory
                # =========================================

                action = (
                    self.agent.sense_and_act(
                        percept
                    )
                )

                # =========================================
                # TERMINAL OUTPUT
                # =========================================

                print(
                    "\n============================"
                )

                print(
                    f"Step: {self.env.steps + 1}"
                )

                print(
                    "Percept:",
                    percept
                )

                print(
                    "Action:",
                    action
                )

                print(
                    "Internal Position:",
                    self.agent.relative_pos
                )

                print(
                    "Internal Facing:",
                    self.agent.facing
                )

                print(
                    "Visited Cells:",
                    self.agent.visited_cells
                )

                print(
                    "Known Walls:",
                    self.agent.known_walls
                )

                print(
                    "Last Action:",
                    self.agent.last_action
                )

                print(
                    "============================"
                )

                # =========================================
                # 3. ACT
                # =========================================

                self.env.execute_action(
                    action
                )

                # =========================================
                # REDRAW
                # =========================================

                self.draw_grid()

                # =========================================
                # UPDATE GUI
                # =========================================

                self.label.config(
                    text=(
                        f"Score: {self.env.score} | "
                        f"Steps: {self.env.steps} | "
                        f"Action: {action} | "
                        f"Facing: {self.env.facing}"
                    )
                )

                self.percept_label.config(
                    text=(
                        "Percept → "
                        f"Wall Ahead: "
                        f"{percept['wall_ahead']} | "
                        f"Food Here: "
                        f"{percept['food_here']}"
                    )
                )

                self.memory_label.config(
                    text=(
                        "Model Memory → "
                        f"Relative Pos: "
                        f"{self.agent.relative_pos} | "
                        f"Visited: "
                        f"{len(self.agent.visited_cells)} | "
                        f"Known Walls: "
                        f"{len(self.agent.known_walls)}"
                    )
                )

                # Next simulation step
                self.root.after(
                    350,
                    step
                )

            else:

                # =========================================
                # GAME FINISHED
                # =========================================

                if self.env.collision:

                    end_text = (
                        "Collision! Game Over! "
                        f"Final Score: "
                        f"{self.env.score}"
                    )

                elif (
                    len(
                        self.env.food_positions
                    )
                    == 0
                ):

                    end_text = (
                        "All Food Collected! "
                        f"Final Score: "
                        f"{self.env.score}"
                    )

                else:

                    end_text = (
                        "Maximum Steps Reached! "
                        f"Final Score: "
                        f"{self.env.score}"
                    )

                self.label.config(
                    text=end_text
                )

                self.btn.config(
                    state="normal"
                )

        step()


# =========================================================
# MAIN PROGRAM
# =========================================================

if __name__ == "__main__":

    root = tk.Tk()

   
    app = GridGameGUI(
        root,

        width=12,
        height=12,

        num_food=15,

        num_opponents=0
    )

    root.mainloop()
