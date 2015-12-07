#!/usr/bin/env python3

import kxg

class World (kxg.World):
    def __init__(self):
        super().__init__()

        self.players = []
        self.target = None
        self.bullets = []

    def add_player(self, player):
        self.players.append(player)

    def add_bullet(self, bullet):
        pass

    def hit_target(self, player):
        pass

