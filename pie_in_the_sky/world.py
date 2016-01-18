#!/usr/bin/env python3

import kxg, pymunk, itertools
from vecrec import Rect

class World (kxg.World):
    """
    It's.
    """

    field_size = 600, 400
    gravity_constant = 1e5
    elasticity_constant = 1

    def __init__(self):
        super().__init__()

        # Initialize the game objects.

        self.field = Rect.from_size(*self.field_size)
        self.players = []
        self.bullets = []
        self.targets = []
        self.final_target = None
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

    def on_update_game(self, dt):
        super().on_update_game(dt)

        # Update players

        for player in self.players:
            player.recharge_arsenal(dt)

        # Update physics

        G = self.gravity_constant

        for obj in self.field_objects:
            obj.body.reset_forces()

        for obj_1, obj_2 in itertools.combinations(self.field_objects, 2):
            dist = obj_2.position - obj_1.position
            force = G * obj_1.mass * obj_2.mass * dist.unit / dist.magnitude_squared
            obj_1.body.apply_force(force.xy, (0,0))
            obj_2.body.apply_force((-force).xy, (0,0))

        # Note that we don't use dt as the time step because the simulation is 
        # much more efficient if the step size doesn't change between frames.

        physics_dt = 1 / 300
        for i in range(int(dt // physics_dt)):
            self.space.step(physics_dt)

