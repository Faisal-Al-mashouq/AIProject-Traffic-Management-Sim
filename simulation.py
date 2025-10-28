from environment import GridEnvironment
from traffic_agent import TrafficAgent
from visualize import Visualize
from vehicle import Vehicle
import matplotlib.pyplot as plt
import datetime
import random
import copy
import time
import os

class Simulation:
    def __init__(self, steps=100, grid_width=3, grid_height=3):
        self.grid_env = GridEnvironment(width=grid_width, height=grid_height)
        self.vehicles = []
        self.agents = [TrafficAgent(intersection) for intersection in self.grid_env.intersections.values()]
        self.steps = steps
        self.visualizer = Visualize(self.grid_env, self.vehicles)
        self.vehicle_count = 0
        self.traffic_density = 0.3  # Controls vehicle spawn rate (0.0 - 1.0)
        self.rush_hour = False  # Toggle for rush hour simulation
        self.rush_hour_factor = 3.0  # Multiplier for traffic during rush hour
        self.traffic_metrics = {
            'avg_wait_time': [],
            'vehicles_in_system': [],
            'vehicles_finished': 0
        }

    def spawn_vehicle(self):
        # Calculate spawn probability based on traffic density and rush hour
        spawn_probability = self.traffic_density
        if self.rush_hour:
            spawn_probability *= self.rush_hour_factor

        # Randomly decide whether to spawn a vehicle this step
        if random.random() > spawn_probability:
            return

        # Choose entry point
        direction = random.choice(['N', 'S', 'E', 'W'])

        if direction == 'N':
            start_pos = (random.randint(0, self.grid_env.width - 1), self.grid_env.height)
        elif direction == 'S':
            start_pos = (random.randint(0, self.grid_env.width - 1), -1)
        elif direction == 'E':
            start_pos = (-1, random.randint(0, self.grid_env.height - 1))
        else:  # 'W'
            start_pos = (self.grid_env.width, random.randint(0, self.grid_env.height - 1))

        # Check if spawn location is already occupied
        for vehicle in self.vehicles:
            if not vehicle.finished and self._distance(vehicle.position, start_pos) < 0.5:
                return  # Don't spawn if too close to another vehicle

        vehicle = Vehicle(self.vehicle_count, start_pos, direction)
        self.vehicles.append(vehicle)
        self.vehicle_count += 1

    def _distance(self, pos1, pos2):
        return ((pos1[0] - pos2[0]) ** 2 + (pos1[1] - pos2[1]) ** 2) ** 0.5

    def update_metrics(self):
        # Calculate waiting vehicles
        waiting_vehicles = [v for v in self.vehicles if not v.finished and v.waiting]
        active_vehicles = [v for v in self.vehicles if not v.finished]

        # Calculate average waiting time
        if waiting_vehicles:
            avg_wait = sum(v.waiting_time for v in waiting_vehicles) / len(waiting_vehicles)
            self.traffic_metrics['avg_wait_time'].append(avg_wait)
        else:
            self.traffic_metrics['avg_wait_time'].append(0)

        # Count vehicles in system
        self.traffic_metrics['vehicles_in_system'].append(len(active_vehicles))

    def check_vehicle_interactions(self):
        active_vehicles = [v for v in self.vehicles if not v.finished]

        # Simple collision avoidance: If two vehicles are too close, slow down the following one
        for i, v1 in enumerate(active_vehicles):
            if v1.waiting:
                continue  # Skip waiting vehicles

            for v2 in active_vehicles[i + 1:]:
                if v2.waiting:
                    continue  # Skip waiting vehicles

                # Check if vehicles are on the same path and close to each other
                if (v1.direction == v2.direction and
                        self._distance(v1.position, v2.position) < 0.4):

                    # Determine which vehicle is in front
                    if self._is_vehicle_ahead(v1, v2):
                        v2.speed = 0.1  # Slow down following vehicle
                    else:
                        v1.speed = 0.1  # Slow down following vehicle
                else:
                    # Reset speeds if not in proximity
                    v1.speed = 0.2
                    v2.speed = 0.2

    def _is_vehicle_ahead(self, v1, v2):
        x1, y1 = v1.position
        x2, y2 = v2.position

        if v1.direction == 'N':
            return y1 < y2
        elif v1.direction == 'S':
            return y1 > y2
        elif v1.direction == 'E':
            return x1 > x2
        elif v1.direction == 'W':
            return x1 < x2
        return False

    def run(self, visualize=True):
        plt.ion()

        # Keep track of previous states for Q-learning updates
        previous_states = {}

        for step in range(self.steps):
            print(f"\n--- Simulation step {step + 1}/{self.steps} ---")

            # Toggle rush hour in the middle of simulation
            if step == self.steps // 3:
                self.rush_hour = True
                print("Rush hour traffic started!")
            elif step == 2 * self.steps // 3:
                self.rush_hour = False
                print("Rush hour traffic ended.")

            # Store current states before updates for reward calculation
            current_states = {}
            for agent in self.agents:
                intersection_pos = agent.intersection.position

                # Count waiting vehicles at this intersection
                waiting_vehicles = {'N': 0, 'S': 0, 'E': 0, 'W': 0}
                for vehicle in self.vehicles:
                    if (not vehicle.finished and vehicle.waiting and
                            vehicle.grid_pos == intersection_pos):
                        waiting_vehicles[vehicle.direction] += 1

                current_states[intersection_pos] = {
                    'light_state': agent.intersection.traffic_light.current_state,
                    'waiting_vehicles': waiting_vehicles.copy()
                }


            # Update environment
            self.grid_env.update()

            # AI agents take actions
            for agent in self.agents:
                intersection_pos = agent.intersection.position

                # Get current state for this agent
                state = current_states[intersection_pos]

                # Agent decides action based on state
                action = agent.decide_action(state)

                # Agent performs action
                agent.perform_action(action)

                # If we have previous state information, calculate reward and update Q-table
                if intersection_pos in previous_states:
                    prev_state = previous_states[intersection_pos]
                    reward = agent.calculate_reward(state)
                    agent.update_q_table(prev_state, agent.last_action, reward, state)

            # Store current states for next iteration's Q-learning updates
            previous_states = copy.deepcopy(current_states)

            # Spawn new vehicles
            self.spawn_vehicle()

            # Check for vehicle interactions (like avoiding collisions)
            self.check_vehicle_interactions()

            # Move vehicles
            for vehicle in self.vehicles:
                vehicle.move(self.grid_env)

                # Count finished vehicles
                if vehicle.finished and not hasattr(vehicle, 'counted'):
                    self.traffic_metrics['vehicles_finished'] += 1
                    vehicle.counted = True

            # Update traffic metrics
            self.update_metrics()

            # Visualize current state
            if visualize:
                self.visualizer.plot()
                plt.pause(0.1)
                time.sleep(0.1)  # Shorter delay for smoother animation

        # Final Q-learning updates for the last state
        for agent in self.agents:
            intersection_pos = agent.intersection.position
            if intersection_pos in previous_states:
                # For terminal state, use current reward without future value
                prev_state = previous_states[intersection_pos]
                final_state = current_states.get(intersection_pos, prev_state)
                reward = agent.calculate_reward(final_state)
                # Terminal state has no future reward
                agent.update_q_table(prev_state, agent.last_action, reward, final_state)

        # Display final metrics and Q-tables
        self.display_enhanced_metrics()
        plt.ioff()
        plt.show()

    def display_enhanced_metrics(self):
        import matplotlib.pyplot as plt

        # 3 rows: avg wait time, active vehicles, improvement
        fig, axs = plt.subplots(3, 1, figsize=(10, 12))

        # 1) Average waiting time per step
        steps = range(1, len(self.traffic_metrics['avg_wait_time']) + 1)
        axs[0].plot(steps, self.traffic_metrics['avg_wait_time'], 'r-')
        axs[0].set_title('Average Waiting Time')
        axs[0].set_xlabel('Simulation Step')
        axs[0].set_ylabel('Time Steps')
        axs[0].grid(True)

        # 2) Number of vehicles in system per step
        axs[1].plot(steps, self.traffic_metrics['vehicles_in_system'], 'b-')
        axs[1].set_title('Active Vehicles in System')
        axs[1].set_xlabel('Simulation Step')
        axs[1].set_ylabel('Number of Vehicles')
        axs[1].grid(True)

        # 3) Reduction in wait time vs start (performance improvement)
        if self.traffic_metrics['avg_wait_time']:
            initial_wait = self.traffic_metrics['avg_wait_time'][0]
            reduction = [initial_wait - w for w in self.traffic_metrics['avg_wait_time']]
        else:
            reduction = []
        axs[2].plot(steps, reduction, 'm-o')
        axs[2].set_title('Reduction in Avg Wait Time vs Start')
        axs[2].set_xlabel('Simulation Step')
        axs[2].set_ylabel('Wait Time Reduction')
        axs[2].grid(True)

        plt.tight_layout()
        plt.savefig('q_learning_metrics.png')
        plt.close(fig)

        # Console output of exact average-wait-time data
        print("\n-----------------------------\n")
        print(f"Total vehicles finished: {self.traffic_metrics['vehicles_finished']}")
        if self.traffic_metrics['avg_wait_time']:
            overall = sum(self.traffic_metrics['avg_wait_time']) / len(self.traffic_metrics['avg_wait_time'])
        else:
            overall = 0.0
        print(f"Overall average wait time: {overall:.2f}")
        print("Enhanced metrics saved to 'q_learning_metrics.png'")

    def save_agent_q_tables(self, run_id=None):
        if run_id is None:
            timestamp = datetime.datetime.now().strftime("%Y%m%d_%H%M%S")
            run_id = f"run_{timestamp}"

        save_dir = os.path.join("saved_models", run_id)
        os.makedirs(save_dir, exist_ok=True)

        saved_paths = []
        for i, agent in enumerate(self.agents):
            file_path = os.path.join(save_dir, f"agent_{i}_q_table.pkl")
            agent.save_q_table(file_path)
            saved_paths.append(file_path)

        print(f"Saved {len(saved_paths)} agent Q-tables to {save_dir}")
        return save_dir

    def load_agent_q_tables(self, load_dir):
        if not os.path.exists(load_dir):
            print(f"Directory not found: {load_dir}")
            return False

        loaded_count = 0
        for i, agent in enumerate(self.agents):
            file_path = os.path.join(load_dir, f"agent_{i}_q_table.pkl")
            if agent.load_q_table(file_path):
                loaded_count += 1

        print(f"Loaded {loaded_count}/{len(self.agents)} agent Q-tables from {load_dir}")
        return loaded_count > 0

    def run_continuous_session(self, num_runs=6, steps_per_run=100, load_path=None):

        # Create a directory for this continuous session
        timestamp = datetime.datetime.now().strftime("%Y%m%d_%H%M%S")
        session_dir = os.path.join("saved_models", f"continuous_session_{timestamp}")
        os.makedirs(session_dir, exist_ok=True)

        # Load previous Q-tables if specified
        if load_path:
            self.load_agent_q_tables(load_path)
            print(f"Continuing session from {load_path}")

        # Track metrics across runs
        all_metrics = {
            'avg_wait_times': [],
            'vehicles_finished': [],
            'avg_epsilon': []
        }

        # Run multiple simulations
        for run in range(num_runs):
            print(f"\n\n=== STARTING CONTINUOUS RUN {run + 1}/{num_runs} ===")

            # Reset environment but keep agent's Q-tables
            self.reset_environment()

            # Configure this run
            self.steps = steps_per_run

            # Run simulation
            self.run(save_metrics=False)

            # Save the Q-tables after this run
            run_save_dir = os.path.join(session_dir, f"run_{run + 1}")
            self.save_agent_q_tables(run_save_dir)

            # Collect metrics for this run
            avg_wait = sum(self.traffic_metrics['avg_wait_time']) / len(self.traffic_metrics['avg_wait_time']) if \
                self.traffic_metrics['avg_wait_time'] else 0
            all_metrics['avg_wait_times'].append(avg_wait)
            all_metrics['vehicles_finished'].append(self.traffic_metrics['vehicles_finished'])
            all_metrics['avg_epsilon'].append(self.agents[0].epsilon if self.agents else 0)

            print(
                f"Run {run + 1} completed - Avg Wait: {avg_wait:.2f}, Vehicles Completed: {self.traffic_metrics['vehicles_finished']}")

        # Plot continuous session progress across runs
        self.display_enhanced_metrics()

        return session_dir

    def reset_environment(self):
        """Reset the environment but keep the agents' Q-tables"""
        # Create new vehicles list
        self.vehicles = []
        self.vehicle_count = 0

        # Reset grid environment
        self.grid_env = GridEnvironment(width=self.grid_env.width, height=self.grid_env.height)

        # Create new agents but preserve their Q-tables
        old_q_tables = [agent.q_table for agent in self.agents]
        self.agents = [TrafficAgent(intersection) for intersection in self.grid_env.intersections.values()]

        # Transfer Q-tables to new agents
        for i, q_table in enumerate(old_q_tables):
            if i < len(self.agents):
                self.agents[i].q_table = q_table

        # Reset metrics
        self.traffic_metrics = {
            'avg_wait_time': [],
            'vehicles_in_system': [],
            'vehicles_finished': 0
        }

        # Update visualizer with new environment and vehicles
        self.visualizer = Visualize(self.grid_env, self.vehicles)


if __name__ == "__main__":
    # Create a simulation with your desired parameters
    sim = Simulation(steps=100, grid_width=3, grid_height=3)

    # Toggle this to True to enable continuous session
    continuous_session = True

    if continuous_session:
        # Run multiple simulation sessions with learning persisting between them
        num_runs = 5  # Number of simulation runs
        steps_per_run = 100  # Steps in each run
        load_path = None  # Set to a saved model path to continue from previous session

        sim.run_continuous_session(num_runs=num_runs, steps_per_run=steps_per_run, load_path=load_path)
    else:
        # Run a single simulation (the original behavior)
        sim.run()
