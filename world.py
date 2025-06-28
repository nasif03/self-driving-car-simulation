import sys
import math
import pygame
from utils import blit_rotate_center

# pygame setup
FPS = 60
pygame.init()
SCREEN = pygame.display.set_mode((1280, 720), vsync = 1)
clock = pygame.time.Clock()

class Car():
    def __init__(self):
        self.image = pygame.image.load('assets/car.png')
        self.velocity = 0
        self.angle = 0
        self.x, self.y = 200, 200

    def rotate(self, left=False, right=False):
        if left:
            self.angle += 3
        elif right:
            self.angle -= 3

    def accelerate(self, acc):
        self.velocity = min(self.velocity + acc, 10)
        self.velocity = max(self.velocity, 0)

    def move(self):
        rad = math.radians(self.angle)
        vertical = math.cos(rad) * self.velocity
        horizontal = math.sin(rad) * self.velocity

        self.x += vertical
        self.y -= horizontal

    def draw(self, surf):
        blit_rotate_center(SCREEN, self.image, (self.x, self.y), self.angle)

def main():
    playerCar = Car()

    while True:
        clock.tick(FPS)
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                sys.exit(0)

        # update
        keys = pygame.key.get_pressed()
        if keys[pygame.K_w]:
            playerCar.accelerate(0.3)
        if keys[pygame.K_s]:
            playerCar.accelerate(-0.3)
        vel = playerCar.velocity
        if vel != 0 and keys[pygame.K_a]:
            playerCar.rotate(left = True)
        if vel != 0 and keys[pygame.K_d]:
            playerCar.rotate(right = True)
        else:
            playerCar.accelerate(-0.1)
        playerCar.move()

        # draw
        SCREEN.fill("grey")
        playerCar.draw(SCREEN)
    
        pygame.display.flip()

if __name__ == "__main__":
    main()