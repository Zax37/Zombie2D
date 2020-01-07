import math


def angle_from_direction_vector(vector):
    rads = math.atan2(-vector.y, vector.x) % (2 * math.pi)
    return -math.degrees(rads)


def shortest_angle(angle_from, angle_to):
    return ((((angle_to - angle_from) % 360) + 540) % 360) - 180


def limit_vector(vector, max_length):
    if vector.length() > max_length:
        return vector.normalize() * max_length
    return vector
