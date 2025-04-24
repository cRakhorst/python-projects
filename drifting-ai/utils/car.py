import pygame
import math

class Car:
    def __init__(self, x, y, speed=0, angle=0):
        self.x = x
        self.y = y
        self.speed = speed
        self.angle = angle
        self.width = 40
        self.height = 70

    def update(self, dt, steering, throttle, brake):
        self.speed += throttle - brake
        self.angle += steering * 5
        self.x += self.speed * math.cos(math.radians(self.angle)) * dt
        self.y += self.speed * math.sin(math.radians(self.angle)) * dt

    def reset(self, x, y):
        self.x = x
        self.y = y
        self.speed = 0
        self.angle = 0

    def get_inputs(self):
        return [self.x, self.y, self.speed, self.angle]

    def draw(self, screen):
        pygame.draw.rect(screen, (255, 0, 0), (self.x, self.y, self.width, self.height))

