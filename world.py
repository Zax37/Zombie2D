import pygame
import random
from camera import Camera
from obstacle import Obstacle
from player import Player
from zombie import Zombie

COLOR_BACKGROUND = (10, 40, 10)
COLOR_WALL = (120, 30, 30)
COLOR_HP = (255, 0, 0)


class World:
    def __init__(self, screen, world_size, start_pos, font):
        self.debug_mode = True
        self.font = font
        self.screen = screen
        self.world_size = world_size
        self.start_pos = start_pos
        self.camera = Camera(self)
        self.reset_camera()
        self.player = Player(self, start_pos[0], start_pos[1])
        self.enemies = []
        self.obstacles = []
        self.bullets = []
        self.misc = []
        self.wall_width = 8

        gen_grid_size = 512
        half_grid_size = gen_grid_size / 4
        gen_w = int(world_size[0] / gen_grid_size)
        gen_h = int(world_size[1] / gen_grid_size)

        spawn_probabilities = [(0.3, self.spawn_zombie), (0.5, self.spawn_obstacle)]
        for x in range(1, gen_w):
            for y in range(1, gen_h):
                for spawn in spawn_probabilities:
                    if random.uniform(0, 1) < spawn[0]:
                        spawn[1](x * gen_grid_size + random.uniform(-half_grid_size, half_grid_size),
                                 y * gen_grid_size + random.uniform(-half_grid_size, half_grid_size))

    def spawn_zombie(self, x, y):
        self.enemies.append(Zombie(self, x, y))

    def spawn_obstacle(self, x, y):
        self.obstacles.append(Obstacle(self, x, y, random.uniform(50, 120)))

    def reset_camera(self):
        if self.debug_mode:
            self.camera.pos = pygame.math.Vector2(self.world_size[0] / 2, self.world_size[1] / 2)
            self.camera.zoom = self.screen.get_width() / (self.world_size[0] + 150)
        elif self.player:
            self.camera.pos = pygame.math.Vector2(self.player.pos)

    def get_wall_inner_rect(self):
        return pygame.Rect((self.wall_width, self.wall_width),
                           tuple([x - self.wall_width for x in self.world_size]))

    def update(self, time_elapsed):
        if self.player:
            self.player.update(time_elapsed)
        for enemy in self.enemies:
            enemy.update(time_elapsed)
        self.bullets = [bullet for bullet in self.bullets if bullet.update(time_elapsed)]

    def draw(self):
        self.screen.fill(COLOR_BACKGROUND)
        wall_rect = (0, 0) + tuple([self.camera.zoom * x for x in self.world_size])
        pygame.draw.rect(self.screen, COLOR_WALL, self.camera.offset_rect(wall_rect),
                         1 + int(self.wall_width * 2 * self.camera.zoom))
        for entity in self.misc:
            entity.draw()
        for enemy in self.enemies:
            enemy.draw()
        if self.player:
            self.player.draw()
        for obstacle in self.obstacles:
            obstacle.draw()
        for bullet in self.bullets:
            bullet.draw()

        if self.player:
            player_hp = self.font.render(str(self.player.health), False, COLOR_HP)
            self.screen.blit(player_hp, (10, 10))
        else:
            dead = self.font.render('YOU DIED', False, COLOR_HP)
            self.screen.blit(dead, (self.screen.get_width() / 2 - dead.get_width() / 2,
                                    self.screen.get_height() / 2 - dead.get_height() / 2))
