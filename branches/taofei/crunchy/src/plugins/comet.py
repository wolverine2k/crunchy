"""
comet.py

Simple plugin whose only role is to register the cometIO basic handlers.
For consistency, we register all handlers via a plugin in the plugins
directory so that they are easier to locate, and that names duplication
can be avoided.
"""

from src.interface import plugin
from src.cometIO import comet, push_input

requires = set(["apply_io_hook"])
provides = set(["/comet", "/input"])

def register():
    '''registers two http handlers: /input and /comet'''
    plugin['register_http_handler'](
                    "/input%s" % plugin['session_random_id'], push_input)
    plugin['register_http_handler']("/comet", comet)
