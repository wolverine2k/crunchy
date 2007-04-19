"""A settings plugin - other plugins can register settings fields on startup.

There will be a few different types of option:
  * Text :: a one line text entry box.
  * MultiText :: a multiline text entry box.
  * Boolean :: A tick-box.
  * Password :: obvious.
  * Choice :: Radio-buttons or dropdown list.
  * MultiChoice :: Like choice but more than one option can be selected.

Settings will be saved and so be persistent between sessions.
"""

from CrunchyPlugin import *

provides = set(["settings"])

settings_groups = set([])


def register():
    register_http_handler("/setup", setup_page)
    register_service(register_settings_group, "register_settings_group")
    
def setup_page(request):
    """display the settings page"""
    pass

def register_settings_group(option_type, option_key, option_name, option_list, default_value):
    """plugins use this to register a set of options
    option_key should be a key (string) used to refer to this setting.
    option_name should be a (localised) description for the option.
    option_list should be a list of pairs of (key, description), where description is localised.
    default_value should be one of the keys in option_list.
    """
    if option_type == "text":
        CrunchyOptionText(option_key, option_name, default_value)
    else:
        pass

def CrunchyOption(object):
    """superclass for all Crunchy options"""
    def __init__(self, option_key, option_name, option_list, default_value):
        self.option_key = option_key
        self.option_name = option_name
        self.option_list = option_list
        self.default_value = default_value
        self.value = default_value
        settings_groups.add(self)
    def reset():
        self.value = self.default_value
    def get(self):
        raise ErrorNotImplemented
    def set(self, value):
        self.value = value
    def gen_html(self):
        raise ErrorNotImplemented
        
def CrunchyOptionText(CrunchyOption):
    def __init__(self, option_key, option_name, default_value):
        CrunchyOption.__init__(self, option_key, option_name, [], default_value)
#todo: finish this...
