import pygame
from bulletray import BulletRay
from entity import Entity

PLAYER_IMAGE = pygame.image.load('player.png')
PLAYER_MAX_SPEED = 10
SPEED_CHANGE_CONST = .2
ROTATION_SPEED = .1
COLOR_WHITE = (255, 255, 255)
SHOOT_DELAY = 500


class Player(Entity):
    def __init__(self, world, x, y):
        Entity.__init__(self, world, x, y, PLAYER_IMAGE, (75, 95), PLAYER_MAX_SPEED, ROTATION_SPEED)
        rect = PLAYER_IMAGE.get_rect()
        self.action_point = pygame.math.Vector2(280 - rect.center[0], 110 - rect.center[1])
        self.shoot_timeout = 0
        self.health = 100

    def shoot(self):
        action_point_rotated = self.action_point.rotate(self.angle)
        self.world.bullets.append(BulletRay(self.world, self.pos + action_point_rotated, self.angle))
        self.shoot_timeout = SHOOT_DELAY

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
        center = self.pos + mouse_pos - pygame.math.Vector2(self.world.screen.get_size()) / 2

        self.look_at(center)
        self.world.camera.move_towards(center)

    def draw(self):
        Entity.draw(self)
        if self.world.debug_mode:
            action_point_rotated = self.action_point.rotate(self.angle)
            point = self.world.camera.offset(self.pos + action_point_rotated)
            pygame.draw.circle(self.world.screen, COLOR_WHITE, (int(point.x), int(point.y)), 3)