"""
pluginloader.py: Loading plugins
"""

import sys
import os
import CrunchyPlugin

def gen_register_list(initial_list):
    """generates a registration ordering from the dependencies"""
    print "Ordering plugins by dependencies"
    final_list = []
    found_this_iter = True
    while (len(initial_list) > 0) and found_this_iter:
        found_this_iter = False
        for mod in initial_list:
            if not hasattr(mod, "requires"):
                mod.requires = set()
            if not hasattr(mod, "provides"):
                mod.provides = set()
            capability_set = set()
            pos = 0
            while pos < len(final_list):
                capability_set.update(final_list[pos].provides)
                pos += 1
            if mod.requires.issubset(capability_set):
                final_list.insert(len(final_list), mod)
                initial_list.remove(mod)
                found_this_iter = True
                break
            
    #by now final_list should have been constructed, go ahead and print initial list:
    print initial_list
    return final_list
                    
                
        
def init_plugin_system(server, plugins):
    """load the plugins"""
    CrunchyPlugin.server = server
    if not "plugins/" in sys.path:
        sys.path.insert(0, "plugins")
    imported_plugins = []
    print "Importing plugins"
    for plugin in plugins:
        mod = __import__ (plugin, globals())
        imported_plugins.append(mod)
    register_list = gen_register_list(imported_plugins)
    print "Registering plugins"
    for mod in register_list:
        if hasattr(mod, "register"):
            mod.register()
            print "  * Registered %s" % mod.__name__



if __name__ == "__main__":
    init_plugin_system(["testplugins"])