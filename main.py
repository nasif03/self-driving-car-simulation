import pygame
import math
import sys

SWIDTH = 1280
SHEIGHT = 720

BLACK = (0, 0, 0)
WHITE = (255, 255, 255)
GRAY = (128, 128, 128)
RED = (255, 0, 0)

class Car:
    def __init__(self, center_x, center_y):
        self.origin = pygame.math.Vector2(center_x, center_y)
        self.points = [pygame.math.Vector2(0, 0) for _ in range(4)]
        self.width = 10
        self.height = 15
        self.direction = 0
        self.velocity = 0.0

    def draw(self, surface):
        pygame.draw.lines(surface, WHITE, True, self.points, 1)
        pygame.draw.circle(surface, WHITE, self.origin, 1)

    def update(self):
        keys = pygame.key.get_pressed()
        
        self.velocity = max(self.velocity - 0.1, 0.0)

        if keys[pygame.K_w]:
            self.velocity = min(self.velocity + 0.5, 5.0)
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

def check_line_collision(p1, q1, p2, q2):
    def orientation(p, q, r):
        val = (q.y - p.y) * (r.x - q.x) - (q.x - p.x) * (r.y - q.y)
        if val == 0: return 0
        return 1 if val > 0 else 2

    def on_segment(p, q, r):
        return (q.x <= max(p.x, r.x) and q.x >= min(p.x, r.x) and
                q.y <= max(p.y, r.y) and q.y >= min(p.y, r.y))

    o1 = orientation(p1, q1, p2)
    o2 = orientation(p1, q1, q2)
    o3 = orientation(p2, q2, p1)
    o4 = orientation(p2, q2, q1)

    if o1 != 0 and o2 != 0 and o3 != 0 and o4 != 0:
        if o1 != o2 and o3 != o4:
            return True

    if o1 == 0 and on_segment(p1, p2, q1): return True
    if o2 == 0 and on_segment(p1, q2, q1): return True
    if o3 == 0 and on_segment(p2, p1, q2): return True
    if o4 == 0 and on_segment(p2, q1, q2): return True

    return False

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

def main():
    pygame.init()
    screen = pygame.display.set_mode((SWIDTH, SHEIGHT))
    pygame.display.set_caption("QCar")
    clock = pygame.time.Clock()

    player = Car(SWIDTH / 2, SHEIGHT / 2)
    track = Track("assets/track1.txt")
    
    running = True
    while running:
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                running = False
            
        player.update()

        collided = check_collision_car_track(player, track)
        
        screen.fill(BLACK)
        
        track.draw(screen)
        player.draw(screen)
        
        if collided:
            pygame.draw.circle(screen, RED, player.origin, 2)
        
        pygame.display.flip()
        
        clock.tick(60)
        
    pygame.quit()
    sys.exit()

if __name__ == "__main__":
    main()