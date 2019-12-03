import pygame


class Camera:
    def __init__(self, world, x, y):
        self.world = world
        self.pos = pygame.math.Vector2(x, y)
        self.zoom = 0.4
        self.screen_center = pygame.math.Vector2(self.world.screen.get_size()) / 2

    def offset(self, pos):
        return (pos - self.pos) * self.zoom + self.screen_center

    def move_towards(self, target):
        self.pos *= 9
        self.pos += target
        self.pos /= 10
