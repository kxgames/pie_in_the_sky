#!/usr/bin/env python3

import kxg
from . import messages, tokens

class Referee (kxg.Referee):

    def __init__(self):
        super().__init__()
        self.num_players_expected = None
        self.last_sync = 0

    def on_start_game(self, num_players):
        self.num_players_expected = num_players

        self.world.space.add_collision_handler(
                tokens.Bullet.collision_type,
                tokens.Bullet.collision_type,
                post_solve=self.on_hit_bullet,
        )
        self.world.space.add_collision_handler(
                tokens.Bullet.collision_type,
                tokens.Target.collision_type,
                post_solve=self.on_hit_target,
        )
        self.world.space.add_collision_handler(
                tokens.Bullet.collision_type,
                tokens.Obstacle.collision_type,
                post_solve=self.on_hit_obstacle,
        )

    @kxg.subscribe_to_message(messages.CreatePlayer)
    def on_create_player(self, message):
        num_players_joined = len(self.world.players)
        kxg.info("{num_players_joined} of {self.num_players_expected} players created.")

        if num_players_joined == self.num_players_expected:
            self >> messages.StartGame(self.world)

    def on_update_game(self, dt):
        self.last_sync += dt
        if self.last_sync > 1:
            self >> messages.SyncWorlds(self.world)
            self.last_sync = 0

    def on_hit_bullet(self, space, arbiter):
        bullet = arbiter.shapes[0].token
        other_bullet = arbiter.shapes[1].token
        self >> messages.HitBullet(bullet, other_bullet)

    def on_hit_target(self, space, arbiter):
        bullet = arbiter.shapes[0].token
        target = arbiter.shapes[1].token
        self >> messages.HitTarget(bullet, target)
        if not bullet.player.targets and target.is_final_target:
            self >> messages.EndGame(bullet.player)

    def on_hit_obstacle(self, space, arbiter):
        bullet = arbiter.shapes[0].token
        obstacle = arbiter.shapes[1].token
        self >> messages.HitObstacle(bullet, obstacle)


def on_hit_bullet(space, arbiter, reporter):
    bullet = arbiter.shapes[0].token
    other_bullet = arbiter.shapes[1].token
    reporter >> messages.HitBullet(bullet, other_bullet)

