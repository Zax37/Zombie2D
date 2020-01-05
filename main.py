import pygame
from world import World

pygame.init()
pygame.display.set_caption("Zombie2D")
screen = pygame.display.set_mode((800, 600))
clock = pygame.time.Clock()
pygame.font.init()
DEFAULT_FONT = pygame.font.SysFont('Consolas', 12)

world = World(screen, world_size=(1600, 1200), start_pos=(150, 100), debug_font=DEFAULT_FONT)

done = False
while not done:
    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            done = True
        elif event.type == pygame.KEYUP and event.key == pygame.K_F1:
            world.debug_mode = not world.debug_mode
            world.reset_camera()
        elif event.type == pygame.MOUSEBUTTONDOWN:
            if event.button == 4:
                world.camera.zoom = min(world.camera.zoom * 1.1, 2)
            if event.button == 5:
                world.camera.zoom = max(world.camera.zoom * 0.9, 0.1)

    world.update(clock.get_time())

    world.draw()
    pygame.display.flip()

    clock.tick(60)
