"""
pluginloader.py: Loading plugins
"""

import sys
import os

class CrunchyPlugin(object):
    """superclass for all Crunchy Plugins"""
    pass
    
imported_plugins = []
 
def register_plugin(plugin):
    global imported_plugins
    imported_plugins.append(plugin)
        

def init_plugin_system(plugins):
    if not "plugins/" in sys.path:
        sys.path.insert(0, "plugins/")
    for plugin in plugins:
        __import__ (plugin, None, None, [''])
    

if __name__ == "__main__":
    init_plugin_system(["testplugins","test"])
    print imported_plugins
