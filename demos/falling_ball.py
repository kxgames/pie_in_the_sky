#!/usr/bin/env python3

import pyglet, random, itertools
import pymunk, pymunk.pyglet_util

window = pyglet.window.Window()
fps_display = pyglet.clock.ClockDisplay()

space = pymunk.Space()
space.gravity = 0,-900

mass = 10
radius = 25
inertia = pymunk.moment_for_circle(mass, 0, radius, (0,0))
body = pymunk.Body(mass, inertia)
body.position = window.width/2, window.height/2
ball = pymunk.Circle(body, radius, (0,0))
ball.elasticity = 0.95
space.add(body, ball)

def on_time_step(dt):
    # Note that we don't use dt as input into step.  The simulation behaves 
    # much better if the step size doesn't change between frames.
    steps = 10
    for i in range(steps):
        space.step(1/30/steps)
        print(ball.body.position)

@window.event
def on_draw():
    pyglet.gl.glClearColor(240,240,240,255)
    window.clear()
    fps_display.draw()
    pymunk.pyglet_util.draw(space)


pyglet.clock.schedule_interval(on_time_step, 1/30)
pyglet.app.run()

