import pygame
from shapely.geometry import Point

COLOR_BLACK = (0, 0, 0)


class Obstacle:
    def __init__(self, world, x, y, size):
        self.world = world
        self.pos = pygame.math.Vector2(x, y)
        self.size = size

    def draw(self):
        pt = self.world.camera.offset(self.pos)
        pygame.draw.circle(self.world.screen, COLOR_BLACK, (int(pt.x), int(pt.y)),
                           int(self.size * self.world.camera.zoom))

    def get_boundary(self):
        return Point(self.pos.x, self.pos.y).buffer(self.size).boundary

