#!/usr/bin/env python3

import kxg
from vecrec import Rect

class World (kxg.World):

    field_size = 600, 400

    def __init__(self):
        super().__init__()
        self.field = Rect.from_size(*self.field_size)
        self.players = []
        self.targets = []
        self.bullets = []

    def add_bullet(self, player, bullet):
        self.bullets.append(bullet)

    def remove_bullet(self, bullet):
        self.bullets.remove(bullet)

    def hit_target(self, player):
        # End the game...
        raise NotImplementedError

