import math
import pygame
import pygame.gfxdraw


class BulletRay:
    def __init__(self, world, source, angle):
        self.world = world
        self.source = source
        rads = angle * math.pi / 180.0
        self.length = int(sum(self.world.screen.get_size()) / world.camera.zoom)
        self.target = pygame.math.Vector2(math.floor(source.x + self.length * math.cos(rads)),
                                          math.floor(source.y + self.length * math.sin(rads)))
        self.opacity = 255

        for obstacle in world.obstacles:
            intersection_point = self.get_intersection_point(obstacle)
            if intersection_point:
                self.target = intersection_point
                self.length = (self.target - self.source).length()

        close_enemy = None

        for enemy in world.enemies:
            if enemy.is_dead():
                continue

            intersection_point = self.get_intersection_point(enemy)
            if intersection_point:
                self.target = intersection_point
                self.length = (self.target - self.source).length()
                close_enemy = enemy

        if close_enemy is not None:
            close_enemy.kill()

    def get_intersection_point(self, target):
        dir_vector = (self.target - self.source).normalize()
        dist = (self.source - target.pos)

        if dist.length() > self.length:
            return None

        lf = dir_vector.dot(dist)
        s = target.size ** 2 - dist.length_squared() + lf ** 2

        if s < 0:
            return None

        s = math.sqrt(s)

        return self.source + dir_vector * -(s + lf)

    def update(self, time_elapsed):
        self.opacity -= time_elapsed * 0.5
        return self.opacity > 0

    def draw(self):
        progress = (1 - self.opacity / 255) * 0.05
        tgt = self.world.camera.offset(self.target)
        src = self.world.camera.offset(self.source) * (1 - progress) + tgt * progress
        pygame.gfxdraw.line(self.world.screen, int(src.x), int(src.y), int(tgt.x), int(tgt.y), (255, 255, 255, self.opacity))