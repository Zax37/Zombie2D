import pygame


class Entity:
    def __init__(self, world, x, y, image=None, pivot=None):
        self.world = world
        self.pos = pygame.math.Vector2(x, y)
        self.angle = 0
        self.tagged = False
        self.heading = pygame.math.Vector2(1, 0)
        self.side = pygame.math.Vector2(0, -1)
        self.velocity = pygame.math.Vector2(0, 0)

        if image:
            self.image = image
            rect = image.get_rect()
            self.offset = pygame.math.Vector2(pivot[0] - rect.center[0], pivot[1] - rect.center[1])

    def draw(self):
        rotated_image = pygame.transform.rotozoom(self.image, -self.angle, self.world.camera.zoom)
        rotated_offset = self.offset.rotate(self.angle)
        rect = rotated_image.get_rect()
        rect.center = self.world.camera.offset(self.pos - rotated_offset)
        self.world.screen.blit(rotated_image, rect)

    def world_point_to_local(self, pos):
        t_x = -self.pos.dot(self.heading)
        t_y = -self.pos.dot(self.side)

        x = self.heading.x * pos.x + self.heading.y * pos.y + t_x
        y = self.side.x * pos.x + self.side.y * pos.y + t_y
        return pygame.math.Vector2(x, y)

    def local_vector_to_world(self, pos):
        x = self.heading.x * pos.x + self.side.x * pos.y
        y = self.heading.y * pos.x + self.side.y * pos.y
        return pygame.math.Vector2(x, y)
