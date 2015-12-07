
import kxg
from . import tokens

class StartGame (kxg.Message):
    """
    Create the target.
    """

    def __init__(self, field):
        from vecrec import Vector

        # Create the target and give it a somewhat random initial position and 
        # velocity.

        position = field.center + Vector.random(field.height/4)
        velocity = Vector.random(10)
        self.target = tokens.Target(position, velocity)

        # Create a cannon for each player and decide which side of the field 
        # each one should go on.

        #self.cannons = []

        #if num_players == 1:
        #    cannon = 
        #for i in range(num_players):
        #    cannon = tokens.Cannon()


    def tokens_to_add(self):
        yield self.target

    def on_check(self, world):
        if world.targets:
            raise kxg.MessageCheck("target already exists")

    def on_execute(self, world):
        world.targets = [self.target]




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
        target = self.target
        bullet = self.bullet
        if not target.can_collide_with(bullet) and not bullet.can_collide_with(target):
            raise kxg.MessageCheck("bullet missed")

    def on_execute(self, world):
        world.remove_bullet(self.bullet)
        world.hit_target(self.player)





