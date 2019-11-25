import pygame
import pygame.gfxdraw
import math
import copy

pygame.init()
pygame.display.set_caption("Zombie2D")
screen = pygame.display.set_mode((800, 600))
grass = (10, 40, 10)
white = (255, 255, 255)
clock = pygame.time.Clock()

player_image = pygame.image.load('player.png')
zombie_image = pygame.image.load('zombie.png')

start_x = 350
start_y = 150
shoot_delay = 500

debug_mode = False

class Camera:
    def __init__(self, x, y):
        self.x = x
        self.y = y
        
    def offset(self, pos):
        ret = copy.copy(pos)
        ret.x -= self.x - screen.get_width() / 2
        ret.y -= self.y - screen.get_height() / 2
        return ret
        
    def move_towards(self, x, y):
        self.x = (self.x * 9 + x) / 10
        self.y = (self.y * 9 + y) / 10

camera = Camera(start_x, start_y)
bullets = []

class BulletRay:
    def __init__(self, x, y, angle):
        self.source = pygame.math.Vector2(x, y)
        rads = angle * math.pi / 180.0
        length = sum(screen.get_size())
        self.target = pygame.math.Vector2(math.floor(x + length * math.cos(rads)), math.floor(y + length * math.sin(rads)))
        self.opacity = 255

    def update(self):
        self.opacity -= clock.get_time() * 0.5
        if self.opacity > 0:
            progress = (1 - self.opacity / 255) * 0.05
            tgt = camera.offset(self.target)
            src = camera.offset(self.source) * (1 - progress) + tgt * progress
            pygame.gfxdraw.line(screen, int(src.x), int(src.y), int(tgt.x), int(tgt.y), (255, 255, 255, self.opacity))
            return True
        return False

class Entity:
    def __init__(self, x, y, image, pivot):
        self.x = x
        self.y = y
        self.image = image
        self.angle = 0
        
        rect = image.get_rect()
        self.offset = pygame.math.Vector2(pivot[0] - rect.center[0], pivot[1] - rect.center[1])
    
    def draw(self):
        rotated_image = pygame.transform.rotate(self.image, -self.angle)
        rotated_offset = self.offset.rotate(self.angle)
        rect = rotated_image.get_rect()
        rect.center = -rotated_offset
        rect.x += self.x
        rect.y += self.y
        rect = camera.offset(rect)
        screen.blit(rotated_image, rect)
        if debug_mode:
            pt = camera.offset(pygame.math.Vector2(self.x, self.y))
            pygame.draw.circle(screen, white, (int(pt.x), int(pt.y)), 50)
        
    def look_at(self, x, y):
        dx = x - self.x
        dy = y - self.y
        rads = math.atan2(-dy,dx)
        rads %= 2 * math.pi
        self.angle = -math.degrees(rads)
        

class Player(Entity):
    def __init__(self, x, y):
        Entity.__init__(self, x, y, player_image, (75, 95))
        rect = player_image.get_rect()
        self.action_point = pygame.math.Vector2(280 - rect.center[0], 110 - rect.center[1])
        self.shoot_timeout = 0
        
    def shoot(self):
        rotated_offset = self.action_point.rotate(self.angle)
        bullets.append(BulletRay(self.x + rotated_offset.x, self.y + rotated_offset.y, self.angle))
        self.shoot_timeout = shoot_delay
        
    def draw(self):
        Entity.draw(self)
        if debug_mode:
            action_point_rotated = self.action_point.rotate(self.angle)
            point = camera.offset(action_point_rotated + (self.x, self.y))
            pygame.draw.circle(screen, white, (int(point.x), int(point.y)), 3)

class Zombie(Entity):
    def __init__(self, x, y):
        Entity.__init__(self, x, y, zombie_image, (90, 125))
    
player = Player(start_x, start_y)
enemies = list([Zombie((300*i)%1000, 300+math.floor(i/4)*300) for i in range(1, 12)])

done = False

PLAYER_SPEED = 5

while not done:
    screen.fill(grass)
    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            done = True
        elif event.type == pygame.KEYUP and event.key == pygame.K_F1:
            debug_mode = not debug_mode
            
    pressed = pygame.key.get_pressed()
    if pressed[pygame.K_w]: player.y -= PLAYER_SPEED
    if pressed[pygame.K_s]: player.y += PLAYER_SPEED
    if pressed[pygame.K_a]: player.x -= PLAYER_SPEED
    if pressed[pygame.K_d]: player.x += PLAYER_SPEED
    
    if player.shoot_timeout > 0:
        player.shoot_timeout -= clock.get_time()
    elif pygame.mouse.get_pressed()[0]:
        player.shoot()

    (mouse_x, mouse_y) = pygame.mouse.get_pos()
    
    center_x = player.x + mouse_x - screen.get_width() / 2
    center_y = player.y + mouse_y - screen.get_height() / 2
    
    player.look_at(center_x, center_y)
    camera.move_towards(center_x, center_y)
    
    player.draw()
    
    for enemy in enemies:
        enemy.look_at(player.x, player.y)
        enemy.draw()
        
    bullets = [bullet for bullet in bullets if bullet.update()]

    pygame.display.flip()
    clock.tick(60)