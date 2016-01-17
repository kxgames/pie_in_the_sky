#!/usr/bin/env python3

import kxg, pymunk, itertools
from vecrec import Rect

class World (kxg.World):
    """
    It's.
    """

    field_size = 600, 400
    gravity_constant = 1e5
    elasticity_constant = 0.95

    def __init__(self):
        super().__init__()

        # Initialize the game objects.

        self.field = Rect.from_size(*self.field_size)
        self.players = []
        self.bullets = []
        self.targets = []
        self.obstacles = []
        self.winner = None

        # Initialize the 2D physics simulator.

        self.space = pymunk.Space()
        self.space.gravity = 0, 0
        self.make_boundary()

    @property
    def field_objects(self):
        yield from self.bullets
        yield from self.targets
        yield from self.obstacles

    @property
    def non_bullets(self):
        yield from self.targets
        yield from self.obstacles

    def hit_target(self, player):
        # End the game...
        raise NotImplementedError

    def on_update_game(self, delta_t):
        super().on_update_game(delta_t)

        # Update players

        for player in self.players:
            player.recharge_arsenal(delta_t)

        # Update physics

        G = self.gravity_constant

        for obj in self.field_objects:
            obj.body.reset_forces()

        for obj_1, obj_2 in itertools.combinations(self.field_objects, 2):
            dist = obj_2.position - obj_1.position
            force = G * obj_1.mass * obj_2.mass * dist.unit / dist.magnitude_squared
            obj_1.body.apply_force(force.xy, (0,0))
            obj_2.body.apply_force((-force).xy, (0,0))

        for i in range(10):
            self.space.step(1/300)

    @kxg.read_only
    def on_report_to_referee(self, reporter):
        pass
        #from . import messages
        #for bullet, field_object in self.yield_bullet_collisions():
        #    field_object.on_hit_by_bullet(reporter, bullet)
        #    break

    @kxg.read_only
    def make_boundary(self):
        w, h = self.field.size
        static_body = pymunk.Body()
        walls = [
                pymunk.Segment(static_body, (0,0), (0,h), 0),
                pymunk.Segment(static_body, (0,h), (w,h), 0),
                pymunk.Segment(static_body, (w,h), (w,0), 0),
                pymunk.Segment(static_body, (w,0), (0,0), 0),
        ]
        for wall in walls:
            wall.elasticity = 1
        self.space.add(walls)

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
            force = G * m1 * m2 * offset.unit / offset.magnitude_squared

            fo1.add_next_acceleration(force / abs(m1))
            fo2.add_next_acceleration(-force / abs(m2))

        # Calculate new velocities and positions based on the new 
        # accelerations.
        for fo in self.field_objects:
            fo.calculate_motion(delta_t)

    @kxg.read_only
    def yield_bullet_collisions(self):
        for b1, b2 in itertools.combinations(self.bullets, 2):
            if b1.is_touching(b2):
                yield b1, b2

        for b, nb in itertools.product(self.bullets, self.non_bullets):
            if b.is_touching(nb):
                yield b, nb

    @kxg.read_only
    def yield_bouncing_collisions(self):
        for nb1, nb2 in itertools.combinations(self.non_bullets, 2):
            if nb1.is_touching(nb2):
                yield nb1, nb2

