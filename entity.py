import pygame
import math
import random

COLOR_WHITE = (255, 255, 255)


class Entity:
    def __init__(self, world, x, y, image, pivot, max_speed, rotation_speed):
        self.world = world
        self.pos = pygame.math.Vector2(x, y)
        self.image = image
        self.angle = 0
        self.velocity = pygame.math.Vector2(0, 0)
        self.heading = pygame.math.Vector2(0, 0)
        self.side = pygame.math.Vector2(0, 0)
        self.max_speed = max_speed
        self.rotation_speed = rotation_speed
        self.wander_target = pygame.math.Vector2(0, 0)

        rect = image.get_rect()
        self.offset = pygame.math.Vector2(pivot[0] - rect.center[0], pivot[1] - rect.center[1])

    def draw(self):
        rotated_image = pygame.transform.rotate(self.image, -self.angle)
        rotated_offset = self.offset.rotate(self.angle)
        rect = rotated_image.get_rect()
        rect.center = self.world.camera.offset(self.pos - rotated_offset)
        self.world.screen.blit(rotated_image, rect)
        if self.world.debug_mode:
            pt = self.world.camera.offset(self.pos)
            pygame.draw.circle(self.world.screen, COLOR_WHITE, (int(pt.x), int(pt.y)), 50)

    def move(self):
        speed = self.velocity.length()

        if speed > self.max_speed:
            self.velocity /= speed / self.max_speed

        if speed > 0.0000001:
            self.heading = self.velocity.normalize()
            self.side = pygame.math.Vector2(self.heading.y, -self.heading.x)

        self.pos += self.velocity

    def update_angle_from_heading(self):
        rads = math.atan2(-self.heading.y, self.heading.x) % (2 * math.pi)
        new_angle = -math.degrees(rads)
        shortest_angle = ((((new_angle - self.angle) % 360) + 540) % 360) - 180
        self.angle += (shortest_angle * self.rotation_speed) % 360

    def look_at(self, target):
        dx = target.x - self.pos.x
        dy = target.y - self.pos.y
        rads = math.atan2(-dy, dx) % (2 * math.pi)
        new_angle = -math.degrees(rads)
        shortest_angle = ((((new_angle - self.angle) % 360) + 540) % 360) - 180
        self.angle += (shortest_angle * self.rotation_speed) % 360

    def seek(self, target_pos):
        desired_velocity = (target_pos - self.pos).normalize() * self.max_speed
        return desired_velocity - self.velocity

    def flee(self, target_pos):
        desired_velocity = (self.pos - target_pos).normalize() * self.max_speed
        return desired_velocity - self.velocity

    def pursuit(self, target):
        to_target = target.pos - self.pos

        relative_heading = self.heading.dot(target.heading)

        if ((to_target.dot(self.heading) > 0) and (relative_heading < -0.95)):
            return self.seek(target.pos)

        look_ahead_time = to_target.length() / (self.max_speed + target.velocity.length())

        return self.seek(target.pos + target.velocity * look_ahead_time)

    def evade(self, target):
        to_target = target.pos - self.pos

        look_ahead_time = to_target.length() / (self.max_speed + target.velocity.length())

        return self.flee(target.pos + target.velocity * look_ahead_time)

    def wander(self):
        radius = 10
        distance = 20
        jitter = 2

        self.wander_target += pygame.math.Vector2(random.uniform(-1, 1) * jitter, random.uniform(-1, 1) * jitter)
        self.wander_target = self.wander_target.normalize() * radius

        return (self.wander_target + self.heading * distance)