import pygame
from actor import Actor
from entity import Entity

ZOMBIE_IMAGE = pygame.image.load('zombie.png')
DEAD_IMAGE = pygame.image.load('blood.png')
ZOMBIE_MAX_SPEED = 2
ROTATION_SPEED = .1
COLOR_WHITE = (255, 255, 255)


class Zombie(Actor):
    def __init__(self, world, x, y):
        Actor.__init__(self, world, x, y, ZOMBIE_IMAGE, (90, 125), ZOMBIE_MAX_SPEED, ROTATION_SPEED)

    def set_state(self, state):
        self.state = state
        self.debug_text = self.world.debug_font.render(str(self.state), False, (0, 0, 0))

    def update(self, time_elapsed):
        direction = self.pursuit(self.world.player)
        self.velocity += direction
        self.move()
        self.update_angle_from_heading()

    def draw(self):
        Actor.draw(self)
        if self.world.debug_mode:
            pt = self.world.camera.offset(self.pos)
            pygame.draw.circle(self.world.screen, COLOR_WHITE, (int(pt.x), int(pt.y)), 3)
            self.world.screen.blit(self.debug_text, (int(pt.x), int(pt.y)))

    def kill(self):
        self.world.enemies.remove(self)
        blood = Entity(self.world, self.pos.x, self.pos.y, DEAD_IMAGE, (125, 115))
        blood.angle = self.angle
        self.world.misc.append(blood)
