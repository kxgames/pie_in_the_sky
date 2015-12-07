
import kxg

class StartGame (kxg.Message):
    """
    Create the target.
    """

    def __init__(self, target_position, target_velocity):
        self.target = FieldObject(target_position, target_velocity)

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
        self.target = player

    def tokens_to_add(self):
        yield self.player

    def on_check(self, world):
        if self.player in world.players:
            raise kxg.MessageCheck("player already exists")

    def on_execute(self, world):
        world.add_player(self.player)


class ShootBullet (kxg.Message):
    """
    Shoot a bullet
    """

    def __init__(self, player):
        self.player = player

        position = player.init_bullet_position
        velocity = player.init_bullet_velocity
        self.bullet = FieldObject(position, velocity, player)

    def tokens_to_add(self):
        yield self.bullet

    def on_check(self, world):
        if self.player.has_bullet_capacity(self.bullet):
            raise kxg.MessageCheck("player has too many bullets in play")

    def on_execute(self, world):
        world.add_bullet(self.player, self.bullet)


class SyncWorlds (kxg.Message):
    """
    Synchronize game objects.
    """

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
        if not target.can_collide_with(bullet) and
           not bullet.can_collide_with(target)):
            raise kxg.MessageCheck("bullet missed")

    def on_execute(self, world):
        world.remove_bullet(self.bullet)
        world.hit_target(self.player)





