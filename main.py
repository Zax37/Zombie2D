import pygame
import pygame.gfxdraw
import math
import copy
import random

pygame.init()
pygame.display.set_caption("Zombie2D")
screen = pygame.display.set_mode((800, 600))
black = (0, 0, 0)
grass = (10, 40, 10)
white = (255, 255, 255)
clock = pygame.time.Clock()

player_image = pygame.image.load('player.png')
zombie_image = pygame.image.load('zombie.png')

start_x = 150
start_y = 100
shoot_delay = 500

SPEED_CHANGE_CONST = .2
PLAYER_MAX_SPEED = 10
ZOMBIE_MAX_SPEED = 2
ROTATION_SPEED = .1

debug_mode = False

class Camera:
    def __init__(self, x, y):
        self.pos = pygame.math.Vector2(x, y)
        
    def offset(self, pos):
        ret = copy.copy(pos)
        ret -= self.pos
        ret += pygame.math.Vector2(screen.get_size()) / 2
        return ret
        
    def move_towards(self, target):
        self.pos *= 9
        self.pos += target
        self.pos /= 10

camera = Camera(start_x, start_y)
bullets = []
obstacles = []

class BulletRay:
    def __init__(self, source, angle):
        self.source = source
        rads = angle * math.pi / 180.0
        length = sum(screen.get_size())
        self.target = pygame.math.Vector2(math.floor(source.x + length * math.cos(rads)), math.floor(source.y + length * math.sin(rads)))
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
        
class Obstacle:
    def __init__(self, x, y, size):
        self.pos = pygame.math.Vector2(x, y)
        self.size = size
        
    def draw(self):
        pt = camera.offset(self.pos)
        pygame.draw.circle(screen, black, (int(pt.x), int(pt.y)), self.size)

class Entity:
    def __init__(self, x, y, image, pivot, max_speed, rotation_speed):
        self.pos = pygame.math.Vector2(x, y)
        self.image = image
        self.angle = 0
        self.velocity = pygame.math.Vector2(0, 0)
        self.heading = pygame.math.Vector2(0, 0)
        self.side = pygame.math.Vector2(0, 0)
        self.max_speed = max_speed
        self.rotation_speed = rotation_speed
        self.wander_target = pygame.math.Vector2(0, 0)
        
        rect = image.get_rect()
        self.offset = pygame.math.Vector2(pivot[0] - rect.center[0], pivot[1] - rect.center[1])
    
    def draw(self):
        rotated_image = pygame.transform.rotate(self.image, -self.angle)
        rotated_offset = self.offset.rotate(self.angle)
        rect = rotated_image.get_rect()
        rect.center = camera.offset(self.pos - rotated_offset)
        screen.blit(rotated_image, rect)
        if debug_mode:
            pt = camera.offset(self.pos)
            pygame.draw.circle(screen, white, (int(pt.x), int(pt.y)), 50)
            
    def move(self):
        speed = self.velocity.length()

        if speed > self.max_speed:
            self.velocity /= speed / self.max_speed

        if speed > 0.0000001:
            self.heading = self.velocity.normalize()
            self.side = pygame.math.Vector2(self.heading.y, -self.heading.x)
        
        self.pos += self.velocity
        
    def update_angle_from_heading(self):
        rads = math.atan2(-self.heading.y,self.heading.x) % (2 * math.pi)
        new_angle = -math.degrees(rads)
        shortest_angle = ((((new_angle - self.angle) % 360) + 540) % 360) - 180
        self.angle += (shortest_angle * self.rotation_speed) % 360
        
    def look_at(self, target):
        dx = target.x - self.pos.x
        dy = target.y - self.pos.y
        rads = math.atan2(-dy,dx) % (2 * math.pi)
        new_angle = -math.degrees(rads)
        shortest_angle = ((((new_angle - self.angle) % 360) + 540) % 360) - 180
        self.angle += (shortest_angle * self.rotation_speed) % 360

    def seek(self, target_pos):
        desired_velocity = (target_pos - self.pos).normalize() * self.max_speed
        return desired_velocity - self.velocity
        
    def flee(self, target_pos):
        desired_velocity = (self.pos - target_pos).normalize() * self.max_speed
        return desired_velocity - self.velocity
    
    def pursuit(self, target):
        to_target = target.pos - self.pos
        
        relative_heading = self.heading.dot(target.heading)
        
        if ((to_target.dot(self.heading) > 0) and (relative_heading < -0.95)):
            return self.seek(target.pos)
        
        look_ahead_time = to_target.length() / (self.max_speed + target.velocity.length())
        
        return self.seek(target.pos + target.velocity * look_ahead_time)
        
    def evade(self, target):
        to_target = target.pos - self.pos
        
        look_ahead_time = to_target.length() / (self.max_speed + target.velocity.length())
        
        return self.flee(target.pos + target.velocity * look_ahead_time)
        
    def wander(self):
        radius = 10
        distance = 20
        jitter = 2
        
        self.wander_target += pygame.math.Vector2(random.uniform(-1, 1) * jitter, random.uniform(-1, 1) * jitter)
        self.wander_target = self.wander_target.normalize() * radius
        
        return (self.wander_target + self.heading * distance)

class Player(Entity):
    def __init__(self, x, y):
        Entity.__init__(self, x, y, player_image, (75, 95), PLAYER_MAX_SPEED, ROTATION_SPEED)
        rect = player_image.get_rect()
        self.action_point = pygame.math.Vector2(280 - rect.center[0], 110 - rect.center[1])
        self.shoot_timeout = 0
        
    def shoot(self):
        action_point_rotated = self.action_point.rotate(self.angle)
        bullets.append(BulletRay(self.pos + action_point_rotated, self.angle))
        self.shoot_timeout = shoot_delay
        
    def update(self):    
        time_elapsed = clock.get_time()

        pressed = pygame.key.get_pressed()
        if pressed[pygame.K_w]: self.velocity.y -= SPEED_CHANGE_CONST * time_elapsed
        elif pressed[pygame.K_s]: self.velocity.y += SPEED_CHANGE_CONST * time_elapsed
        else: self.velocity.y *= 0.7
        
        if pressed[pygame.K_a]: self.velocity.x -= SPEED_CHANGE_CONST * time_elapsed
        elif pressed[pygame.K_d]: self.velocity.x += SPEED_CHANGE_CONST * time_elapsed
        else: self.velocity.x *= 0.7
        
        self.move()
        
        if self.shoot_timeout > 0:
            self.shoot_timeout -= time_elapsed
        elif pygame.mouse.get_pressed()[0]:
            self.shoot()

        mouse_pos = pygame.mouse.get_pos()
        center = self.pos + mouse_pos - pygame.math.Vector2(screen.get_size()) / 2
        
        self.look_at(center)
        camera.move_towards(center)
        
    def draw(self):
        Entity.draw(self)
        if debug_mode:
            action_point_rotated = self.action_point.rotate(self.angle)
            point = camera.offset(self.pos + action_point_rotated)
            pygame.draw.circle(screen, white, (int(point.x), int(point.y)), 3)

class Zombie(Entity):
    def __init__(self, x, y):
        Entity.__init__(self, x, y, zombie_image, (90, 125), ZOMBIE_MAX_SPEED, ROTATION_SPEED)
    
    def update(self):
        direction = self.pursuit(player)
        self.velocity += direction
        self.move()
        self.update_angle_from_heading()
        
    def draw(self):
        Entity.draw(self)
        if debug_mode:
            pygame.draw.circle(screen, white, (int(point.x), int(point.y)), 3)

player = Player(start_x, start_y)
enemies = list([Zombie((350*i)%1000, 500+math.floor(i/4)*300) for i in range(1, 2)])

done = False

obstacles.append( Obstacle(0, 0, 100) )

while not done:
    screen.fill(grass)
    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            done = True
        elif event.type == pygame.KEYUP and event.key == pygame.K_F1:
            debug_mode = not debug_mode
            
    player.update()    
    player.draw()
    
    for enemy in enemies:
        enemy.update()
        enemy.draw()
        
    bullets = [bullet for bullet in bullets if bullet.update()]
    
    for obstacle in obstacles:
        obstacle.draw()

    pygame.display.flip()
    clock.tick(60)