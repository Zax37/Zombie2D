import pygame
from entity import Entity

ZOMBIE_IMAGE = pygame.image.load('zombie.png')
ZOMBIE_MAX_SPEED = 2
ROTATION_SPEED = .1
COLOR_WHITE = (255, 255, 255)


class Zombie(Entity):
    def __init__(self, world, x, y):
        Entity.__init__(self, world, x, y, ZOMBIE_IMAGE, (90, 125), ZOMBIE_MAX_SPEED, ROTATION_SPEED)

    def update(self, time_elapsed):
        direction = self.pursuit(self.world.player)
        self.velocity += direction
        self.move()
        self.update_angle_from_heading()

    def draw(self):
        Entity.draw(self)
        if self.world.debug_mode:
            pygame.draw.circle(self.world.screen, COLOR_WHITE, (self.pos.x, self.pos.y), 3)