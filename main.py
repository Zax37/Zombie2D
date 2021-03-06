import pygame
from pygame import locals
from world import World

pygame.init()
pygame.display.set_caption("Zombie2D")
clock = pygame.time.Clock()
pygame.font.init()
DEFAULT_FONT = pygame.font.SysFont('Consolas', 24)
BIG_FONT = pygame.font.SysFont('Consolas', 32)

screen = pygame.display.set_mode((1920, 1080), pygame.locals.FULLSCREEN)
world_size = (screen.get_width() * 4, screen.get_height() * 4)
world = World(screen, world_size, start_pos=(270, 120), default_font=DEFAULT_FONT, big_font=BIG_FONT)

done = False
while not done:
    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            done = True
        elif event.type == pygame.KEYUP and event.key == pygame.K_F1:
            world.debug_mode = not world.debug_mode
            world.reset_camera()
        elif event.type == pygame.KEYUP and event.key == pygame.K_ESCAPE:
            done = True
        # elif event.type == pygame.MOUSEBUTTONDOWN:
        #     if event.button == 4:
        #         world.camera.zoom = min(world.camera.zoom * 1.1, 2)
        #     if event.button == 5:
        #         world.camera.zoom = max(world.camera.zoom * 0.9, 0.1)

    world.update(clock.get_time())

    world.draw()
    pygame.display.flip()

    clock.tick(60)
