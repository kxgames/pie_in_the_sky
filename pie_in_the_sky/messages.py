
import kxg
from . import tokens

class StartGame (kxg.Message):
    """
    Create the target.
    """

    def __init__(self, target_position, target_velocity):
        self.target = tokens.Target(target_position, target_velocity)

    def tokens_to_add(self):
        yield self.target

    def on_check(self, world):
        if world.target:
            raise kxg.MessageCheck("target already exists")

    def on_execute(self, world):
        world.target = self.target


class CreatePlayer (kxg.Message):
    """
    Create a player.
    """

    def __init__(self, player):
        self.player = player

    def tokens_to_add(self):
        yield self.player
        yield from player.cannons

    def on_check(self, world):
        if self.player in world.players:
            raise kxg.MessageCheck("player already exists")

    def on_execute(self, world):
        world.add_player(self.player)


class ShootBullet (kxg.Message):
    """
    Shoot a bullet
    """

    def __init__(self, cannon):
        self.bullet = cannon.fire_bullet()

    def tokens_to_add(self):
        yield self.bullet

    def on_check(self, world):
        if self.bullet.player.has_bullet_capacity(self.bullet):
            raise kxg.MessageCheck("player has too many bullets in play")

    def on_execute(self, world):
        world.add_bullet(self.player, self.bullet)


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
        if not self.target.has_collided(self.bullet):
            raise kxg.MessageCheck("bullet missed")

    def on_execute(self, world):
        world.remove_bullet(self.bullet)
        world.hit_target(self.player)





