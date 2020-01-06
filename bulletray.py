import math
import pygame
import pygame.gfxdraw


class BulletRay:
    def __init__(self, world, source, angle):
        self.world = world
        self.source = source
        rads = angle * math.pi / 180.0
        self.length = sum(self.world.world_size)
        self.target = pygame.math.Vector2(math.floor(source.x + self.length * math.cos(rads)),
                                          math.floor(source.y + self.length * math.sin(rads)))
        self.opacity = 255

        self.limit_by_rect(pygame.Rect((0, 0), world.world_size))

        for obstacle in world.obstacles:
            intersection_point = self.get_intersection_point(obstacle)
            if intersection_point:
                self.target = intersection_point
                self.length = (self.target - self.source).length()

        close_enemy = None

        for enemy in world.enemies:
            intersection_point = self.get_intersection_point(enemy)
            if intersection_point:
                self.target = intersection_point
                self.length = (self.target - self.source).length()
                close_enemy = enemy

        if close_enemy is not None:
            close_enemy.kill()

    def get_intersection_point(self, target):
        if target.pos.distance_to(self.source) < target.size:
            return self.source

        if self.target.distance_to(self.source) <= 0:
            return None

        dir_vector = (self.target - self.source).normalize()
        to_target = (self.source - target.pos)

        if to_target.length() - target.size > self.length:
            return None

        lf = dir_vector.dot(to_target)
        s = target.size ** 2 - to_target.length_squared() + lf ** 2

        if s < 0:
            return None

        s = math.sqrt(s)

        if s + lf > 0:
            return None

        return self.source + dir_vector * -(s + lf)

    def update(self, time_elapsed):
        self.opacity -= time_elapsed * 0.5
        return self.opacity > 0

    def draw(self):
        progress = (1 - self.opacity / 255) * 0.05
        tgt = self.world.camera.offset(self.target)
        src = self.world.camera.offset(self.source) * (1 - progress) + tgt * progress
        pygame.gfxdraw.line(self.world.screen, int(src.x), int(src.y), int(tgt.x), int(tgt.y), (255, 255, 255, self.opacity))

    def limit_by_rect(self, rect):
        dir_vector = (self.target - self.source).normalize()

        if abs(dir_vector.x) <= 0.001:  # avoid extreme cases with vertical lines
            if self.source.x < rect[0] or self.source.x > rect[2]:
                return  # no intersection

            if dir_vector.y > 0:
                self.target.y = min(self.target.y, rect[3])
            else:
                self.target.y = max(self.target.y, rect[1])
            self.target.x = self.source.x
        else:
            slope = dir_vector.y / dir_vector.x
            intercept = self.source.y - slope * self.source.x

            if self.target.x < rect[0]:
                self.target.x = rect[0]
                self.target.y = slope * self.target.x + intercept
            elif self.target.x > rect[2]:
                self.target.x = rect[2]
                self.target.y = slope * self.target.x + intercept

            if self.target.y < rect[1]:
                self.target.y = rect[1]
                self.target.x = (self.target.y - intercept) / slope
            elif self.target.y > rect[3]:
                self.target.y = rect[3]
                self.target.x = (self.target.y - intercept) / slope

        self.length = (self.target - self.source).length()
