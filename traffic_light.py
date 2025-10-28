import time

class TrafficLight:
    def __init__(self, green_duration=4, yellow_duration=1):
        self.green_duration = green_duration
        self.yellow_duration = yellow_duration
        self.current_state = 'NS_GREEN'
        self.state_start_time = time.time()

    def update(self):
        elapsed_time = time.time() - self.state_start_time

        if self.current_state in ['NS_GREEN', 'EW_GREEN']:
            if elapsed_time >= self.green_duration:
                self._switch_to_yellow()
        elif self.current_state in ['NS_YELLOW', 'EW_YELLOW']:
            if elapsed_time >= self.yellow_duration:
                self._switch_to_next_green()

    def _switch_to_yellow(self):
        if self.current_state == 'NS_GREEN':
            self.current_state = 'NS_YELLOW'
        elif self.current_state == 'EW_GREEN':
            self.current_state = 'EW_YELLOW'
        self.state_start_time = time.time()

    def _switch_to_next_green(self):
        if self.current_state == 'NS_YELLOW':
            self.current_state = 'EW_GREEN'
        elif self.current_state == 'EW_YELLOW':
            self.current_state = 'NS_GREEN'
        self.state_start_time = time.time()

    def get_light_state(self, direction):
        if self.current_state == 'NS_GREEN':
            return 'GREEN' if direction in ['N', 'S'] else 'RED'
        elif self.current_state == 'EW_GREEN':
            return 'GREEN' if direction in ['E', 'W'] else 'RED'
        else:
            return 'RED'  # Treat yellow as red

    def __repr__(self):
        return f"TrafficLight(state={self.current_state})"
