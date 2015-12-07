
import kxg
from . import tokens

class StartGame (kxg.Message):
    """
    Create the target.
    """

    def __init__(self, world):
        from vecrec import Vector
        field = world.field

        # Create the target and give it a somewhat random initial position and 
        # velocity.

        position = field.center + Vector.random(field.height/4)
        velocity = Vector.random(10)
        self.target = tokens.Target(position, velocity)

        # Create a cannon for each player and decide which side of the field 
        # each one should go on.

        players = world.players
        num_players = len(players)

        if num_players == 1:
            self.cannons = [
                    tokens.Cannon(players[0], field.center_left),
            ]
        elif num_players == 2:
            self.cannons = [
                    tokens.Cannon(players[0], field.center_left),
                    tokens.Cannon(players[1], field.center_right),
            ]
        else:
            raise ValueError("Must have either 1 or 2 players")

    def tokens_to_add(self):
        yield self.target
        yield from self.cannons

    def on_check(self, world):
        if world.targets:
            raise kxg.MessageCheck("target already exists")

    def on_execute(self, world):
        world.targets = [self.target]

        for cannon in self.cannons:
            player = cannon.player
            player.cannons = [cannon]


class CreatePlayer (kxg.Message):
    """
    Create a player.
    """

    def __init__(self, player):
        self.player = player

    def tokens_to_add(self):
        yield self.player

    def on_check(self, world):
        if self.player in world.players:
            raise kxg.MessageCheck("player already exists")

    def on_execute(self, world):
        world.players.append(self.player)


class ShootBullet (kxg.Message):
    """
    Shoot a bullet
    """

    def __init__(self, target, cannon):
        direction = (target - cannon.position).unit
        velocity = cannon.muzzle_speed * direction
        position = cannon.position + 40 * direction
        self.bullet = tokens.Bullet(cannon, position, velocity)

    def tokens_to_add(self):
        yield self.bullet

    def on_check(self, world):
        if self.bullet.player.has_bullet_capacity(self.bullet):
            raise kxg.MessageCheck("player has too many bullets in play")

    def on_execute(self, world):
        world.bullets.append(self.bullet)


class SyncWorlds (kxg.Message):
    """
    Synchronize game objects.
    """
    pass

class HitTarget (kxg.Message):
    """
    Hit a target. 
    """

    def __init__(self, target, bullet):
        self.target = target
        self.bullet = bullet
        self.player = bullet.player

    def tokens_to_remove(self):
        yield self.bullet, self.target

    def on_check(self, world):
        target = self.target
        bullet = self.bullet
        if not target.can_collide_with(bullet) and not bullet.can_collide_with(target):
            raise kxg.MessageCheck("bullet missed")

    def on_execute(self, world):
        world.remove_bullet(self.bullet)
        world.hit_target(self.player)





