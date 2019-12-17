import pygame


class Entity:
    def __init__(self, world, x, y, image, pivot):
        self.world = world
        self.pos = pygame.math.Vector2(x, y)
        self.image = image
        self.angle = 0

        rect = image.get_rect()
        self.offset = pygame.math.Vector2(pivot[0] - rect.center[0], pivot[1] - rect.center[1])

    def draw(self):
        rotated_image = pygame.transform.rotozoom(self.image, -self.angle, self.world.camera.zoom)
        rotated_offset = self.offset.rotate(self.angle)
        rect = rotated_image.get_rect()
        rect.center = self.world.camera.offset(self.pos - rotated_offset)
        self.world.screen.blit(rotated_image, rect)