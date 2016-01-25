#!/usr/bin/env python3

import cProfile
import pie_in_the_sky as pie

cProfile.run('pie.main()', 'restats')

import pstats
p = pstats.Stats('restats')
p.strip_dirs().sort_stats('time').print_stats(100)
