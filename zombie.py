import pygame
from actor import Actor
from entity import Entity
from steering_force import SteeringForce

ZOMBIE_IMAGE = pygame.image.load('zombie.png')
DEAD_IMAGE = pygame.image.load('blood.png')
ZOMBIE_MAX_SPEED = 9
ZOMBIE_MAX_FORCE = 22
ROTATION_SPEED = 30
COLOR_BLACK = (0, 0, 0)
COLOR_RED = (255, 0, 0)
COLOR_WHITE = (255, 255, 255)
PLAYER_DETECTION_LENGTH = 1000
HIDING_TIMEOUT = 150
MAX_HIDING_TIME = 70

class Zombie(Actor):
    def __init__(self, world, x, y):
        Actor.__init__(self, world, x, y, ZOMBIE_IMAGE, (90, 125), ZOMBIE_MAX_SPEED, ROTATION_SPEED)
        self.hide_timer = 0
        self.needs_to_change_cover = False
        self.kamikaze = False

    def process_behaviors(self):
        steering_force = SteeringForce(ZOMBIE_MAX_FORCE)

        if not steering_force.accumulate(self.heading):
            return steering_force.force

        if not steering_force.accumulate(self.avoid_obstacles() * 0.15):
            return steering_force.force

        if self.kamikaze and self.world.player:
            steering_force.accumulate(self.pursuit(self.world.player))
            return steering_force.force

        if not steering_force.accumulate(self.avoid_walls() * 0.6):
            return steering_force.force

        count = self.tag_close_entities(self.world.enemies)
        if self.world.player:
            if count >= 2:
                if count >= 4:
                    self.kamikaze = True
                if not steering_force.accumulate(self.pursuit(self.world.player) * count / 4):
                    return steering_force.force
            else:
                player_detection_length = PLAYER_DETECTION_LENGTH + self.world.player.size
                dist_from_player = (self.pos - self.world.player.pos).length()

                self.world.player.tagged = False
                if dist_from_player < player_detection_length:
                    self.world.player.tag()

                    if dist_from_player < player_detection_length / 5:
                        self.kamikaze = True
                    else:
                        factor = (1 - dist_from_player / player_detection_length) ** 2
                        if not steering_force.accumulate(self.evade(self.world.player) * factor):
                            return steering_force.force

        # if not steering_force.accumulate(self.separation(self.world.enemies)):
        #    return steering_force.force
        # if not steering_force.accumulate(self.alignment(self.world.enemies)):
        #    return steering_force.force
        # if not steering_force.accumulate(self.cohesion(self.world.enemies)):
        #    return steering_force.force

        if count < 2:
            if self.needs_to_change_cover:
                self.hide_timer -= 1
                if self.hide_timer <= 0:
                    self.needs_to_change_cover = False
            elif self.world.player:
                hide_force = self.hide(self.world.player)
                if hide_force.length() < self.size:
                    self.hide_timer += 1
                    if self.hide_timer >= MAX_HIDING_TIME:
                        self.needs_to_change_cover = True
                        self.hide_timer = HIDING_TIMEOUT

                if steering_force.accumulate(hide_force):
                    return steering_force.force

        if not steering_force.accumulate(self.wander() * 2):
            return steering_force.force

        return steering_force.force

    def update(self, time_elapsed):
        self.velocity += self.process_behaviors()

        self.move()
        self.update_angle_from_heading()

        player = self.world.player
        if player and (self.pos - player.pos).length() <= self.size + player.size + 1:
            player.hurt()

    def draw(self):
        Actor.draw(self)
        if self.world.debug_mode:
            pt = self.world.camera.offset(self.pos)
            pygame.draw.circle(self.world.screen, COLOR_WHITE, (int(pt.x), int(pt.y)), 3)

            pygame.draw.circle(self.world.screen, COLOR_BLACK, (int(pt.x), int(pt.y)),
                               int(PLAYER_DETECTION_LENGTH * self.world.camera.zoom), 1)

    def kill(self):
        self.world.enemies.remove(self)
        blood = Entity(self.world, self.pos.x, self.pos.y, DEAD_IMAGE, (125, 115))
        blood.angle = self.angle
        self.world.misc.append(blood)
