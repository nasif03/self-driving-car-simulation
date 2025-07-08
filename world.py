import sys
import math
import pygame
import pygame.surface
from utils import blit_rotate_center

# pygame setup
FPS = 60
SWIDTH = 1920
SHEIGHT = 1080
pygame.init()
screen = pygame.display.set_mode((SWIDTH, SHEIGHT), vsync = 1)
clock = pygame.time.Clock()
background = pygame.image.load("assets/circle.png").convert_alpha()
image_rect = background.get_rect(center=(SWIDTH // 2, SHEIGHT // 2))

def RotatePoint(point, origin, angle):
    rad = math.radians(angle)
    s = math.sin(rad)
    c = math.cos(rad)

    point.x -= origin.x
    point.y -= origin.y
    
    xnew = point.x * c - point.y * s
    ynew = point.x * s + point.y * c
    
    point.x = xnew + origin.x
    point.y = ynew + origin.y

class Polygon:
    def __init__(self, points = []):
        self.points = points
        self.center = pygame.Vector2(SWIDTH / 2, SHEIGHT / 2)

    def add_point(self, point):
        self.points.append(point)
    
    def draw(self):
        pygame.draw.polygon(screen, "BLACK", self.points, 4)

    def rotate(self, angle):
        for point in self.points:
            RotatePoint(point, self.center, angle)
    
    def move(self, dir):
        self.center.x += dir.x
        self.center.y += dir.y
        
        for point in self.points:
            point.x += dir.x
            point.y += dir.y

class Car:
    def __init__(self):
        self.poly = Polygon()
        self.center = pygame.Vector2(SWIDTH / 2, SHEIGHT / 2)

        self.poly.add_point(pygame.Vector2(self.center.x - 60, self.center.y - 40))
        self.poly.add_point(pygame.Vector2(self.center.x - 60, self.center.y + 40))
        self.poly.add_point(pygame.Vector2(self.center.x + 60, self.center.y + 40))
        self.poly.add_point(pygame.Vector2(self.center.x + 60, self.center.y - 40))

        self.velocity = 0;
        self.direction = 0;

    def check_collision(self):
        for point in self.poly.points:
            x, y = point
            x = int(x)
            y = int(y)

            if image_rect.collidepoint(x, y):
                x = x - image_rect.left
                y = y - image_rect.top
                pixel_color = background.get_at((x, y))
                if pixel_color.a == 0:
                    return False
        return True

    def draw(self):
        self.poly.draw()

    def update(self):
        self.velocity = max(0, self.velocity - 0.1)
        keys = pygame.key.get_pressed()
        if keys[pygame.K_w]:
            self.velocity = min(self.velocity + 0.5, 7)
        if keys[pygame.K_s]:
            self.velocity = max(self.velocity - 0.5, 0)
        if keys[pygame.K_a] and self.velocity > 0:
            self.poly.rotate(-3)
            self.direction -= 3
        if keys[pygame.K_d] and self.velocity > 0:
            self.poly.rotate(3)
            self.direction += 3

        dir = pygame.Vector2()
        rad = math.radians(self.direction)
        dir.x = self.velocity * math.cos(rad)
        dir.y = self.velocity * math.sin(rad)
        self.poly.move(dir)

def main():
    car = Car()

    while True:
        clock.tick(FPS)
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                sys.exit(0)

        # update
        car.update()
        
        # draw
        if car.check_collision():
            screen.fill("WHITE")
        else:
            screen.fill("RED")
        screen.blit(background, image_rect)

        car.poly.draw()

        pygame.display.flip()

if __name__ == "__main__":
    main()