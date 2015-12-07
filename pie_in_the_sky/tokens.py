#!/usr/bin/env python

import kxg
from vecrec import Vector

class Player(kxg.Token):

    def __init__(self):
        pass


class Cannon(kxg.Token):

    def __init__(self, player):
        self.player = player
        self.init_bullet_position = 0
        self.init_bullet_velocity = Vector.null()

    def fire_bullet(self):
        return Bullet(
                self, self.init_bullet_position, self.init_bullet_velocity)


class FieldObject(kxg.Token):

    def __init__(self, position, velocity):
        super().__init__()
        self.position = position
        self.velocity = velocity
        self.collision_distance = 20

    def __extend__(self):
        from . import gui
        return {gui.GuiActor: gui.FieldObjectExtension}

    def has_collided(self, object):
        distance = self.calculate_distance(object)
        return distance <= self.collision_distance

    def calculate_distance(self, object):
        delta = self.position - object.position
        return delta.magnitude


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

