#!/usr/bin/env python3

import kxg

from . import tokens
from . import messages

class AiActor (kxg.Actor):

    def on_start_game(self, num_players):
        self.player = tokens.Player()
        self >> messages.CreatePlayer(self.player)

