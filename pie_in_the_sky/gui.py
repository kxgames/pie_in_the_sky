#!/usr/bin/env python3

import os.path
import kxg, pyglet, glooey

from . import world
from . import tokens
from . import messages

pyglet.resource.path = [
        os.path.join(os.path.dirname(__file__), '..', 'resources'),
]

class Gui:

    def __init__(self):
        self.window = pyglet.window.Window()
        self.window.set_visible(True)
        self.window.set_size(*world.World.field_size)
        self.batch = pyglet.graphics.Batch()

        with pyglet.resource.file('background.rgb') as file:
            bg_color_hex = file.read().decode().strip()
            self.bg_color = glooey.drawing.hex_to_float(bg_color_hex)

        self.bullet_image = pyglet.resource.image('bullet.png')
        self.target_image = pyglet.resource.image('target.png')

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
            self << messages.ShootBullet(self.player)

    def on_mouse_motion(self, x, y, dx, dy):
        pass



class CannonExtension (kxg.TokenExtension):

    @kxg.watch_token
    def on_add_to_world(self, world):
        pass

    @kxg.watch_token
    def on_remove_from_world(self, world):
        pass


class FieldObjectExtension (kxg.TokenExtension):

    @kxg.watch_token
    def on_add_to_world(self, world):
        self.sprite = pyglet.sprite.Sprite(
                self.image,
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

    @property
    def image(self):
        return self.actor.gui.bullet_image


class TargetExtension (FieldObjectExtension):

    @property
    def image(self):
        return self.actor.gui.target_image



