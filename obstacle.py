import pygame
from entity import Entity

COLOR_BLACK = (0, 0, 0)
COLOR_RED = (255, 0, 0)


class Obstacle(Entity):
    def __init__(self, world, x, y, size):
        Entity.__init__(self, world, x, y)
        self.size = size

    def draw(self):
        pt = self.world.camera.offset(self.pos)
        pygame.draw.circle(self.world.screen, COLOR_BLACK, (int(pt.x), int(pt.y)),
                           int(self.size * self.world.camera.zoom))
        if self.world.debug_mode and self.tagged:
            pygame.draw.circle(self.world.screen, COLOR_RED, (int(pt.x), int(pt.y)),
                               int(self.size * self.world.camera.zoom))
