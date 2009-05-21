"""
comet.py:  unit tests in test_comet.rst

Simple plugin whose only role is to register the cometIO basic handlers.
For consistency, we register all handlers via plugins located in the plugins
directory so that they are easier to locate, and that names duplication
can be avoided.
"""

from src.interface import plugin
from src.cometIO import comet, push_input

provides = set(["/comet", "/input"])

def register():  # tested
    '''registers two http handlers: /input and /comet'''
    plugin['register_http_handler'](
                    "/input%s" % plugin['session_random_id'], push_input)
    plugin['register_http_handler']("/comet", comet)
