import pygame

COLOR_BLACK = (0, 0, 0)


class Obstacle:
    def __init__(self, world, x, y, size):
        self.world = world
        self.pos = pygame.math.Vector2(x, y)
        self.size = size

    def draw(self):
        pt = self.world.camera.offset(self.pos)
        pygame.draw.circle(self.world.screen, COLOR_BLACK, (int(pt.x), int(pt.y)), self.size)
