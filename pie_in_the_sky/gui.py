#!/usr/bin/env python3

import os.path
import kxg, pyglet, glooey, random
from vecrec import Vector
from . import world, tokens, messages

pyglet.resource.path = [
        os.path.join(os.path.dirname(__file__), '..', 'resources'),
]

class Gui:

    def __init__(self):
        self.window = pyglet.window.Window()
        self.window.set_visible(True)
        self.window.set_size(*world.World.field_size)
        self.batch = pyglet.graphics.Batch()

        # Load the background color from a resource file.

        with pyglet.resource.file('background.rgb') as file:
            bg_color_hex = file.read().decode().strip()
            self.bg_color = glooey.drawing.hex_to_float(bg_color_hex)

        # Load all the sprite images from resource files.

        self.images = {
                'bullet': pyglet.resource.image('bullet.png'),
                'empty_bullet': pyglet.resource.image('empty_bullet.png'),
                'target': pyglet.resource.image('target.png'),
                'target_black': pyglet.resource.image('target_black.png'),
                'target_blue': pyglet.resource.image('target_blue.png'),
                'target_green': pyglet.resource.image('target_green.png'),
                'target_orange': pyglet.resource.image('target_orange.png'),
                'target_pink': pyglet.resource.image('target_pink.png'),
                'target_purple': pyglet.resource.image('target_purple.png'),
                'target_red': pyglet.resource.image('target_red.png'),
                'target_teal': pyglet.resource.image('target_teal.png'),
                'target_yellow': pyglet.resource.image('target_yellow.png'),
                'obstacle': pyglet.resource.image('obstacle.png'),
                'cannon-base': pyglet.resource.image('cannon_base.png'),
                'cannon-muzzle': pyglet.resource.image('cannon_muzzle.png'),
                'explosion-1': pyglet.resource.image('explosion_1.png'),
                'explosion-2': pyglet.resource.image('explosion_2.png'),
                'explosion-3': pyglet.resource.image('explosion_3.png'),
        }

        # Center all the images except the cannon muzzle, which we will want to 
        # rotate around it's leftmost edge.

        for image in self.images.values():
            image.anchor_x = image.width / 2
            image.anchor_y = image.height / 2

        self.images['cannon-muzzle'].anchor_x = 0

    def on_refresh_gui(self):
        pyglet.gl.glClearColor(*self.bg_color)
        self.window.clear()
        self.batch.draw()


class GuiActor (kxg.Actor):
    """
    Control how players interact with the game.

    The user interface for Pie in the Sky is pretty simple.  Each player has a 
    cannon that points at the mouse and fires when the mouse is clicked.  The 
    cannons are rendered as rectangles, and the bullets and targets are 
    rendered as circles.
    """

    def __init__(self):
        super().__init__()
        self.player = None
        self.animations = []
        self.focus_point = Vector.null()
        self.show_fps = False
        self.fps_widget = pyglet.clock.ClockDisplay()

    def on_setup_gui(self, gui):
        self.gui = gui
        self.gui.window.push_handlers(self)

    def on_start_game(self, num_players):
        self.player = tokens.Player()
        self >> messages.CreatePlayer(self.player)

    def on_draw(self):
        self.gui.on_refresh_gui()
        if self.show_fps:
            self.fps_widget.draw()

    def on_update_game(self, dt):
        for animation in self.animations:
            animation.on_update(dt)

    def on_key_press(self, symbol, modifiers):
        if symbol == pyglet.window.key.SPACE:
            self.show_fps = not self.show_fps

    def on_mouse_press(self, x, y, button, modifiers):
        # Send a "ShootBullet" signal when the user left-clicks.
        if button == 1:
            target = self.focus_point
            cannon = self.player.cannons[0]

            direction = (target - cannon.position).unit
            velocity = cannon.muzzle_speed * direction
            position = cannon.position + 40 * direction

            bullet = tokens.Bullet(cannon, position, velocity)

            if self.player.can_shoot(bullet):
                self >> messages.ShootBullet(bullet)
            else:
                kxg.info("Not enough arsenal to shoot bullet!")

    def on_mouse_motion(self, x, y, dx, dy):
        self.focus_point = Vector(x, y)

    @kxg.subscribe_to_message(messages.HitSomething)
    def on_hit_by_bullet(self, message):
        ExplosionAnimation(self, message.position)

    @kxg.subscribe_to_message(messages.EndGame)
    def on_end_game(self, message):
        you_won = self.world.winner is self.player 
        self.gui.window.pop_handlers()
        self.gui.splash_message = pyglet.text.Label(
                'You won!' if you_won else 'You lost...',
                font_name='Times New Roman',
                font_size=36,
                x=self.world.field.center.x, y=self.world.field.center.y,
                anchor_x='center', anchor_y='center',
                batch=self.gui.batch,
                group=pyglet.graphics.OrderedGroup(10),
        )



class CannonExtension (kxg.TokenExtension):

    @kxg.watch_token
    def on_add_to_world(self, world):
        self.create_arsenal(world)

        self.base = pyglet.sprite.Sprite(
                self.actor.gui.images['cannon-base'],
                x=self.token.position.x,
                y=self.token.position.y,
                batch=self.actor.gui.batch,
                group=pyglet.graphics.OrderedGroup(4),
        )
        if self.token.player is self.actor.player:
            self.muzzle = pyglet.sprite.Sprite(
                    self.actor.gui.images['cannon-muzzle'],
                    x=self.token.position.x,
                    y=self.token.position.y,
                    batch=self.actor.gui.batch,
                    group=pyglet.graphics.OrderedGroup(3),
            )

    def create_arsenal(self, world):
        if self.token.player is not self.actor.player:
            return

        # create ordered arsenal position list
        bullet_radius = 5
        buffer = 1
        radius = buffer+bullet_radius
        arsenal_corner_positions = (
                Vector(  radius, 3* radius),
                Vector(  radius,    radius),
                Vector(  radius,   -radius),
                Vector(  radius, 3*-radius),
                Vector(3*radius,    radius),
                Vector(3*radius,   -radius)
        )

        # Generate ordered list of empty and full arsenal bullets
        token_position = self.token.position
        self.arsenal_images = []
        for relative_position in arsenal_corner_positions:
            position = token_position + relative_position
            empty_bullet = pyglet.sprite.Sprite(
                        self.actor.gui.images['empty_bullet'],
                        x=position.x,
                        y=position.y,
                        batch=self.actor.gui.batch,
                        group=pyglet.graphics.OrderedGroup(5),
            )
            full_bullet = pyglet.sprite.Sprite(
                        self.actor.gui.images['bullet'],
                        x=position.x,
                        y=position.y,
                        batch=self.actor.gui.batch,
                        group=pyglet.graphics.OrderedGroup(5),
            )
            empty_bullet.visible = True
            full_bullet.visible = False

            self.arsenal_images.append({
                "empty" : empty_bullet,
                "full" : full_bullet
            })

    @kxg.watch_token
    def on_update_game(self, dt):
        if self.token.player is not self.actor.player:
            return

        focus_vector = self.actor.focus_point - self.token.position
        self.muzzle.rotation = focus_vector.get_degrees_to((1, 0))

        arsenal_count = self.token.player.arsenal
        # activate full bullets
        for bullet in self.arsenal_images[0:arsenal_count]:
            if not bullet["full"].visible:
                bullet["empty"].visible = False
                bullet["full"].visible = True

        # activate empty bullets
        for bullet in self.arsenal_images[arsenal_count:]:
            if not bullet["empty"].visible:
                bullet["empty"].visible = True
                bullet["full"].visible = False

    @kxg.watch_token
    def on_remove_from_world(self):
        pass


class FieldObjectExtension (kxg.TokenExtension):

    @kxg.watch_token
    def on_add_to_world(self, world):
        self.sprite = pyglet.sprite.Sprite(
                self.actor.gui.images[self.get_image()],
                x=self.token.position.x,
                y=self.token.position.y,
                batch=self.actor.gui.batch,
                group=pyglet.graphics.OrderedGroup(1),
        )

    def get_image(self):
        return self.image

    @kxg.watch_token
    def on_update_game(self, delta_t):
        self.sprite.position = self.token.position

    @kxg.watch_token
    def on_remove_from_world(self):
        self.sprite.delete()


class BulletExtension (FieldObjectExtension):
    image = 'bullet'

class TargetExtension (FieldObjectExtension):

    def get_image(self):
        if not self.token.owner:
            return 'target_black'
        elif self.token.owner is self.actor.player:
            return 'target_red'
        else:
            return 'target_blue'


class ObstacleExtension (FieldObjectExtension):
    image = 'obstacle'


class ExplosionAnimation:

    def __init__(self, actor, position):
        self.actor = actor; self.actor.animations.append(self)
        self.position = position
        self.scale_velocity = -2
        self.scale_acceleration = -4
        self.num_images = 3

        self.explosion_sprites = [
                pyglet.sprite.Sprite(
                    self.actor.gui.images['explosion-'+str(i+1)],
                    x=self.position.x,
                    y=self.position.y,
                    batch=self.actor.gui.batch,
                    group=pyglet.graphics.OrderedGroup(-(i+1)),
                )
                for i in range(self.num_images)
        ]
        self.rotation_rates = [
                random.randrange(180, 360) * (-1)**i
                for i in range(self.num_images)
        ]

    def on_update(self, dt):
        for i in range(self.num_images):
            sprite = self.explosion_sprites[i]
            sprite.scale += self.scale_velocity * dt
            sprite.rotation += self.rotation_rates[i] * dt

        self.scale_velocity += self.scale_acceleration * dt

        if sprite.scale < 0:
            self.actor.animations.remove(self)
            for sprite in self.explosion_sprites:
                sprite.delete()



