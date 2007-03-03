"""
pluginloader.py: Loading plugins
"""

import sys
import os
from CrunchyPlugin import CrunchyPlugin
    
imported_plugin_classes = []
instantiated_plugins = []

def init_plugin_system(server, plugins):
    """load the plugins"""
    CrunchyPlugin.server = server
    if not "plugins/" in sys.path:
        sys.path.insert(0, "plugins/")
    for plugin in plugins:
        mod = __import__ (plugin, globals())
        for name in dir(mod):
            obj = getattr(mod, name)
            try:
                if CrunchyPlugin in obj.__bases__:
                    imported_plugin_classes.append(obj)
            except AttributeError:
                pass
    for plugin in imported_plugin_classes:
        instantiated_plugins.append(plugin())



if __name__ == "__main__":
    init_plugin_system(["testplugins"])
