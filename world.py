import math
from camera import Camera
from obstacle import Obstacle
from player import Player
from zombie import Zombie

COLOR_BACKGROUND = (10, 40, 10)

class World:
    def __init__(self, screen, start_x, start_y, debug_font):
        self.debug_font = debug_font
        self.screen = screen
        self.camera = Camera(self, start_x, start_y)
        self.player = Player(self, start_x, start_y)
        self.enemies = list([Zombie(self, (350 * i) % 1000, 600 + math.floor(i / 4) * 300) for i in range(1, 12)])
        self.obstacles = [Obstacle(self, 0, 0, 100)]
        self.bullets = []
        self.misc = []
        self.debug_mode = False
        self.step_by_step = False

    def update(self, time_elapsed):
        self.player.update(time_elapsed)
        for enemy in self.enemies:
            enemy.update(time_elapsed)
        self.bullets = [bullet for bullet in self.bullets if bullet.update(time_elapsed)]

    def draw(self):
        self.screen.fill(COLOR_BACKGROUND)
        for entity in self.misc:
            entity.draw()
        for enemy in self.enemies:
            enemy.draw()
        self.player.draw()
        for obstacle in self.obstacles:
            obstacle.draw()
        for bullet in self.bullets:
            bullet.draw()
