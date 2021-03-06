
import kxg, random
from . import tokens

class StartGame (kxg.Message):
    """
    Create the target.
    """

    def __init__(self, world):
        from vecrec import Vector
        field = world.field

        def random_position():
            return field.center + Vector.random(0.4*field.height)
        def random_velocity():
            return Vector.random(50)

        # Create a few obstacles in the same way.

        self.obstacles = [
                tokens.Obstacle(
                    Vector(
                        random.randrange(field.left + 100, field.center_x),
                        random.randrange(field.bottom + 100, field.top - 100),
                    ),
                    Vector.random(10))
                for i in range(2)
        ]

        # Create a cannon and several targets for each player and decide which 
        # side of the field each cannon should go on.

        self.targets = []
        targets_per_player = 2

        players = world.players
        num_players = len(players)
        self.cannons = []

        for i in range(num_players):
            player = players[i]
            position = Vector(
                    field.left, (i + 1) * field.height / (num_players + 1))
            self.cannons.append(
                    tokens.Cannon(player, position))

            for j in range(targets_per_player):
                x = field.width * 2/3
                y = field.height * (1 + i * targets_per_player + j) / (num_players * targets_per_player + 1)
                target = tokens.Target(
                        Vector(x, y), random_velocity(), player)
                self.targets.append(target)

        # Create the final target

        self.final_target = tokens.Target(
                Vector(field.width * 3/4, field.center_y),
                random_velocity(),
        )
        self.targets.append(self.final_target)

    def tokens_to_add(self):
        yield from self.targets
        yield from self.obstacles
        yield from self.cannons

    def on_check(self, world):
        if world.targets:
            raise kxg.MessageCheck("targets already exists")

    def on_execute(self, world):
        world.targets = self.targets
        world.final_target = self.final_target
        world.obstacles = self.obstacles

        for cannon in self.cannons:
            player = cannon.player
            player.cannons = [cannon]

        for target in self.targets:
            if target.owner:
                target.owner.add_target(target)


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
        if self.player.cannot_shoot(self.bullet):
            raise kxg.MessageCheck("player does not have enough bullet capacity.")

    def on_execute(self, world):
        world.bullets.append(self.bullet)
        self.player.spend_arsenal(self.bullet)


class SyncWorlds (kxg.Message):
    """
    Synchronize game objects.
    """

    def __init__(self, world):
        self.state = {
                token: (token.position.xy, token.velocity.xy)
                for token in world.field_objects
        }

    def on_check(self, world):
        if not self.was_sent_by_referee():
            raise kxg.MessageCheck('sync must be sent by referee')

    def on_execute(self, world):
        for token in self.state:
            token.body.position, token.body.velocity = self.state[token]


class HitSomething (kxg.Message):

    def __init__(self, bullet):
        self.position = bullet.position

    def on_check(self, world):
        pass

    def on_execute(self, world):
        pass


class HitBullet (HitSomething):
    """
    When two bullets collide with each other, destroy both of them.
    """

    def __init__(self, bullet_1, bullet_2):
        super().__init__(bullet_1)
        self.bullets = bullet_1, bullet_2

    def tokens_to_remove(self):
        yield from self.bullets


class HitTarget (HitSomething):
    """
    Hit a target or a power-up with a bullet. 
    """

    def __init__(self, bullet, target):
        super().__init__(bullet)
        self.bullet = bullet
        self.shooter = bullet.cannon.player

        self.target = None
        self.owner = target.owner

        if self.owner == self.shooter:
            # Player hitting there target
            self.target = target
        elif not (self.owner or self.shooter.targets):
            # Player hitting final target
            self.target = target

    def tokens_to_remove(self):
        yield self.bullet
        if self.target:
            yield self.target

    def on_execute(self, world):
        if self.owner == self.shooter:
            self.owner.remove_target(self.target)


class HitObstacle (HitSomething):
    """
    Hit a target or a power-up with a bullet. 
    """

    def __init__(self, bullet, obstacle):
        super().__init__(bullet)
        self.bullet = bullet
        self.obstacle = obstacle

    def tokens_to_remove(self):
        yield self.bullet


class EndGame (kxg.Message):

    def __init__(self, winner):
        self.winner = winner

    def on_check(self, world):
        if world.is_game_over():
            raise kxg.MessageCheck("game already over")

    def on_execute(self, world):
        world.winner = self.winner
        world.end_game()
