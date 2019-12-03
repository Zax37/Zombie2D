import pygame
from world import World

pygame.init()
pygame.display.set_caption("Zombie2D")
screen = pygame.display.set_mode((800, 600))
clock = pygame.time.Clock()
pygame.font.init()
DEFAULT_FONT = pygame.font.SysFont('Consolas', 12)

world = World(screen, start_x=150, start_y=100, debug_font=DEFAULT_FONT)

done = False

while not done:
    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            done = True
        elif event.type == pygame.KEYUP and event.key == pygame.K_F1:
            world.debug_mode = not world.debug_mode

    world.update(clock.get_time())
    world.draw()
    pygame.display.flip()
    clock.tick(60)