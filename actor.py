import math
import pygame
import random
from entity import Entity

COLOR_BLACK = (0, 0, 0)
COLOR_WHITE = (255, 255, 255)
BODY_RADIUS = 70
MIN_DETECTION_BOX_LENGTH = 100


class Actor(Entity):
    def __init__(self, world, x, y, image, pivot, max_speed, rotation_speed):
        Entity.__init__(self, world, x, y, image, pivot)
        self.max_speed = max_speed
        self.rotation_speed = rotation_speed
        self.size = BODY_RADIUS

        theta = random.uniform(0, 360)

        self.wander_radius = 1.2
        self.wander_distance = 2.0
        self.wander_jitter = 40.0
        self.wander_target = pygame.math.Vector2(self.wander_radius * math.cos(theta),
                                                 self.wander_radius * math.sin(theta))

    def get_detection_box_length(self):
        return MIN_DETECTION_BOX_LENGTH * (1 + self.velocity.length() / self.max_speed) + BODY_RADIUS

    def tag_close_entities(self):
        for entity in (self.world.obstacles + self.world.enemies):
            entity.tagged = False
            to = self.pos - entity.pos
            detection_length = self.get_detection_box_length() + entity.size
            if entity != self and to.length_squared() < detection_length ** 2:
                entity.tag()

    def draw(self):
        Entity.draw(self)
        if self.world.debug_mode:
            pt = self.world.camera.offset(self.pos)
            pygame.draw.circle(self.world.screen, COLOR_WHITE, (int(pt.x), int(pt.y)),
                               int(BODY_RADIUS * self.world.camera.zoom))
            detection_length = self.get_detection_box_length()
            pygame.draw.circle(self.world.screen, COLOR_BLACK, (int(pt.x), int(pt.y)),
                               int(detection_length * self.world.camera.zoom), 1)
            pt2 = pt + self.heading * detection_length * self.world.camera.zoom
            pygame.draw.line(self.world.screen, COLOR_BLACK, (int(pt.x), int(pt.y)),
                             (int(pt2.x), int(pt2.y)))

    def move(self):
        speed = self.velocity.length()

        if speed > self.max_speed:
            self.velocity /= speed / self.max_speed

        if speed > 0.0000001:
            self.heading = self.velocity.normalize()
            self.side = pygame.math.Vector2(self.heading.y, -self.heading.x)

        self.pos += self.velocity

    def update_angle_from_heading(self):
        rads = math.atan2(-self.heading.y, self.heading.x) % (2 * math.pi)
        new_angle = -math.degrees(rads)
        shortest_angle = ((((new_angle - self.angle) % 360) + 540) % 360) - 180
        self.angle += (shortest_angle * self.rotation_speed) % 360

    def look_at(self, target):
        dx = target.x - self.pos.x
        dy = target.y - self.pos.y
        rads = math.atan2(-dy, dx) % (2 * math.pi)
        new_angle = -math.degrees(rads)
        shortest_angle = ((((new_angle - self.angle) % 360) + 540) % 360) - 180
        self.angle += (shortest_angle * self.rotation_speed) % 360

    def seek(self, target_pos):
        desired_velocity = (target_pos - self.pos).normalize() * self.max_speed
        return desired_velocity - self.velocity

    def flee(self, target_pos):
        desired_velocity = (self.pos - target_pos).normalize() * self.max_speed
        return desired_velocity - self.velocity

    def arrive(self, target_pos):
        to_target = target_pos - self.pos
        dist = to_target.length()

        if dist > 0:
            deceleration_tweaker = 0.3
            speed = min(dist / deceleration_tweaker, self.max_speed)
            desired_velocity = to_target * speed / dist
            return desired_velocity - self.velocity

        return pygame.math.Vector2(0, 0)

    def pursuit(self, target):
        to_target = target.pos - self.pos

        relative_heading = self.heading.dot(target.heading)

        if (to_target.dot(self.heading) > 0) and (relative_heading < -0.95):
            return self.seek(target.pos)

        look_ahead_time = to_target.length() / (self.max_speed + target.velocity.length())

        return self.seek(target.pos + target.velocity * look_ahead_time)

    def evade(self, target):
        to_target = target.pos - self.pos

        look_ahead_time = to_target.length() / (self.max_speed + target.velocity.length())

        return self.flee(target.pos + target.velocity * look_ahead_time)

    def wander(self):
        self.wander_target += pygame.math.Vector2(random.uniform(-1, 1) * self.wander_jitter,
                                                  random.uniform(-1, 1) * self.wander_jitter)
        self.wander_target = self.wander_target.normalize() * self.wander_radius
        return self.wander_target + self.heading * self.wander_distance

    def avoid_obstacles(self):
        self.tag_close_entities()

        closest_intersecting_obstacle = None
        dist_to_closest_ip = float('inf')
        local_pos_of_closest_obstacle = None

        for entity in (self.world.obstacles + self.world.enemies):
            if entity.tagged:
                local_pos = self.world_point_to_local(entity.pos)
                if local_pos.x >= 0:
                    expanded_radius = entity.size + self.size
                    if abs(local_pos.y) < expanded_radius:
                        sqrt_part = math.sqrt(expanded_radius ** 2 - local_pos.y ** 2)
                        ip = local_pos.x - sqrt_part

                        if ip <= 0:
                            ip = local_pos.x + sqrt_part

                        if ip < dist_to_closest_ip:
                            dist_to_closest_ip = ip
                            closest_intersecting_obstacle = entity
                            local_pos_of_closest_obstacle = local_pos

        steering_force = pygame.math.Vector2(0, 0)
        braking_weight = 0.2

        if closest_intersecting_obstacle:
            detection_length = self.get_detection_box_length()
            multiplier = 1 + (detection_length - local_pos_of_closest_obstacle.x) / detection_length
            steering_force.x = (closest_intersecting_obstacle.size - local_pos_of_closest_obstacle.x) * braking_weight
            steering_force.y = (closest_intersecting_obstacle.size - local_pos_of_closest_obstacle.y) * multiplier

        return self.local_vector_to_world(steering_force)
