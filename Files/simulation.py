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
    def __init__(self, steps, grid_width, grid_height):
        self.grid_env # Create Grid Environment
        self.vehicles = []
        self.agents = []
        self.steps =steps
        self.visualizer # Create Visualizer
        self.vehicle_count = 0
        self.trafic_density = 0.4
        self.traffic_metrics = {
            'avg_wait_time': [],
            'total_wait_time': 0,
            'vehicles_in_system': [],
            'vehicles_finished': 0
        }

    def spawn_vehicle(self):
        ...
    def update_metrics(self):
        ...
    def check_vehicle_interactions(self):
        ...
    def _distance(self,pos1,pos2) -> int:
        return ((pos1[0] - pos2[0]) ** 2 + (pos1[1] - pos2[1]) ** 2) ** 0.5
    def _is_vehicle_ahead(self, v1, v2):
        ...
    def display_metrics(self):
        ...
    def save_agent_q_tables(self, run_id=None):
        ...
    def load_agent_q_tables(self, load_dir):
        ...
    def run(self, visualize=True):
        ...
    def run_continuous_session(self, num_runs=5, steps_per_run=100, save_and_load_path=None):
        ...
    def _reset_environment(self):
        ...

if __name__ == '__main__':
    sim = Simulation(steps=100, grid_width=3 ,grid_height=3)
    continuous_session = True

    if continuous_session:
        num_runs = 5
        steps_per_run = 100
        save_and_load_path = "q_learning_metrics.txt"

        sim.run_continuous_session(num_runs=num_runs, steps_per_run=steps_per_run, save_and_load_path=save_and_load_path)
    else:
        sim.run()