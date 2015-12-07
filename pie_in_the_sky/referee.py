#!/usr/bin/env python3

import kxg
from . import messages

class Referee (kxg.Referee):

    def on_start_game(self):
        from vecrec import Vector
        position = Vector(100, 100)
        velocity = Vector.null()
        self >> messages.StartGame(position, velocity)
