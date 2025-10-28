from traffic_light import TrafficLight

class Intersection:
    def __init__(self, position):
        self.position = position
        self.traffic_light = TrafficLight()

    def update(self):
        self.traffic_light.update()

    def get_light_state(self, direction):
        return self.traffic_light.get_light_state(direction)

class GridEnvironment:
    def __init__(self, width=2, height=2):
        self.width = width
        self.height = height
        self.intersections = {}
        for x in range(width):
            for y in range(height):
                self.intersections[(x, y)] = Intersection((x, y))

    def update(self):
        for intersection in self.intersections.values():
            intersection.update()

    def is_within_grid(self, position):
        x, y = position
        return 0 <= x < self.width and 0 <= y < self.height

    def get_intersection_at(self, position):
        return self.intersections.get(position, None)

    def is_within_bounds(self, pos):
        x, y = pos
        return -1 <= x <= self.width and -1 <= y <= self.height