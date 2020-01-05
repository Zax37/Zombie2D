import pygame
from actor import Actor
from entity import Entity

ZOMBIE_IMAGE = pygame.image.load('zombie.png')
DEAD_IMAGE = pygame.image.load('blood.png')
ZOMBIE_MAX_SPEED = 3
ROTATION_SPEED = .1
COLOR_RED = (255, 0, 0)
COLOR_WHITE = (255, 255, 255)


class Zombie(Actor):
    def __init__(self, world, x, y):
        Actor.__init__(self, world, x, y, ZOMBIE_IMAGE, (90, 125), ZOMBIE_MAX_SPEED, ROTATION_SPEED)

    def update(self, time_elapsed):
        direction = self.wander()

        detection_length = self.get_detection_box_length()
        dist_from_player = (self.pos - self.world.player.pos).length()

        self.world.player.tagged = False
        if dist_from_player < detection_length:
            self.world.player.tagged = True
            evade_factor = 1 - dist_from_player / detection_length
            direction *= 1 - evade_factor
            direction += self.evade(self.world.player) * evade_factor * 25

        direction += self.avoid_obstacles()

        self.velocity += direction
        self.move()
        self.update_angle_from_heading()

    def draw(self):
        Actor.draw(self)
        if self.world.debug_mode:
            pt = self.world.camera.offset(self.pos)
            pygame.draw.circle(self.world.screen, COLOR_WHITE, (int(pt.x), int(pt.y)), 3)

            pt2 = pt + self.avoid_obstacles()
            pygame.draw.line(self.world.screen, COLOR_RED, (int(pt.x), int(pt.y)), (int(pt2.x), int(pt2.y)))

    def kill(self):
        self.world.enemies.remove(self)
        blood = Entity(self.world, self.pos.x, self.pos.y, DEAD_IMAGE, (125, 115))
        blood.angle = self.angle
        self.world.misc.append(blood)
