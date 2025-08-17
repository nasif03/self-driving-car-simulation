import pygame
import math
import sys

# Constants

SWIDTH = 1280
SHEIGHT = 720

BLACK = (0, 0, 0)
WHITE = (255, 255, 255)
GRAY = (128, 128, 128)
RED = (255, 0, 0)


# Helper Functions

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


# Objects

class Car:
    def __init__(self, center_x, center_y):
        self.origin = pygame.math.Vector2(center_x, center_y)
        self.points = [pygame.math.Vector2(0, 0) for _ in range(4)]
        self.width = 10
        self.height = 15
        self.direction = 0
        self.velocity = 0.0
        self.sensors = [pygame.math.Vector2(0, 0) for _ in range(5)]

    def draw(self, surface):
        pygame.draw.lines(surface, WHITE, True, self.points, 1)
        pygame.draw.circle(surface, WHITE, self.origin, 1)

    def update(self):
        keys = pygame.key.get_pressed()
        
        self.velocity = max(self.velocity - 0.05, 0.0)

        if keys[pygame.K_w]:
            self.velocity = min(self.velocity + 0.3, 5.0)
        if keys[pygame.K_s]:
            self.velocity = max(self.velocity - 0.4, 0.0);
        if self.velocity > 0:
            if keys[pygame.K_a]:
                self.direction -= 3
            if keys[pygame.K_d]:
                self.direction += 3
        
        rad = math.radians(self.direction)
        s = math.sin(rad)
        c = math.cos(rad)

        self.origin.x += c * self.velocity
        self.origin.y += s * self.velocity

        w, h = self.width, self.height
        
        self.points[0] = pygame.math.Vector2(self.origin.x - s * w - c * h, self.origin.y + c * w - s * h)
        self.points[1] = pygame.math.Vector2(self.origin.x - s * w + c * h, self.origin.y + c * w + s * h)
        self.points[2] = pygame.math.Vector2(self.origin.x + s * w + c * h, self.origin.y - c * w + s * h)
        self.points[3] = pygame.math.Vector2(self.origin.x + s * w - c * h, self.origin.y - c * w - s * h)

        start_point = pygame.math.Vector2(self.origin.x + c * 70, self.origin.y + s * 70)
        start_point = rotate_point(self.origin, start_point, -90)

        for i in range(5):
            self.sensors[i] = rotate_point(self.origin, start_point, i * 45)


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

    def draw(self, surface):
        if len(self.outer) > 1:
            pygame.draw.lines(surface, GRAY, True, self.outer, 1)
        if len(self.inner) > 1:
            pygame.draw.lines(surface, GRAY, True, self.inner, 1)

    def handle_input(self, event):
        if event.type == pygame.MOUSEBUTTONDOWN:
            if event.button == 1: 
                self.outer.append(pygame.mouse.get_pos())
            elif event.button == 3:
                self.inner.append(pygame.mouse.get_pos())

    def save(self, file_name):
        with open(file_name, 'w') as track_file:
            track_file.write(f"{len(self.inner)}\n")
            for p in self.inner:
                track_file.write(f"{p.x} {p.y}\n")
            
            track_file.write(f"{len(self.outer)}\n")
            for p in self.outer:
                track_file.write(f"{p.x} {p.y}\n")

def draw_sensors(surface, car : Car, track : Track):
    start_point = car.origin

    end_points = []
    for end_point in car.sensors:

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
    
    return end_points

def main():
    pygame.init()
    screen = pygame.display.set_mode((SWIDTH, SHEIGHT))
    pygame.display.set_caption("QCar")
    clock = pygame.time.Clock()

    player = Car(SWIDTH / 2, SHEIGHT / 2)
    track = Track("assets/track1.txt")
    
    frame_counter = 0
    running = True
    while running:
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                running = False
        
        # updates
        player.update()
        collided = check_collision_car_track(player, track)
        frame_counter += 1

        # draw
        screen.fill(BLACK)
        
        track.draw(screen)
        player.draw(screen)
        sensors = draw_sensors(screen, player, track)

        # debugging
        # if frame_counter % 60 == 0:
        #     x2, y2 = player.origin
        #     for x1, y1 in sensors:
        #         dist = math.sqrt((x1 - x2) * (x1 - x2) + (y1 - y2) * (y1 - y2))
        #         print(dist)

        if collided:
            pygame.draw.circle(screen, RED, player.origin, 2)
        
        pygame.display.flip()
        
        clock.tick(60)
        
    pygame.quit()
    sys.exit()

if __name__ == "__main__":
    main()