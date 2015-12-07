#!/usr/bin/env python3

import kxg
from . import messages

class Referee (kxg.Referee):

    def __init__(self):
        super().__init__()
        self.num_players_expected = None

    def on_start_game(self, num_players):
        self.num_players_expected = num_players

    @kxg.subscribe_to_message(messages.CreatePlayer)
    def on_create_player(self, message):
        num_players_joined = len(self.world.players)
        kxg.info("{num_players_joined} of {self.num_players_expected} players created.")

        if num_players_joined == self.num_players_expected:
            from vecrec import Vector
            position = Vector(100, 100)
            velocity = Vector(10, 10)
            self >> messages.StartGame(position, velocity)


