from traffic_light import TrafficLight 

class Intersection:
    def __init__(self, pos, green_duration = 10, yellow_duration=3):
        self.pos = pos
        self.traffic_light = TrafficLight(green_duration=green_duration,yellow_duration=yellow_duration)

    def update(self):
        self.traffic_light.update()

    def get_light_state(self, direction):
        return self.traffic_light.get_light_state(direction=direction)

    
class GridEnvironment:
    def __init__(self, width =3, height=3):
        self.width = width
        self.height = height
        self.intersections = {}
        for x in range(width):
            for y in range(height):
                self.intersections[(x, y)] = Intersection((x, y))

    def update(self):
        for intersection in self.intersections.values():
            intersection.update()
    
    def is_within_grid(self, pos) -> bool:
        x, y = pos
        return 0 <= x < self.width and 0 <= y < self.height
    
    def get_intersection_at(self, pos):
        return self.intersections.get(pos, None)

