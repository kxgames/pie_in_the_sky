#!/usr/bin/env python3

import kxg, itertools
from vecrec import Rect

class World (kxg.World):
    """
    It's.
    """

    field_size = 600, 400

    def __init__(self):
        super().__init__()
        self.field = Rect.from_size(*self.field_size)
        self.players = []
        self.targets = []
        self.bullets = []

        self.gravity_constant = 10.0**5

    @property
    def field_objects(self):
        yield from self.targets
        yield from self.bullets

    @property
    def non_bullets(self):
        yield from self.targets

    def hit_target(self, player):
        # End the game...
        raise NotImplementedError

    def on_update_game(self, delta_t):
        super().on_update_game(delta_t)

        # Update players

        for player in self.players:
            player.recharge_arsenal(delta_t)

        # Calculate motion phase

        self.calculate_motions(delta_t)

        # Motion phase

        for field_object in self.field_objects:
            field_object.move()

        # Collision detection phase

        for obj1, obj2 in self.yield_bouncing_collisions():
            obj1.bounce(obj2)

    def on_report_to_referee(self, reporter):
        from . import messages
        for bullet, field_object in self.yield_bullet_collisions():
            reporter >> messages.HitSomething(bullet, field_object)

    def calculate_motions(self, delta_t):
        """ 
        Calculate new accelerations, velocities, and positions.
        """

        # Calculate new accelerations
        # Note, this assumes the objects have already cleared their 
        # accelerations
        for fo1, fo2 in itertools.combinations(self.field_objects, 2):

            # Don't calculate gravity for objects that are too close to each 
            # other, to avoid weird artifacts.
            if fo1.is_touching(fo2):
                continue

            m1 = fo1.mass
            p1 = fo1.position
            m2 = fo2.mass
            p2 = fo2.position
            G = self.gravity_constant

            offset = p2 - p1
            partial_force = G * offset.unit / offset.magnitude_squared

            fo1.add_next_acceleration(m2 * partial_force)
            fo2.add_next_acceleration(-m1 * partial_force)

        # Calculate new velocities and positions based on the new 
        # accelerations.
        for fo in self.field_objects:
            fo.calculate_motion(delta_t)

    def yield_bullet_collisions(self):
        for b1, b2 in itertools.combinations(self.bullets, 2):
            if b1.is_touching(b2):
                yield b1, b2

        for b, nb in itertools.product(self.bullets, self.non_bullets):
            if b.is_touching(nb):
                yield b, nb

    def yield_bouncing_collisions(self):
        for nb1, nb2 in itertools.combinations(self.non_bullets, 2):
            if nb1.is_touching(nb2):
                yield nb1, nb2

