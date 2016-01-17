#!/usr/bin/env python

import kxg
from vecrec import Vector

class Player(kxg.Token):

    def __init__(self):
        super().__init__()
        from getpass import getuser
        self.name = getuser()
        self.cannons = []

        self.max_arsenal = 6
        self.arsenal = self.max_arsenal
        self._arsenal = float(self.max_arsenal)
        self.arsenal_recharge_rate = 1/2

    @kxg.read_only
    def can_shoot(self, bullet):
        return bullet.mass <= self.arsenal

    @kxg.read_only
    def can_not_shoot(self, bullet):
        return not self.can_shoot(bullet)

    def spend_arsenal(self, bullet):
        self.arsenal -= bullet.mass
        self._arsenal -= bullet.mass
        kxg.info("Arsenal at: {self.arsenal}")

    def recharge_arsenal(self, dt):
        if not self.arsenal == self.max_arsenal:
            self._arsenal += dt * self.arsenal_recharge_rate
            if int(self._arsenal) > self.arsenal:
                tmp = self.arsenal+1
                if tmp == self.max_arsenal:
                    kxg.info("Arsenal at: {tmp} (full)")
                else:
                    kxg.info("Arsenal at: {tmp}")
            self.arsenal = int(self._arsenal)
            if self._arsenal > self.max_arsenal:
                self._arsenal = self.max_arsenal



class Cannon(kxg.Token):

    def __init__(self, player, position):
        super().__init__()
        self.player = player
        self.position = position
        self.muzzle_speed = 100

    def __extend__(self):
        from . import gui
        return {gui.GuiActor: gui.CannonExtension}


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

        self.check_wall_bounce()

    def check_wall_bounce(self):
        field = self.world.field
        x, y = self.next_position.tuple

        if x <= field.left or x >= field.right:
            # Flip the x velocity
            self.next_velocity *= Vector(-1, 1)
        if y <= field.bottom or y >= field.top:
            # Flip the y velocity
            self.next_velocity *= Vector(1, -1)

    def move(self):
        self.position = self.next_position
        self.velocity = self.next_velocity
        self.acceleration = self.next_acceleration
        
        self.next_position = Vector.null()
        self.next_velocity = Vector.null()
        self.next_acceleration = Vector.null()


class Bullet(FieldObject):

    def __init__(self, cannon, position, velocity, mass=1):
        super().__init__(position, velocity)
        self.cannon = cannon
        self.mass = mass
        
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

