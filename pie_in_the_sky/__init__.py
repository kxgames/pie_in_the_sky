#!/usr/bin/env python3

from .metadata import *
from .world import *
from .referee import *
from .gui import *
from .ai import *

def main():
    import kxg
    kxg.quickstart.main(World, Referee, Gui, GuiActor, AiActor)

