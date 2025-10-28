import random

class TrafficAgent:
    def __init__(self, intersection):
        self.intersection = intersection
        self.min_green_time = 3  # Minimum time to keep light green
        self.current_green_time = 0
        self.last_action = None
        self.last_state = None

        # Q-Learning parameters
        self.alpha = 0.1  # Learning rate
        self.gamma = 0.9  # Discount factor
        self.epsilon = 0.3  # Exploration rate
        self.epsilon_decay = 0.995  # Decay rate for exploration
        self.min_epsilon = 0.01  # Minimum exploration rate

        # Initialize Q-table
        self.q_table = {}

    def get_state_representation(self, state):
        light_state = state['light_state']
        waiting_vehicles = state['waiting_vehicles']

        # Count vehicles waiting in each direction
        ns_waiting = waiting_vehicles['N'] + waiting_vehicles['S']
        ew_waiting = waiting_vehicles['E'] + waiting_vehicles['W']

        # Discretize waiting vehicles count to prevent state space explosion
        ns_waiting_bin = min(5, ns_waiting)  # Cap at 5 vehicles
        ew_waiting_bin = min(5, ew_waiting)  # Cap at 5 vehicles

        return light_state, ns_waiting_bin, ew_waiting_bin

    def get_q_value(self, state_rep, action):
        if state_rep not in self.q_table:
            self.q_table[state_rep] = {'stay': 0.0, 'change': 0.0}
        return self.q_table[state_rep][action]

    def decide_action(self, state):
        state_rep = self.get_state_representation(state)

        # Increment green time counter if light is green
        if 'GREEN' in state['light_state']:
            self.current_green_time += 1
        else:
            # Reset counter during yellow phase
            self.current_green_time = 0

        # Only allow 'change' if minimum green time has passed
        valid_actions = ['stay']
        if self.current_green_time >= self.min_green_time and 'GREEN' in state['light_state']:
            valid_actions.append('change')

        # Exploration: random action with probability epsilon
        if random.random() < self.epsilon and len(valid_actions) > 1:
            action = random.choice(valid_actions)
        # Exploitation: best action from Q-table
        else:
            if len(valid_actions) == 1:
                action = 'stay'
            else:
                # Get Q-values for the current state
                q_stay = self.get_q_value(state_rep, 'stay')
                q_change = self.get_q_value(state_rep, 'change')

                # Choose the action with highest Q-value
                action = 'stay' if q_stay >= q_change else 'change'

        # Store current state and action for learning
        self.last_state = state_rep
        self.last_action = action

        return action

    def calculate_reward(self, current_state):
        waiting_vehicles = current_state['waiting_vehicles']
        ns_waiting = waiting_vehicles['N'] + waiting_vehicles['S']
        ew_waiting = waiting_vehicles['E'] + waiting_vehicles['W']

        # Total waiting vehicles (negative reward)
        total_waiting = -(ns_waiting + ew_waiting)

        # Additional penalty for vehicles waiting at red light
        light_state = current_state['light_state']
        red_waiting = 0

        if 'NS_GREEN' in light_state:
            red_waiting = ew_waiting * 2  # Vehicles waiting at EW (red)
        elif 'EW_GREEN' in light_state:
            red_waiting = ns_waiting * 2  # Vehicles waiting at NS (red)

        # Larger penalty for longer queue at red light
        return total_waiting - red_waiting

    def update_q_table(self, state, action, reward, next_state):
        if self.last_state is None:
            return  # Skip update if this is the first action

        state_rep = self.get_state_representation(state)
        next_state_rep = self.get_state_representation(next_state)

        # Get current Q-value
        current_q = self.get_q_value(state_rep, action)

        # Get max Q-value for next state
        next_max_q = max([
            self.get_q_value(next_state_rep, a)
            for a in ['stay', 'change']
        ])

        # Q-learning formula
        new_q = current_q + self.alpha * (reward + self.gamma * next_max_q - current_q)

        # Update Q-table
        self.q_table[state_rep][action] = new_q

        # Decay exploration rate
        self.epsilon = max(self.min_epsilon, self.epsilon * self.epsilon_decay)

    def perform_action(self, action):
        if action == 'change' and 'GREEN' in self.intersection.traffic_light.current_state:
            # Force the light to start changing to yellow
            self.intersection.traffic_light._switch_to_yellow()
            self.current_green_time = 0
        # 'stay' action does nothing - the traffic light continues its normal timing

    def save_q_table(self, file_path=None):
        if file_path is None:
            file_path = f"agent_{id(self)}_q_table.pkl"

        import pickle
        with open(file_path, 'wb') as f:
            pickle.dump(self.q_table, f)
        return file_path

    def load_q_table(self, file_path):
        import pickle
        import os

        if os.path.exists(file_path):
            with open(file_path, 'rb') as f:
                self.q_table = pickle.load(f)
            return True
        return False