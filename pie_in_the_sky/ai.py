#!/usr/bin/env python3

import kxg, random
from . import tokens, messages
from vecrec import Vector

class AiActor (kxg.Actor):

    def __init__(self):
        super().__init__()

    def on_start_game(self, num_players):
        self.player = tokens.Player()
        self >> messages.CreatePlayer(self.player)


class CannonExtension (kxg.TokenExtension):

    @kxg.watch_token
    def on_add_to_world(self, world):
        if self.token.player is not self.actor.player:
            return

        self.reset_shot_timer()

    @kxg.watch_token
    def on_update_game(self, dt):
        if self.token.player is not self.actor.player:
            return

        cannon = self.token
        player = self.token.player
        world = self.token.world

        self.shot_timer -= dt
        if self.shot_timer < 0:
            self.reset_shot_timer()

            # Pick the closest target to aim at.

            def distance_to_cannon(target):
                return cannon.position.get_distance(target.position)

            if self.token.player.targets:
                target = sorted(player.targets, key=distance_to_cannon)[0]
            else:
                target = world.final_target

            # Aim in front of the target with some variance.

            aim = target.position - cannon.position
            aim += target.velocity * 5
            aim += 0.0 * aim.magnitude * Vector.random()
            aim.normalize()

            velocity = cannon.muzzle_speed * aim
            position = cannon.position + 40 * aim
            bullet = tokens.Bullet(cannon, position, velocity)

            # Shoot unless we're out of bullets.

            if player.can_shoot(bullet):
                self.actor >> messages.ShootBullet(bullet)
            else:
                self.shot_timer /= 2

    def reset_shot_timer(self):
        self.shot_timer = random.uniform(0.3, 1.0)


