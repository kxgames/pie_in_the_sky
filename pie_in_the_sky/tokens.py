#!/usr/bin/env python

import kxg
from vecrec import Vector

class Player(kxg.Token):

    def __init__(self):
        super().__init__()
        from getpass import getuser
        self.name = getuser()


class Cannon(kxg.Token):

    def __init__(self, player):
        self.player = player
        self.init_bullet_position = 0
        self.init_bullet_velocity = Vector.null()

    def fire_bullet(self):
        return Bullet(
                self, self.init_bullet_position, self.init_bullet_velocity)


class FieldObject(kxg.Token):
    """
    A base class for targets, bullets, obstacles, and other objects that are in the field of play. Instances of this base class can be used if special methods are not necessary for a type of object. This class defines default functionality for motion, collisions, and updating.
    """

    def __init__(self, position, velocity, mass=1, collision_distance=20):
        super().__init__()

        self.mass = float(mass)
        self.position = position
        self.velocity = velocity
        self.acceleration = Vector.null()
        self.collision_distance = float(collision_distance)
        self.collision_distance_squared = collision_distance**2

        self.next_position = Vector.null()
        self.next_velocity = Vector.null()
        self.next_acceleration = Vector.null()

    def __extend__(self):
        from . import gui
        return {gui.GuiActor: gui.FieldObjectExtension}

    def can_collide_with(self, object):
        distance_squared = self.calculate_distance_squared(object)
        return distance_squared <= self.collision_distance_squared

    def calculate_distance_squared(self, object):
        delta = self.position - object.position
        return delta.magnitude_squared

    def add_next_acceleration(self, acceleration):
        self.next_acceleration += acceleration

    def calculate_motion(self, dt):
        p = self.position
        v = self.velocity
        a = self.next_acceleration

        dv = a * dt
        dp = (v + dv) * dt

        self.next_position = p + dp
        self.next_velocity = v + dv

    def move(self):
        self.position = self.next_position
        self.velocity = self.next_velocity
        self.acceleration = self.next_acceleration
        
        self.next_position = Vector.null()
        self.next_velocity = Vector.null()
        self.next_acceleration = Vector.null()


class Bullet(FieldObject):

    def __init__(self, cannon, position, velocity):
        super().__init__(self, position, velocity)
        self.cannon = cannon
        
    def __extend__(self):
        from . import gui
        return {gui.GuiActor: gui.BulletExtension}

    @property
    def player(self):
        return self.cannon.player


class Target(FieldObject):

    def __init__(self, position, velocity):
        super().__init__(position, velocity)
        
    def __extend__(self):
        from . import gui
        return {gui.GuiActor: gui.TargetExtension}

