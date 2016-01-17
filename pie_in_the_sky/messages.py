
import kxg
from . import tokens

class StartGame (kxg.Message):
    """
    Create the target.
    """

    def __init__(self, world):
        from vecrec import Vector
        field = world.field

        # Create a few targets and give them somewhat random initial positions 
        # and velocities.

        random_offset = Vector.random(field.height/4)
        random_velocity = Vector.random(10)

        self.targets = [
                tokens.Target(field.center + random_offset, random_velocity),
                tokens.Target(field.center - random_offset, -random_velocity),
        ]

        # Create a few obstacles in the same way.

        self.obstacles = [
                tokens.Obstacle(
                    field.center + Vector.random(field.height / 3),
                    Vector.random(10))
                for i in range(1)
        ]

        # Create a cannon for each player and decide which side of the field 
        # each one should go on.

        players = world.players
        num_players = len(players)
        self.cannons = []

        for i in range(num_players):
            position = Vector(
                    field.left, (i + 1) * field.height / (num_players + 1))
            self.cannons.append(
                    tokens.Cannon(players[i], position))

    def tokens_to_add(self):
        yield from self.targets
        yield from self.obstacles
        yield from self.cannons

    def on_check(self, world):
        if world.targets:
            raise kxg.MessageCheck("target already exists")

    def on_execute(self, world):
        world.targets = self.targets
        world.obstacles = self.obstacles

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

    def __init__(self, bullet):
        self.bullet = bullet
        self.player = bullet.player

    def tokens_to_add(self):
        yield self.bullet

    def on_check(self, world):
        if self.player.can_not_shoot(self.bullet):
            raise kxg.MessageCheck("player does not have enough bullet capacity.")

    def on_execute(self, world):
        world.bullets.append(self.bullet)
        self.player.spend_arsenal(self.bullet)


class SyncWorlds (kxg.Message):
    """
    Synchronize game objects.
    """
    pass

class HitBullet (kxg.Message):
    """
    When two bullets collide with each other, destroy both of them.
    """

    def __init__(self, bullet_1, bullet_2):
        self.bullets = bullet_1, bullet_2

    def tokens_to_remove(self):
        yield from self.bullets

    def on_check(self, world):
        pass


class HitTarget (kxg.Message):
    """
    Hit a target or a power-up with a bullet. 
    """

    def __init__(self, bullet, target):
        self.bullet = bullet
        self.target = target

    def tokens_to_remove(self):
        yield self.bullet
        yield self.target

    def on_check(self, world):
        pass

    def on_execute(self, world):
        pass


class HitObstacle (kxg.Message):
    """
    Hit a target or a power-up with a bullet. 
    """

    def __init__(self, bullet, obstacle):
        self.bullet = bullet
        self.obstacle = obstacle

    def tokens_to_remove(self):
        yield self.bullet

    def on_check(self, world):
        pass

    def on_execute(self, world):
        pass





