**************
Pie In The Sky
**************

Pie in the Sky is a simple game where you try to shoot at targets faster than 
your opponents in a zero-G environment.

.. image:: resources/screenshot.png

Installation
============
First, check out the most recent version of the game from GitHub::

   $ git checkout git@github.com:kxgames/pie_in_the_sky.git

Then use pip to install the game locally::

   $ pip install ./pie_in_the_sky

Use your package manager to install the chipmunk library.  Chipmunk is a 2D 
physics engine that is required by Pie in the Sky.  The ``pip`` command will 
install the python interface to chipmunk -- ``pymunk`` -- but the game won't 
work unless the underlying libraries are present.  For fedora, the command 
would be::

   $ sudo yum install chipmunk

Usage
=====
Play a single player game against 2 AIs::

   $ pie_in_the_sky sandbox 2

Play a networked game with a friend::

   $ pie_in_the_sky server 2
   $ pie_in_the_sky client
   $ pie_in_the_sky client

Firewalls often cause problems for networked games.  By default the game uses 
port 53351, so make sure that that port is accessible to all the clients.
