import pygame
import math

# ENVIRONMENT CONSTANTS

SWIDTH = 1280
SHEIGHT = 720

BLACK = (0, 0, 0)
WHITE = (255, 255, 255)
GRAY = (128, 128, 128)
RED = (255, 0, 0)
GREEN = (0, 255, 0)


# HELPER FUNCTIONS

def rotate_point(origin, point, angle_degrees):
    ox, oy = origin
    px, py = point

    angle_rad = math.radians(angle_degrees)

    translated_x = px - ox
    translated_y = py - oy

    rotated_x = translated_x * math.cos(angle_rad) - translated_y * math.sin(angle_rad)
    rotated_y = translated_x * math.sin(angle_rad) + translated_y * math.cos(angle_rad)

    new_x = rotated_x + ox
    new_y = rotated_y + oy

    return pygame.math.Vector2(new_x, new_y)

def check_collision_car_track(car, track):
    car_lines = []
    for i in range(4):
        car_lines.append((car.points[i], car.points[(i + 1) % 4]))
    
    track_lines = []
    if len(track.inner) > 1:
        for i in range(len(track.inner)):
            track_lines.append((track.inner[i], track.inner[(i + 1) % len(track.inner)]))
    if len(track.outer) > 1:
        for i in range(len(track.outer)):
            track_lines.append((track.outer[i], track.outer[(i + 1) % len(track.outer)]))
    
    for car_line in car_lines:
        for track_line in track_lines:
            if check_line_collision(car_line[0], car_line[1], track_line[0], track_line[1]):
                return True
    return False

def check_line_collision(p1, p2, q1, q2):
    x1, y1 = p1
    x2, y2 = p2

    x3, y3 = q1
    x4, y4 = q2

    den = (y4-y3)*(x2-x1) - (x4-x3)*(y2-y1)
    if den == 0:
        return None

    uA = ((x4-x3)*(y1-y3) - (y4-y3)*(x1-x3)) / ((y4-y3)*(x2-x1) - (x4-x3)*(y2-y1));
    uB = ((x2-x1)*(y1-y3) - (y2-y1)*(x1-x3)) / ((y4-y3)*(x2-x1) - (x4-x3)*(y2-y1));
    
    if uA >= 0 and uA <= 1 and uB >= 0 and uB <= 1:
        xs = x1 + (uA * (x2-x1));
        ys = y1 + (uA * (y2-y1));
        return pygame.math.Vector2(xs, ys)
    
    return None

def check_car_reward(car, reward_gates):
    car_lines = []
    for i in range(4):
        car_lines.append((car.points[i], car.points[(i + 1) % 4]))
    
    idx = reward_gates.active_gate
    reward_gate = (reward_gates.start[idx], reward_gates.end[idx])

    for car_line in car_lines:
        if check_line_collision(car_line[0], car_line[1], reward_gate[0], reward_gate[1]):
            reward_gates.active_gate += 1
            if reward_gates.active_gate > len(reward_gates.start):
                reward_gates.active_gate = 0
            return True
    return False

# OBJECTS

class Car:
    def __init__(self, center_x, center_y):
        self.origin = pygame.math.Vector2(center_x, center_y)
        self.points = [pygame.math.Vector2(0, 0) for _ in range(4)]
        self.width = 10
        self.height = 15
        self.direction = 0
        self.velocity = 0.0

class Track:
    def __init__(self, file_name):
        self.outer = []
        self.inner = []
        try:
            with open(file_name, 'r') as track_file:
                lines = [line.strip() for line in track_file if line.strip()]
            
            idx = 0
            num_inner = int(lines[idx])
            idx += 1
            for _ in range(num_inner):
                x, y = map(float, lines[idx].split())
                self.inner.append(pygame.math.Vector2(x, y))
                idx += 1
            
            num_outer = int(lines[idx])
            idx += 1
            for _ in range(num_outer):
                x, y = map(float, lines[idx].split())
                self.outer.append(pygame.math.Vector2(x, y))
                idx += 1
        except (IOError, IndexError) as e:
            print(f"Error loading track file: {e}. Starting with an empty track.")

class RewardGates:
    def __init__(self, file_name):
        self.active_gate = 0
        self.start = []
        self.end = []

        try:
            with open(file_name, 'r') as track_file:
                lines = [line.strip() for line in track_file if line.strip()]
            
            idx = 0
            num_inner = int(lines[idx])
            idx += 1
            for _ in range(num_inner):
                x, y = map(float, lines[idx].split())
                self.start.append(pygame.math.Vector2(x, y))
                idx += 1

                x, y = map(float, lines[idx].split())
                self.end.append(pygame.math.Vector2(x, y))
                idx += 1
            
        except (IOError, IndexError) as e:
            print(f"Error loading reward gate file: {e}. Starting with no reward gates.")

# EVENTS

def update_car(car, action):
    car.velocity = max(car.velocity - 0.05, 1.0)

    if action == 0:
        car.velocity = min(car.velocity + 0.5, 5.0)
    if action == 1:
        car.velocity = max(car.velocity - 0.5, 1.0);
    if car.velocity > 0:
        if action == 2:
            car.direction -= 3
        if action == 3:
            car.direction += 3
    
    rad = math.radians(car.direction)
    s = math.sin(rad)
    c = math.cos(rad)

    car.origin.x += c * car.velocity
    car.origin.y += s * car.velocity

    w, h = car.width, car.height
    
    car.points[0] = pygame.math.Vector2(car.origin.x - s * w - c * h, car.origin.y + c * w - s * h)
    car.points[1] = pygame.math.Vector2(car.origin.x - s * w + c * h, car.origin.y + c * w + s * h)
    car.points[2] = pygame.math.Vector2(car.origin.x + s * w + c * h, car.origin.y - c * w + s * h)
    car.points[3] = pygame.math.Vector2(car.origin.x + s * w - c * h, car.origin.y - c * w - s * h)

def update_sensors(car, sensors):
    rad = math.radians(car.direction)
    s = math.sin(rad)
    c = math.cos(rad)

    start_point = pygame.math.Vector2(car.origin.x + c * 100, car.origin.y + s * 100)
    start_point = rotate_point(car.origin, start_point, -90)

    i = 0
    for _ in sensors:
        sensors[i] = rotate_point(car.origin, start_point, i * 45)
        i += 1

def get_current_state(car, sensors, track):
    start_point = car.origin

    end_points = []
    for end_point in sensors:

        collided = False
        num = len(track.inner)
        for i in range(num):
            if collided:
                break
            collision = check_line_collision(start_point, end_point, track.inner[i], track.inner[(i + 1) % num])
            if collision:
                collided = True
                end_points.append(collision)

        num = len(track.outer)
        for i in range(num):
            if collided:
                break
            collision = check_line_collision(start_point, end_point, track.outer[i], track.outer[(i + 1) % num])
            if collision:
                collided = True
                end_points.append(collision)
        
        if not collided:
            end_points.append(end_point)

    x0, y0 = start_point
    state = []
    for x1, y1 in end_points:
        dist = math.sqrt((x1 - x0) * (x1 - x0) + (y1 - y0) * (y1 - y0))
        state.append(dist)
    state.append(car.velocity)
    
    return state

# RENDERING

def draw_car(surface, car):
    pygame.draw.lines(surface, WHITE, True, car.points, 1)
    pygame.draw.circle(surface, WHITE, car.origin, 1)

def draw_track(surface, track):
    if len(track.outer) > 1:
        pygame.draw.lines(surface, GRAY, True, track.outer, 1)
    if len(track.inner) > 1:
        pygame.draw.lines(surface, GRAY, True, track.inner, 1)

def draw_sensors(surface, car, sensors, track):
    start_point = car.origin

    end_points = []
    for end_point in sensors:

        collided = False
        num = len(track.inner)
        for i in range(num):
            if collided:
                break
            collision = check_line_collision(start_point, end_point, track.inner[i], track.inner[(i + 1) % num])
            if collision:
                collided = True
                end_points.append(collision)

        num = len(track.outer)
        for i in range(len(track.outer)):
            if collided:
                break
            collision = check_line_collision(start_point, end_point, track.outer[i], track.outer[(i + 1) % num])
            if collision:
                collided = True
                end_points.append(collision)
        
        if not collided:
            end_points.append(end_point)
        
    for end_point in end_points:
        pygame.draw.line(surface, RED, start_point, end_point, 1)

def draw_reward_gates(surface, reward_gates):
    n = len(reward_gates.start)
    for i in range(n):
        if i == reward_gates.active_gate:
            color = GREEN
        else:
            color = RED
        pygame.draw.line(surface, color, reward_gates.start[i], reward_gates.end[i])