class Vehicle:
    def __init__(self, vehicle_id, start_pos, direction):
        self.vehicle_id = vehicle_id
        self.position = tuple(map(float, start_pos))  # current position (float for smoothness)
        self.grid_pos = start_pos  # current grid cell
        self.direction = direction
        self.waiting = False
        self.finished = False
        self.speed = 0.2  # how far to move per step (0.0 - 1.0)
        self.target_pos = self.get_next_position()
        self.size = (0.4, 0.2)  # width, height for box representation (x, y)
        self.color = self.get_random_color()
        self.waiting_time = 0  # track waiting time at intersections

    def get_random_color(self):
        import random
        # Generate random colors but avoid those too close to background or traffic lights
        r = random.uniform(0.2, 0.8)
        g = random.uniform(0.2, 0.8)
        b = random.uniform(0.2, 0.8)
        return r, g, b

    def move(self, grid_env):
        if self.finished:
            return

        # If reached target, check if we need to wait
        if self._is_at_target():
            # Prepare next target position
            self.grid_pos = self.target_pos

            if not grid_env.is_within_bounds(self.grid_pos):
                self.finished = True
                print(f"Vehicle {self.vehicle_id} exited the grid.")
                return

            intersection = grid_env.get_intersection_at(self.grid_pos)

            if intersection:
                light = intersection.get_light_state(self.direction)
                if light != 'GREEN':
                    self.waiting = True
                    self.waiting_time += 1
                    return
                else:
                    self.waiting = False
                    self.waiting_time = 0
                    self.turn_randomly()

            self.target_pos = self.get_next_position()

        self.waiting = False
        self._move_toward_target()

    def _move_toward_target(self):
        x, y = self.position
        tx, ty = self.target_pos

        dx = tx - x
        dy = ty - y
        dist = (dx ** 2 + dy ** 2) ** 0.5

        # Adjust speed based on proximity to other vehicles (simplified traffic behavior)
        adjusted_speed = self.speed

        if dist < adjusted_speed:
            self.position = self.target_pos
        else:
            step_x = (dx / dist) * adjusted_speed
            step_y = (dy / dist) * adjusted_speed
            self.position = (x + step_x, y + step_y)

    def _is_at_target(self):
        return tuple(round(c, 2) for c in self.position) == tuple(round(c, 2) for c in self.target_pos)

    def get_next_position(self):
        x, y = self.grid_pos
        if self.direction == 'N':
            return x, y - 1
        elif self.direction == 'S':
            return x, y + 1
        elif self.direction == 'E':
            return x + 1, y
        elif self.direction == 'W':
            return x - 1, y

    def turn_randomly(self):
        import random
        turn = random.choices(['straight', 'left', 'right'], weights=[0.7, 0.15, 0.15])[0]
        if turn == 'left':
            self.direction = {'N': 'W', 'W': 'S', 'S': 'E', 'E': 'N'}[self.direction]
        elif turn == 'right':
            self.direction = {'N': 'E', 'E': 'S', 'S': 'W', 'W': 'N'}[self.direction]

    def get_box_corners(self):
        x, y = self.position
        width, height = self.size

        # Swap dimensions for vertical direction
        if self.direction in ['N', 'S']:
            width, height = height, width

        # Calculate corners (x, y is the center of the vehicle)
        half_w, half_h = width / 2, height / 2

        # Return corners in the order: bottom-left, bottom-right, top-right, top-left
        return [
            (x - half_w, y - half_h),
            (x + half_w, y - half_h),
            (x + half_w, y + half_h),
            (x - half_w, y + half_h)
        ]