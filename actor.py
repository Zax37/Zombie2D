import math
import pygame
import random
import util
from entity import Entity
from ray import Ray

COLOR_BLACK = (0, 0, 0)
COLOR_WHITE = (255, 255, 255)
BODY_RADIUS = 70
MIN_DETECTION_BOX_LENGTH = 150


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
        self.wall_avoidance_ray = None

    def get_detection_box_length(self):
        return MIN_DETECTION_BOX_LENGTH * (1 + self.velocity.length() / self.max_speed) + self.size

    def tag_close_entities(self, entities):
        num = 0
        for entity in entities:
            entity.tagged = False
            to = self.pos - entity.pos
            detection_length = self.get_detection_box_length() + entity.size
            if entity != self and to.length_squared() < detection_length ** 2:
                entity.tag()
                num += 1
        return num

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

        if speed > 0:
            self.heading = self.velocity.normalize()
            self.side = pygame.math.Vector2(self.heading.y, -self.heading.x)

            if speed > self.max_speed:
                self.velocity = self.heading * self.max_speed

        new_pos = self.pos + self.velocity

        entities = self.world.enemies + self.world.obstacles
        if self.world.player:
            entities.append(self.world.player)
        self.tag_close_entities(entities)

        for entity in entities:
            if entity.tagged:
                from_entity = (new_pos - entity.pos)
                distance = from_entity.length() - self.size - entity.size
                if distance <= 0:
                    new_pos -= from_entity.normalize() * distance

        inner_wall_rect = self.world.get_wall_inner_rect()
        if new_pos.x - self.size < inner_wall_rect[0]:
            new_pos.x = inner_wall_rect[0] + self.size
        if new_pos.y - self.size < inner_wall_rect[1]:
            new_pos.y = inner_wall_rect[1] + self.size
        if new_pos.x + self.size > inner_wall_rect[2]:
            new_pos.x = inner_wall_rect[2] - self.size
        if new_pos.y + self.size > inner_wall_rect[3]:
            new_pos.y = inner_wall_rect[3] - self.size

        self.pos = new_pos

    # def angle_limit(self):
    #     new_heading = self.velocity.normalize()
    #     old_angle = util.angle_from_direction_vector(self.heading)
    #     new_angle = util.angle_from_direction_vector(new_heading)
    #     angle_diff = util.shortest_angle(old_angle, new_angle)
    #
    #     if abs(angle_diff) > self.rotation_speed:
    #         new_heading = self.heading.rotate(math.copysign(self.rotation_speed, angle_diff))
    #         self.velocity = new_heading * speed

    def update_angle_from_heading(self):
        angle = util.angle_from_direction_vector(self.heading)
        self.angle += util.shortest_angle(self.angle, angle) * self.rotation_speed / 360

    def look_at(self, target):
        angle = util.angle_from_direction_vector(target - self.pos)
        self.angle += util.shortest_angle(self.angle, angle) * self.rotation_speed / 360

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
        obstacles = self.world.obstacles
        self.tag_close_entities(obstacles)

        closest_intersecting_obstacle = None
        dist_to_closest_ip = float('inf')
        local_pos_of_closest_obstacle = None

        for entity in obstacles:
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

            detection_length = self.get_detection_box_length() - self.size
            multiplier = (detection_length - local_pos_of_closest_obstacle.x) / detection_length
            steering_force.x = (closest_intersecting_obstacle.size - local_pos_of_closest_obstacle.x) * braking_weight
            steering_force.y = (closest_intersecting_obstacle.size - local_pos_of_closest_obstacle.y) * multiplier

            return self.local_vector_to_world(steering_force)

        return steering_force

    def avoid_walls(self):
        detection_length = self.get_detection_box_length() + self.world.wall_width
        detection_vector = self.heading * detection_length
        ray = Ray(self.world, self.pos, target=self.pos + detection_vector)

        irx = ray.target.x
        iry = ray.target.y

        avoid_direction = pygame.math.Vector2(0, 0)
        penetration_depth = 0

        ray.limit_to_play_area()
        if ray.target.x == irx and ray.target.y == iry:  # no wall in range
            self.wall_avoidance_ray = None
            return avoid_direction

        self.wall_avoidance_ray = ray
        wall_inner_rect = self.world.get_wall_inner_rect()

        if ray.target.x == wall_inner_rect[0]:
            avoid_direction.x = 1
            penetration_depth = -irx
        elif ray.target.x == wall_inner_rect[2]:
            avoid_direction.x = -1
            penetration_depth = irx - ray.target.x
        elif ray.target.y == wall_inner_rect[1]:
            avoid_direction.y = 1
            penetration_depth = -iry
        elif ray.target.y == wall_inner_rect[3]:
            avoid_direction.y = -1
            penetration_depth = iry - ray.target.y

        return avoid_direction * penetration_depth

    def hide(self, hunter):
        distance_to_closest = float('inf')
        best_hiding_spot = None

        for obstacle in self.world.obstacles:
            hiding_spot = self.get_hiding_spot(obstacle.pos, obstacle.size, hunter.pos)
            dist = (self.pos - hiding_spot).length()

            if dist < distance_to_closest:
                distance_to_closest = dist
                best_hiding_spot = hiding_spot

        if best_hiding_spot:
            return self.arrive(best_hiding_spot)

        return self.evade(hunter)

    def get_hiding_spot(self, obstacle_pos, obstacle_radius, hunter_pos):
        distance_from_boundary = 30
        distance_away = self.size + obstacle_radius + distance_from_boundary
        to_ob = (obstacle_pos - hunter_pos).normalize()

        return (to_ob * distance_away) + obstacle_pos

    def separation(self, entities):
        force = pygame.math.Vector2(0, 0)

        for entity in entities:
            if entity.tagged:
                to_entity = self.pos - entity.pos
                distance = to_entity.length()
                force += to_entity.normalize() / distance

        return force

    def alignment(self, entities):
        average_heading = pygame.math.Vector2(0, 0)
        count = 0

        for entity in entities:
            if entity.tagged:
                average_heading += entity.heading
                count += 1

        if count > 0:
            average_heading /= count
            average_heading -= self.heading

        return average_heading

    def cohesion(self, entities):
        center_of_mass = pygame.math.Vector2(0, 0)
        count = 0

        for entity in entities:
            if entity.tagged:
                center_of_mass += entity.pos
                count += 1

        if count > 0:
            center_of_mass /= count
            return self.seek(center_of_mass)

        return pygame.math.Vector2(0, 0)

