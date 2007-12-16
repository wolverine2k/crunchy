# -*- coding: utf-8 -*-
'''
universal.py

This file contains references to various functions in a way that it works
regardless of the Python version.

Until we succeed in making Crunchy compatible with both Python 2.x and 3.x,
we keep this file (and tools*) at the top level of the package so that
we can run tests successfully.
'''

import sys

version = sys.version.split('.')
python_version = float(version[0] + '.' + version[1][0])

if python_version < 3:
    import tools
else:
    import tools_3k as tools

u_print = tools.u_print