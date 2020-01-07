import pygame


class SteeringForce:
    def __init__(self, max_force):
        self.force = pygame.math.Vector2(0, 0)
        self.magnitude = 0
        self.max_force = max_force

    def accumulate(self, force):
        magnitude_remaining = self.max_force - self.magnitude
        if magnitude_remaining <= 0:
            return False

        magnitude_to_add = force.length()
        if magnitude_to_add >= magnitude_remaining:
            self.force += force.normalize() * magnitude_remaining
            self.magnitude = self.max_force
            return False
        else:
            self.force += force
            self.magnitude += magnitude_to_add

        return True
