import math
import pygame
import pygame.gfxdraw
from shapely.geometry import LineString


class BulletRay:
    def __init__(self, world, source, angle):
        self.world = world
        self.source = source
        rads = angle * math.pi / 180.0
        self.length = int(sum(self.world.screen.get_size()) / world.camera.zoom)
        self.target = pygame.math.Vector2(math.floor(source.x + self.length * math.cos(rads)),
                                          math.floor(source.y + self.length * math.sin(rads)))
        self.opacity = 255
        self.line = LineString([(self.source.x, self.source.y), (self.target.x, self.target.y)])

        for obstacle in world.obstacles:
            self.limit_by_intersections(obstacle)

        close_enemy = False

        for enemy in world.enemies:
            if enemy.is_dead():
                continue

            intersections = self.limit_by_intersections(enemy)
            if intersections:
                close_enemy = enemy

        if close_enemy:
            close_enemy.kill()

    def limit_by_intersections(self, target):
        intersection = target.get_boundary().intersection(self.line)
        if intersection.geoms:
            for geom in intersection.geoms:
                for coords in geom.coords:
                    target = pygame.math.Vector2(coords[0], coords[1])
                    from_source = target - self.source
                    length = from_source.length()
                    if length < self.length:
                        self.length = length
                        self.target = target
                        self.line = LineString([(self.source.x, self.source.y), (self.target.x, self.target.y)])

        return len(list(intersection.geoms)) > 0

    def update(self, time_elapsed):
        self.opacity -= time_elapsed * 0.5
        return self.opacity > 0

    def draw(self):
        progress = (1 - self.opacity / 255) * 0.05
        tgt = self.world.camera.offset(self.target)
        src = self.world.camera.offset(self.source) * (1 - progress) + tgt * progress
        pygame.gfxdraw.line(self.world.screen, int(src.x), int(src.y), int(tgt.x), int(tgt.y), (255, 255, 255, self.opacity))