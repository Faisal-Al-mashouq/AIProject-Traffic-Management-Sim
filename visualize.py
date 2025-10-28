import matplotlib.pyplot as plt
import matplotlib.patches as patches
import numpy as np
import math

class Visualize:
    def __init__(self, grid_env, vehicles):
        self.grid_env = grid_env
        self.vehicles = vehicles
        self.fig, self.ax = plt.subplots(figsize=(10, 10))
        plt.ion()
        self.road_width = 0.4
        self.lane_width = self.road_width / 2  # Width for each lane
        self.lane_markings = True

        # Define vehicle size to fit within lanes
        self.vehicle_width = self.lane_width * 0.8  # Vehicle width as a proportion of lane width
        self.vehicle_length = self.vehicle_width * 1.8  # Vehicle length (longer than width)

    def plot(self):
        self.ax.clear()
        self.ax.set_xticks([])
        self.ax.set_yticks([])
        self.ax.tick_params(left=False, bottom=False, labelleft=False, labelbottom=False)
        self.ax.set_title('Traffic Simulation')

        # Add a bit more space around the grid
        buffer = 0.2
        self.ax.set_xlim(-1 - buffer, self.grid_env.width + buffer)
        self.ax.set_ylim(-1 - buffer, self.grid_env.height + buffer)

        # Draw roads
        self._draw_roads()

        # Draw intersections
        self._draw_intersections()

        # Draw vehicles as boxes
        self._draw_vehicles()

        # Add legend for traffic light states
        self._add_legend()

        plt.pause(0.01)

    def _draw_roads(self):
        # Draw horizontal roads
        for y in range(0, self.grid_env.height):
            # Main road
            self.ax.add_patch(
                patches.Rectangle(
                    (-1, y - self.road_width / 2),
                    self.grid_env.width + 1,
                    self.road_width,
                    linewidth=1,
                    edgecolor='black',
                    facecolor='#555555',
                    alpha=0.8
                )
            )

            # Draw solid center line for horizontal roads
            self.ax.plot(
                [-1, -0.22],
                [y, y],
                'y-',
                linewidth=2,
                solid_capstyle='round'
            )

            self.ax.plot(
                [0.21, 0.79],
                [y, y],
                'y-',
                linewidth=2,
                solid_capstyle='round'
            )

            self.ax.plot(
                [1.22, 1.79],
                [y, y],
                'y-',
                linewidth=2,
                solid_capstyle='round'
            )

            self.ax.plot(
                [2.22, 3],
                [y, y],
                'y-',
                linewidth=2,
                solid_capstyle='round'
            )

            # Draw dashed lane markers for each side
            for x in np.arange(-1, self.grid_env.width, 0.3):
                # Bottom lane dash
                self.ax.plot(
                    [x, x + 0.1],
                    [y - self.lane_width / 2, y - self.lane_width / 2],
                    'w--',
                    linewidth=1,
                    dashes=[5, 10]
                )
                # Top lane dash
                self.ax.plot(
                    [x, x + 0.1],
                    [y + self.lane_width / 2, y + self.lane_width / 2],
                    'w--',
                    linewidth=1,
                    dashes=[5, 10]
                )

        # Draw vertical roads
        for x in range(0, self.grid_env.width):
            # Main road
            self.ax.add_patch(
                patches.Rectangle(
                    (x - self.road_width / 2, -1),
                    self.road_width,
                    self.grid_env.height + 1,
                    linewidth=1,
                    edgecolor='black',
                    facecolor='#555555',
                    alpha=0.8
                )
            )

            # Draw solid center line for vertical roads
            self.ax.plot(
                [x, x],
                [-1, -0.22],
                'y-',
                linewidth=2,
                solid_capstyle='round'
            )

            self.ax.plot(
                [x, x],
                [0.21, 0.79],
                'y-',
                linewidth=2,
                solid_capstyle='round'
            )

            self.ax.plot(
                [x, x],
                [1.21, 1.79],
                'y-',
                linewidth=2,
                solid_capstyle='round'
            )

            self.ax.plot(
                [x, x],
                [2.22, 3],
                'y-',
                linewidth=2,
                solid_capstyle='round'
            )

            # Draw dashed lane markers for each side
            for y in np.arange(-1, self.grid_env.height, 0.3):
                # Left lane dash
                self.ax.plot(
                    [x - self.lane_width / 2, x - self.lane_width / 2],
                    [y, y + 0.1],
                    'w--',
                    linewidth=1,
                    dashes=[5, 10]
                )
                # Right lane dash
                self.ax.plot(
                    [x + self.lane_width / 2, x + self.lane_width / 2],
                    [y, y + 0.1],
                    'w--',
                    linewidth=1,
                    dashes=[5, 10]
                )

    def _draw_intersections(self):
        for pos, intersection in self.grid_env.intersections.items():
            x, y = pos
            state = intersection.traffic_light.current_state

            # Draw the intersection square
            self.ax.add_patch(
                patches.Rectangle(
                    (x - self.road_width / 2, y - self.road_width / 2),
                    self.road_width,
                    self.road_width,
                    linewidth=1,
                    edgecolor='black',
                    facecolor='#555555',
                    alpha=0.8
                )
            )

            # Determine light size
            light_size = 0.15

            # Compute colors based on current state
            ns_color = 'green' if 'NS_GREEN' in state else 'red' if 'EW_GREEN' in state else 'yellow'
            ew_color = 'green' if 'EW_GREEN' in state else 'red' if 'NS_GREEN' in state else 'yellow'

            # Draw traffic light boxes with labels
            # North-South traffic light
            self.ax.add_patch(
                patches.Rectangle(
                    (x - light_size, y + self.road_width / 4),
                    light_size * 2,
                    light_size,
                    facecolor='black',
                    edgecolor='white',
                    alpha=0.7
                )
            )
            # N-S light
            self.ax.add_patch(
                patches.Circle(
                    (x, y + self.road_width / 4),
                    light_size / 2,
                    facecolor=ns_color,
                    edgecolor='black',
                    alpha=0.8
                )
            )
            # Add label "NS" above the light
            self.ax.text(
                x,
                y + self.road_width / 4 + light_size * 0.8,
                "NS",
                fontsize=6,
                ha='center',
                va='center',
                color='white',
                bbox=dict(facecolor='black', alpha=0.5, pad=1)
            )

            # East-West traffic light
            self.ax.add_patch(
                patches.Rectangle(
                    (x + self.road_width / 4, y - light_size),
                    light_size,
                    light_size * 2,
                    facecolor='black',
                    edgecolor='white',
                    alpha=0.7
                )
            )
            # E-W light
            self.ax.add_patch(
                patches.Circle(
                    (x + self.road_width / 4, y),
                    light_size / 2,
                    facecolor=ew_color,
                    edgecolor='black',
                    alpha=0.8
                )
            )
            # Add label "EW" to the right of the light
            self.ax.text(
                x + self.road_width / 4 + light_size * 0.8,
                y,
                "EW",
                fontsize=6,
                ha='center',
                va='center',
                color='white',
                bbox=dict(facecolor='black', alpha=0.5, pad=1)
            )

    def _draw_vehicles(self):
        for vehicle in self.vehicles:
            if not vehicle.finished:
                # Adjust position based on direction to stay in the correct lane
                adjusted_position = self._adjust_position_for_lane(vehicle)

                # Create properly oriented vehicle shape
                self._draw_vehicle_shape(vehicle, adjusted_position)

                # Add vehicle ID text
                x, y = adjusted_position
                self.ax.text(x, y, str(vehicle.vehicle_id),
                             fontsize=8, ha='center', va='center', color='white')

                # Visualize waiting time if vehicle is waiting
                if vehicle.waiting and vehicle.waiting_time > 0:
                    offset_y = 0.1 if vehicle.direction in ['N', 'S'] else 0.05
                    self.ax.text(
                        x,
                        y + offset_y,
                        f"Wait: {vehicle.waiting_time}",
                        fontsize=6,
                        ha='center',
                        va='center',
                        color='red',
                        bbox=dict(facecolor='white', alpha=0.5, pad=1)
                    )

    def _draw_vehicle_shape(self, vehicle, position):
        x, y = position

        # Create a properly oriented vehicle shape
        width = self.vehicle_width
        length = self.vehicle_length

        # Define angle based on direction (in radians)
        angle_rad = {
            'N': math.pi / 2,  # 90 degrees
            'S': -math.pi / 2,  # -90 degrees
            'E': 0,  # 0 degrees
            'W': math.pi  # 180 degrees
        }[vehicle.direction]

        # Create a rectangle patch
        rect = patches.Rectangle(
            (x - length / 2, y - width / 2),  # (x,y) is center, but Rectangle expects bottom-left
            length, width,  # Longer in the direction of travel
            angle=math.degrees(angle_rad),  # Convert to degrees for matplotlib
            rotation_point='center',  # Rotate around center
            facecolor=vehicle.color,
            edgecolor='black',
            alpha=1.0
        )

        # Add patch to the plot
        self.ax.add_patch(rect)

    def _adjust_position_for_lane(self, vehicle):
        x, y = vehicle.position

        # Lane offset - how far from the center of the road
        lane_offset = self.lane_width / 3  # Slightly less than half lane width for margin

        if vehicle.direction == 'N':  # Moving up, stay on right side
            return x + lane_offset, y
        elif vehicle.direction == 'S':  # Moving down, stay on right side
            return x - lane_offset, y
        elif vehicle.direction == 'E':  # Moving right, stay on right side
            return x, y + lane_offset
        elif vehicle.direction == 'W':  # Moving left, stay on right side
            return x, y - lane_offset

        return x, y  # Default case, no adjustment

    def _add_legend(self):
        # Add legend for traffic lights
        green_patch = patches.Patch(color='green', alpha=0.5, label='Green Light')
        red_patch = patches.Patch(color='red', alpha=0.5, label='Red Light')
        yellow_patch = patches.Patch(color='yellow', alpha=0.5, label='Yellow Light')


        self.ax.legend(
            handles=[green_patch, red_patch, yellow_patch],
            loc='upper right',
            bbox_to_anchor=(1, 1)
        )