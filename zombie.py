import pygame
from entity import Entity
from enum import Enum

ZOMBIE_IMAGE = pygame.image.load('zombie.png')
DEAD_IMAGE = pygame.image.load('blood.png')
ZOMBIE_MAX_SPEED = 2
ROTATION_SPEED = .1
COLOR_WHITE = (255, 255, 255)


class ZombieState(Enum):
    WANDERING = 1,
    CHASE = 2,
    DEAD = 0xD34D


class Zombie(Entity):
    def __init__(self, world, x, y):
        Entity.__init__(self, world, x, y, ZOMBIE_IMAGE, (90, 125), ZOMBIE_MAX_SPEED, ROTATION_SPEED)
        self.set_state(ZombieState.WANDERING)

    def set_state(self, state):
        self.state = state
        self.debug_text = self.world.debug_font.render(str(self.state), False, (0, 0, 0))

    def update(self, time_elapsed):
        distance_from_player = self.pos.distance_to(self.world.player.pos)
        direction = pygame.math.Vector2(0, 0)
        if self.state == ZombieState.WANDERING:
            direction = self.wander()

            if distance_from_player < 600:
                self.set_state(ZombieState.CHASE)
        elif self.state == ZombieState.CHASE:
            direction = self.pursuit(self.world.player)

            if distance_from_player > 1200:
                self.set_state(ZombieState.WANDERING)
        else:
            self.velocity /= 2

        self.velocity += direction
        self.move()
        self.update_angle_from_heading()

    def draw(self):
        Entity.draw(self)
        if self.world.debug_mode:
            pt = self.world.camera.offset(self.pos)
            pygame.draw.circle(self.world.screen, COLOR_WHITE, (int(pt.x), int(pt.y)), 3)
            self.world.screen.blit(self.debug_text, (int(pt.x), int(pt.y)))

    def kill(self):
        self.image = DEAD_IMAGE
        self.set_state(ZombieState.DEAD)

    def is_dead(self):
        return self.state == ZombieState.DEAD
