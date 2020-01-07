import pygame
from actor import Actor
from entity import Entity
from ray import Ray

PLAYER_IMAGE = pygame.image.load('player.png')
DEAD_IMAGE = pygame.image.load('blood.png')
PLAYER_MAX_SPEED = 7
SPEED_CHANGE_CONST = .2
ROTATION_SPEED = 40
COLOR_RED = (255, 0, 0)
COLOR_WHITE = (255, 255, 255)
SHOOT_DELAY = 500


class Player(Actor):
    def __init__(self, world, x, y):
        Actor.__init__(self, world, x, y, PLAYER_IMAGE, (75, 95), PLAYER_MAX_SPEED, ROTATION_SPEED)
        rect = PLAYER_IMAGE.get_rect()
        self.action_point = pygame.math.Vector2(280 - rect.center[0], 110 - rect.center[1])
        self.shoot_timeout = 0
        self.health = 100

    def shoot(self):
        action_point_rotated = self.action_point.rotate(self.angle)
        bullet = Ray(self.world, self.pos + action_point_rotated, angle=self.angle)
        bullet.shoot_to_kill()
        self.world.bullets.append(bullet)
        self.shoot_timeout = SHOOT_DELAY

    def hurt(self):
        self.health -= 1
        if self.health <= 0:
            self.world.player = None
            blood = Entity(self.world, self.pos.x, self.pos.y, DEAD_IMAGE, (125, 115))
            blood.angle = self.angle
            self.world.misc.append(blood)

    def update(self, time_elapsed):
        pressed = pygame.key.get_pressed()
        if pressed[pygame.K_w]:
            self.velocity.y -= SPEED_CHANGE_CONST * time_elapsed
        elif pressed[pygame.K_s]:
            self.velocity.y += SPEED_CHANGE_CONST * time_elapsed
        else:
            self.velocity.y *= 0.7

        if pressed[pygame.K_a]:
            self.velocity.x -= SPEED_CHANGE_CONST * time_elapsed
        elif pressed[pygame.K_d]:
            self.velocity.x += SPEED_CHANGE_CONST * time_elapsed
        else:
            self.velocity.x *= 0.7

        self.move()

        if self.shoot_timeout > 0:
            self.shoot_timeout -= time_elapsed
        elif pygame.mouse.get_pressed()[0]:
            self.shoot()

        mouse_pos = pygame.mouse.get_pos()
        center = self.pos + mouse_pos - self.world.camera.offset(self.pos)

        self.look_at(center)

        # if not self.world.debug_mode:
        #     self.world.camera.move_towards(center)

    def draw(self):
        Actor.draw(self)
        if self.world.debug_mode:
            action_point_rotated = self.action_point.rotate(self.angle)
            point = self.world.camera.offset(self.pos + action_point_rotated)
            pygame.draw.circle(self.world.screen, COLOR_WHITE, (int(point.x), int(point.y)), 3)
            if self.was_tagged:
                pt = self.world.camera.offset(self.pos)
                pygame.draw.circle(self.world.screen, COLOR_RED, (int(pt.x), int(pt.y)),
                                   int(self.size * self.world.camera.zoom))
                self.was_tagged = False
