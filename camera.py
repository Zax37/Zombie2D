import pygame


class Camera:
    def __init__(self, world, x=0, y=0):
        self.world = world
        self.pos = pygame.math.Vector2(x, y)
        self.zoom = 0.4
        self.screen_center = pygame.math.Vector2(self.world.screen.get_size()) / 2

    def offset(self, pos):
        return (pos - self.pos) * self.zoom + self.screen_center

    def offset_rect(self, rect):
        ret = [r for r in rect]
        ret[0] = (ret[0] - self.pos[0]) * self.zoom + self.screen_center[0]
        ret[1] = (ret[1] - self.pos[1]) * self.zoom + self.screen_center[1]
        return pygame.Rect(ret)

    def move_towards(self, target):
        self.pos *= 9
        self.pos += target
        self.pos /= 10
