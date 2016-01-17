#!/usr/bin/env python3

import pyglet, random, itertools
import pymunk, pymunk.pyglet_util

window = pyglet.window.Window()
fps_display = pyglet.clock.ClockDisplay()

space = pymunk.Space()
space.gravity = 0,-100

def make_walls(window, space, elasticity=0.95):
    w, h = window.get_size()
    static_body = pymunk.Body()
    walls = [
            pymunk.Segment(static_body, (0,0), (0,h), 0),
            pymunk.Segment(static_body, (0,h), (w,h), 0),
            pymunk.Segment(static_body, (w,h), (w,0), 0),
            pymunk.Segment(static_body, (w,0), (0,0), 0),
    ]
    for wall in walls:
        wall.elasticity = elasticity
    space.add(walls)
    return walls

def make_ball(window, space, mass=10, radius=25, elasticity=0.95):
    inertia = pymunk.moment_for_circle(mass, 0, radius, (0,0))
    body = pymunk.Body(mass, inertia)
    x = window.width * random.random()
    y = window.height * random.random()
    body.position = x, y
    ball = pymunk.Circle(body, radius, (0,0))
    ball.elasticity = elasticity
    space.add(body, ball)
    return ball

def add_spring(space, a, b):
    spring = pymunk.DampedSpring(
            a.body, b.body, (0,0), (0,0),
            rest_length=a.radius + b.radius,
            stiffness=10, damping=0)
    space.add(spring)


walls = make_walls(window, space)
balls = [make_ball(window, space) for i in range(10)]
for b1, b2 in itertools.combinations(balls, 2):
    add_spring(space, b1, b2)

def on_time_step(dt):
    # Note that we don't use dt as input into step.  The simulation behaves 
    # much better if the step size doesn't change between frames.
    steps = 10
    for i in range(steps):
        space.step(1/30/steps)

@window.event
def on_draw():
    pyglet.gl.glClearColor(240,240,240,255)
    window.clear()
    pymunk.pyglet_util.draw(space)
    fps_display.draw()


pyglet.clock.schedule_interval(on_time_step, 1/30)
pyglet.app.run()

