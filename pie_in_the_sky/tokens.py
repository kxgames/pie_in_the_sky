#!/usr/bin/env python

import kxg

Class FieldObject(kxg.Token):
    def __init__(self, player=None):
        super().__init__()

        self.player = player
        self.collision_distance = 20

    def has_collided(self, object):
        distance = self.calculate_distance(object)
        return distance <= self.collision_distance

    def calculate_distance(self, object):
        delta = self.position - object.position
        return delta.magnitude

