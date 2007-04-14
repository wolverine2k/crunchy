"""A settings plugin - other plugins can register settings fields on startup.

There will be a few different types of option:
  * Text :: a text entry box.
  * Boolean :: A tick-box.
  * Password :: obvious.
  * Choice :: Radio-buttons or dropdown list.
  * MultiChoice :: Like choice but more than one option can be selected.

Settings will be saved and so be persistent between sessions.
"""

from CrunchyPlugin import *

def register():
    register_http_handler("/setup", setup_page)
    register_service(register_settings_group, "register_settings_group")
    
def setup_page(request):
    """display the settings page"""
    pass

def register_settings_group(tabname, groupname, options, initvalue):
    """plugins use this to register a set of options"""
    pass
