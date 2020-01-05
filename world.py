import pygame
from camera import Camera
from obstacle import Obstacle
from player import Player
from zombie import Zombie

COLOR_BACKGROUND = (10, 40, 10)
COLOR_WALL = (120, 30, 30)


class World:
    def __init__(self, screen, world_size, start_pos, debug_font):
        self.debug_mode = True
        self.debug_font = debug_font
        self.screen = screen
        self.world_size = world_size
        self.start_pos = start_pos
        self.camera = Camera(self)
        self.reset_camera()
        self.player = Player(self, start_pos[0], start_pos[1])
        self.enemies = [Zombie(self, 350, 600)]
        # list([Zombie(self, (350 * i) % 1000, 600 + math.floor(i / 4) * 300) for i in range(1, 12)])
        self.obstacles = [Obstacle(self, 0, 0, 100)]
        self.bullets = []
        self.misc = []

    def reset_camera(self):
        self.camera.pos = pygame.math.Vector2(self.world_size[0] / 2, self.world_size[1] / 2) if self.debug_mode \
            else pygame.math.Vector2(self.start_pos[0], self.start_pos[1])

    def update(self, time_elapsed):
        self.player.update(time_elapsed)
        for enemy in self.enemies:
            enemy.update(time_elapsed)
        self.bullets = [bullet for bullet in self.bullets if bullet.update(time_elapsed)]

    def draw(self):
        self.screen.fill(COLOR_BACKGROUND)
        wall_rect = (0, 0) + tuple([self.camera.zoom * x for x in self.world_size])
        pygame.draw.rect(self.screen, COLOR_WALL, self.camera.offset_rect(wall_rect), int(10 * self.camera.zoom))
        for entity in self.misc:
            entity.draw()
        for enemy in self.enemies:
            enemy.draw()
        self.player.draw()
        for obstacle in self.obstacles:
            obstacle.draw()
        for bullet in self.bullets:
            bullet.draw()
