#!/usr/bin/env python3

import kxg
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

        self.debug_timer = 0

    def add_bullet(self, player, bullet):
        self.bullets.append(bullet)

    def remove_bullet(self, bullet):
        self.bullets.remove(bullet)

    def hit_target(self, player):
        # End the game...
        raise NotImplementedError

    def on_update_game(self, delta_t):

        super().on_update_game(delta_t)

        self.debug_timer += delta_t
        # Calculate motion phase
        self.calculate_motions(delta_t)

        # Motion phase
        for field_object in self.field_objects:
            field_object.move()

        if self.debug_timer >= 1:
            self.debug_timer -= 1

        ## Collision detection phase
        #colliding_pairs = self.detect_collisions()

        ## Collision handling phase

    def calculate_motions(self, delta_t):
        """ 
        Calculate new accelerations, velocities, and positions.
        """

        # Calculate new accelerations
        # Note, this assumes the objects have already cleared their 
        # accelerations
        gravity_objects = self.targets + self.bullets
        unchecked_objects = gravity_objects[:]
        for object_1 in gravity_objects:
            unchecked_objects.remove(object_1)
            for object_2 in unchecked_objects:
                m1 = object_1.mass
                p1 = object_1.position
                m2 = object_2.mass
                p2 = object_2.position
                G = self.gravity_constant

                distance = p2 - p1
                distance_unit = distance.get_unit()
                partial_force = G * distance.unit / distance.magnitude_squared

                a1 = m2 * partial_force
                a2 = m1 * -partial_force

                object_1.add_next_acceleration(a1)
                object_2.add_next_acceleration(a2)

        
        # Calculate new velocities and positions based on the new 
        # accelerations.
        for field_object in self.field_objects:
            field_object.calculate_motion(delta_t)

    def detect_collisions(self):
        """
        Find any instances of bullets hitting other objects and return a list of colliding pairs of bullet and hittable objects. 

        """
        
        collision_pairs = []

        unchecked_bullets = self.bullets[:]
        # Check all hittable objects to see if any can hit or be hit by any 
        # bullet. (They may have different collision distances.)
        for hittable in self.hittable_objects:

            if hittable in unchecked_bullets:
                # Hittable is a bullet. It will be checked for all possible 
                # collisions during this iteration. Further checks aren't 
                # necessary.
                unchecked_bullets.remove(hittable)

            for bullet in unchecked_bullets:
                if hittable.can_collide_with(bullet) or bullet.can_collide_with(hittable): 
                    collision_pairs.append(hittable, bullet)
                    
        return collision_pairs

    @property
    def field_objects(self):
        return self.targets + self.bullets[:]

