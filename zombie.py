import pygame
from actor import Actor
from entity import Entity
from steering_force import SteeringForce

ZOMBIE_IMAGE = pygame.image.load('zombie.png')
DEAD_IMAGE = pygame.image.load('blood.png')
ZOMBIE_MAX_SPEED = 10
ZOMBIE_MAX_FORCE = 20
ROTATION_SPEED = 50
COLOR_RED = (255, 0, 0)
COLOR_WHITE = (255, 255, 255)
PLAYER_DETECTION_LENGTH = 450
MAX_HIDING_TIME = 70
HIDING_TIMEOUT = 500


class Zombie(Actor):
    def __init__(self, world, x, y):
        Actor.__init__(self, world, x, y, ZOMBIE_IMAGE, (90, 125), ZOMBIE_MAX_SPEED, ROTATION_SPEED)
        self.hide_timer = 0
        self.needs_to_change_cover = False

    def process_behaviors(self):
        steering_force = SteeringForce(ZOMBIE_MAX_FORCE)

        if not steering_force.accumulate(self.avoid_walls()):
            return steering_force.force

        if not steering_force.accumulate(self.avoid_obstacles()):
            return steering_force.force

        count = self.tag_close_entities(self.world.enemies)
        if self.world.player:
            if count > 0:
                if not steering_force.accumulate(self.pursuit(self.world.player) * count / 3):
                    return steering_force.force
            else:
                player_detection_length = PLAYER_DETECTION_LENGTH + self.world.player.size
                dist_from_player = (self.pos - self.world.player.pos).length()

                self.world.player.tagged = False
                if dist_from_player < player_detection_length:
                    self.world.player.tag()
                    evade_factor = (1 - dist_from_player / player_detection_length) ** 2

                    if not steering_force.accumulate(self.evade(self.world.player) * evade_factor):
                        return steering_force.force

        # if not steering_force.accumulate(self.separation(self.world.enemies)):
        #    return steering_force.force
        # if not steering_force.accumulate(self.alignment(self.world.enemies)):
        #    return steering_force.force
        # if not steering_force.accumulate(self.cohesion(self.world.enemies)):
        #    return steering_force.force

        if self.needs_to_change_cover:
            self.hide_timer -= 1
            if self.hide_timer <= 0:
                self.needs_to_change_cover = False
        elif self.world.player:
            if steering_force.accumulate(self.hide(self.world.player) * (1 - self.hide_timer / MAX_HIDING_TIME)):
                self.hide_timer += 1
                if self.hide_timer >= MAX_HIDING_TIME:
                    self.hide_timer = HIDING_TIMEOUT
                    self.needs_to_change_cover = True
            else:
                return steering_force.force

        if not steering_force.accumulate(self.wander()):
            return steering_force.force

        steering_force.accumulate(self.heading * 10)
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

            pygame.draw.circle(self.world.screen, COLOR_WHITE, (int(pt.x), int(pt.y)),
                               int(PLAYER_DETECTION_LENGTH * self.world.camera.zoom), 1)

            pt2 = pt + self.avoid_obstacles()
            pygame.draw.line(self.world.screen, COLOR_RED, (int(pt.x), int(pt.y)), (int(pt2.x), int(pt2.y)))

            if self.wall_avoidance_ray:
                self.wall_avoidance_ray.draw()
                pt3 = self.wall_avoidance_ray.target
                pt4 = pt3 + self.avoid_walls()
                pygame.draw.line(self.world.screen, COLOR_RED, (int(pt3.x), int(pt3.y)), (int(pt4.x), int(pt4.y)))

    def kill(self):
        self.world.enemies.remove(self)
        blood = Entity(self.world, self.pos.x, self.pos.y, DEAD_IMAGE, (125, 115))
        blood.angle = self.angle
        self.world.misc.append(blood)
