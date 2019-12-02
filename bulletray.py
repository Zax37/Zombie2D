import pygame
import math
import pygame.gfxdraw

class BulletRay:
    def __init__(self, world, source, angle):
        self.world = world
        self.source = source
        rads = angle * math.pi / 180.0
        length = sum(self.world.screen.get_size())
        self.target = pygame.math.Vector2(math.floor(source.x + length * math.cos(rads)), math.floor(source.y + length * math.sin(rads)))
        self.opacity = 255

    def update(self, time_elapsed):
        self.opacity -= time_elapsed * 0.5
        return self.opacity > 0

    def draw(self):
        progress = (1 - self.opacity / 255) * 0.05
        tgt = self.world.camera.offset(self.target)
        src = self.world.camera.offset(self.source) * (1 - progress) + tgt * progress
        pygame.gfxdraw.line(self.world.screen, int(src.x), int(src.y), int(tgt.x), int(tgt.y), (255, 255, 255, self.opacity))