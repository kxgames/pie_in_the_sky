#!/usr/bin/env python

import kxg, pymunk
from vecrec import Vector, cast_anything_to_vector

class Player(kxg.Token):

    def __init__(self):
        super().__init__()
        from getpass import getuser
        self.name = getuser()
        self.cannons = []
        self.targets = []

        self.max_arsenal = 6
        self.arsenal = self.max_arsenal
        self._arsenal = float(self.max_arsenal)
        self.arsenal_recharge_rate = 1/2

    def add_target(self, target):
        self.targets.append(target)

    def remove_target(self, target):
        self.targets.remove(target)

    @kxg.read_only
    def can_shoot(self, bullet):
        return bullet.mass <= self.arsenal

    @kxg.read_only
    def cannot_shoot(self, bullet):
        return not self.can_shoot(bullet)

    def spend_arsenal(self, bullet):
        self.arsenal -= bullet.mass
        self._arsenal -= bullet.mass

    def recharge_arsenal(self, dt):
        if not self.arsenal == self.max_arsenal:
            self._arsenal += dt * self.arsenal_recharge_rate
            self.arsenal = int(self._arsenal)
            if self._arsenal > self.max_arsenal:
                self._arsenal = self.max_arsenal


class Cannon(kxg.Token):

    def __init__(self, player, position):
        super().__init__()
        self.player = player
        self.position = position
        self.muzzle_speed = 150

    def __extend__(self):
        from . import gui, ai
        return {
                gui.GuiActor: gui.CannonExtension,
                ai.AiActor: ai.CannonExtension,
        }


class FieldObject(kxg.Token):
    """
    A base class for targets, bullets, obstacles, and other objects that are in the field of play. Instances of this base class can be used if special methods are not necessary for a type of object. This class defines default functionality for motion, collisions, and updating.
    """

    def __init__(self, position, velocity, mass=1, radius=20):
        super().__init__()

        inertia = pymunk.moment_for_circle(mass, 0, radius, (0,0))
        self.body = pymunk.Body(int(mass), inertia)
        self.body.position = position.xy
        self.body.velocity = velocity.xy
        self.shape = pymunk.Circle(self.body, radius, (0,0))
        self.shape.collision_type = self.collision_type
        self.shape.token = self
    
    @property
    def mass(self):
        return int(self.body.mass)

    @property
    def radius(self):
        return self.shape.radius

    @property
    def position(self):
        return cast_anything_to_vector(self.body.position)

    @property
    def velocity(self):
        return cast_anything_to_vector(self.body.velocity)

    def on_add_to_world(self, world):
        self.shape.elasticity = world.elasticity_constant
        world.space.add(self.body, self.shape)

    def on_remove_from_world(self):
        self.world.space.remove(self.body, self.shape)

    def on_hit_by_bullet(self, bullet):
        pass


class Bullet(FieldObject):

    collision_type = 1

    def __init__(self, cannon, position, velocity):
        super().__init__(position, velocity, mass=1, radius=5)
        self.cannon = cannon
        
    def __extend__(self):
        from . import gui
        return {gui.GuiActor: gui.BulletExtension}

    @property
    def player(self):
        return self.cannon.player

    def on_remove_from_world(self):
        super().on_remove_from_world()
        self.world.bullets.remove(self)


class Target(FieldObject):

    collision_type = 2

    def __init__(self, position, velocity, owner=None):
        super().__init__(position, velocity, mass=2, radius=15)
        self.owner = owner
        
    def __extend__(self):
        from . import gui
        return {gui.GuiActor: gui.TargetExtension}

    @property
    def is_final_target(self):
        return self.owner is None

    def on_remove_from_world(self):
        super().on_remove_from_world()
        self.world.targets.remove(self)


class Obstacle(FieldObject):

    collision_type = 3

    def __init__(self, position, velocity):
        super().__init__(position, velocity, mass=5, radius=20)

    def __extend__(self):
        from . import gui
        return {gui.GuiActor: gui.ObstacleExtension}

    def on_remove_from_world(self):
        super().on_remove_from_world()
        self.world.obstacles.remove(self)

