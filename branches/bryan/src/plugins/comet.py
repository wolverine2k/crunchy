"""
comet.py

Simple plugin whose only role is to register the cometIO basic handlers.
For consistency, we register all handlers via a plugin in the plugins
directory so that they are easier to locate, and that names duplication
can be avoided.
"""

import src.CrunchyPlugin as CrunchyPlugin
from src.cometIO import comet, push_input
from src.security import update_security

provides = set(["/comet", "/input", "/update"])

def register():
    CrunchyPlugin.register_http_handler("/input", push_input )
    CrunchyPlugin.register_http_handler("/comet", comet)
    CrunchyPlugin.register_http_handler("/update%s"%CrunchyPlugin.session_random_id, update_security)
