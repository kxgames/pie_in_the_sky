#!/usr/bin/env python

import kxg
from vecrec import Vector

class Player(kxg.Token):

    def __init__(self):
        super().__init__()
        from getpass import getuser
        self.name = getuser()
        self.cannons = []

    @kxg.read_only
    def has_bullet_capacity(self, bullet):
        return False


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

    def __init__(self, position, velocity, mass=1, radius=20):
        super().__init__()

        self.mass = float(mass)
        self.position = position
        self.velocity = velocity
        self.acceleration = Vector.null()
        self.radius = float(radius)
        self.vulnerable_to_bullets = True

        self.next_position = Vector.null()
        self.next_velocity = Vector.null()
        self.next_acceleration = Vector.null()

    def move(self):
        self.position = self.next_position
        self.velocity = self.next_velocity
        self.acceleration = self.next_acceleration

        self.next_position = Vector.null()
        self.next_velocity = Vector.null()
        self.next_acceleration = Vector.null()

    def bounce(self, other):
        # Define the x-axis to coincide with the line between the centers of 
        # the two colliding objects and the y-axis to be orthogonal to the 
        # x-axis.  The x component of the velocities will bounce as if this 
        # were a 1D problem, and the y components will not change.

        offset = other.position - self.position
        distance = offset.magnitude

        x = offset.unit
        y = x.orthogonal

        v1x = self.velocity.dot(x)
        v1y = self.velocity.dot(y)
        v2x = other.velocity.dot(x)
        v2y = other.velocity.dot(y)

        # Calculate the new velocities using the equations for a 1D elastic 
        # collision.

        m1, m2 = self.mass, other.mass

        v1x_final = v1x * (m1 - m2) / (m2 + m1) + v2x * (2 * m2) / (m2 + m1)
        v2x_final = v1x * (2 * m1) / (m1 + m2) + v2x * (m2 - m1) / (m1 + m2)

        # Set the final velocities by summing the x and y components of the 
        # velocity.

        self.velocity = y * v1y +  x * v1x_final
        other.velocity = y * v2y + x * v2x_final

    @kxg.read_only
    def is_touching(self, other):
        offset = self.position - other.position
        return offset.magnitude < self.radius + other.radius

    def on_hit_by_bullet(self, bullet):
        pass

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


class Bullet(FieldObject):

    def __init__(self, cannon, position, velocity):
        super().__init__(position, velocity, mass=1, radius=5)
        self.cannon = cannon
        
    def __extend__(self):
        from . import gui
        return {gui.GuiActor: gui.BulletExtension}

    @property
    def player(self):
        return self.cannon.player

    @kxg.read_only
    def on_hit_by_bullet(self, reporter, bullet):
        from . import messages
        reporter >> messages.HitBullet(bullet, self)

    def on_remove_from_world(self):
        self.world.bullets.remove(self)

class Target(FieldObject):

    def __init__(self, position, velocity):
        super().__init__(position, velocity, mass=10, radius=15)
        
    def __extend__(self):
        from . import gui
        return {gui.GuiActor: gui.TargetExtension}

    @kxg.read_only
    def on_hit_by_bullet(self, reporter, bullet):
        from . import messages
        reporter >> messages.HitTarget(bullet, self)

    def on_remove_from_world(self):
        self.world.targets.remove(self)
