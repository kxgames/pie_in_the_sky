#!/usr/bin/env python3

import os.path
import kxg, pyglet, glooey
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
                'target': pyglet.resource.image('target.png'),
                'cannon-base': pyglet.resource.image('cannon_base.png'),
                'cannon-muzzle': pyglet.resource.image('cannon_muzzle.png'),
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
        self.focus_point = Vector.null()

    def on_setup_gui(self, gui):
        self.gui = gui
        self.gui.window.set_handlers(self)

    def on_start_game(self, num_players):
        self.player = tokens.Player()
        self >> messages.CreatePlayer(self.player)

    def on_draw(self):
        self.gui.on_refresh_gui()

    def on_mouse_press(self, x, y, button, modifiers):
        # Send a "ShootBullet" signal when the user left-clicks.
        if button == 1:
            self >> messages.ShootBullet(
                    self.focus_point, self.player.cannons[0])

    def on_mouse_motion(self, x, y, dx, dy):
        self.focus_point = Vector(x, y)



class CannonExtension (kxg.TokenExtension):

    @kxg.watch_token
    def on_add_to_world(self, world):
        self.base = pyglet.sprite.Sprite(
                self.actor.gui.images['cannon-base'],
                x=self.token.position.x,
                y=self.token.position.y,
                batch=self.actor.gui.batch,
                group=pyglet.graphics.OrderedGroup(1),
        )
        if self.token.player is self.actor.player:
            self.muzzle = pyglet.sprite.Sprite(
                    self.actor.gui.images['cannon-muzzle'],
                    x=self.token.position.x,
                    y=self.token.position.y,
                    batch=self.actor.gui.batch,
                    group=pyglet.graphics.OrderedGroup(0),
            )

    @kxg.watch_token
    def on_update_game(self, dt):
        if self.token.player is self.actor.player:
            focus_vector = self.actor.focus_point - self.token.position
            self.muzzle.rotation = focus_vector.get_degrees_to((1, 0))

    @kxg.watch_token
    def on_remove_from_world(self, world):
        pass


class FieldObjectExtension (kxg.TokenExtension):

    @kxg.watch_token
    def on_add_to_world(self, world):
        self.sprite = pyglet.sprite.Sprite(
                self.actor.gui.images[self.image],
                x=self.token.position.x,
                y=self.token.position.y,
                batch=self.actor.gui.batch,
        )

    @kxg.watch_token
    def on_update_game(self, delta_t):
        self.sprite.position = self.token.position

    @kxg.watch_token
    def on_remove_from_world(self, world):
        self.sprite.delete()


class BulletExtension (FieldObjectExtension):
    image = 'bullet'

class TargetExtension (FieldObjectExtension):
    image = 'target'


