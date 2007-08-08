"""
comet.py

Simple plugin whose only role is to register the cometIO basic handlers.
For consistency, we register all handlers via a plugin in the plugins
directory so that they are easier to locate, and that names duplication
can be avoided.
"""

import src.CrunchyPlugin as CrunchyPlugin
from src.cometIO import comet, push_input

provides = set(["/comet", "/input"])

def register():
    CrunchyPlugin.register_http_handler(
                    "/input%s"%CrunchyPlugin.session_random_id, push_input)
    CrunchyPlugin.register_http_handler("/comet", comet)
