"""
pluginloader.py: Loading plugins
"""

import sys
import os
from imp import find_module
import os.path

import CrunchyPlugin

def gen_register_list(initial_list):
    """generates a registration ordering from the dependencies.
    It could happen that some plugin would require (at loading time)
    some services provided by others.
    This function ensures that plugin will be loaded so as
    to ensure that "required" plugins are loaded before "requiring" ones.
    """
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
    return final_list

def gen_plugin_list():
    '''looks for all python files in directory "plugins/", and assume
    that they are all "plugins".'''
    pluginpath = os.path.join(os.path.dirname(find_module("crunchy")[1]),
                             "src", "plugins/")
    pluginfiles = [x[:-3] for x in os.listdir(pluginpath) if x.endswith(".py")]
    return pluginfiles

def init_plugin_system(server):
    """load the plugins and has them self-register."""
    plugins = gen_plugin_list()
    CrunchyPlugin.server = server
    if not "src/plugins/" in sys.path:
        sys.path.insert(0, "src/plugins")
    imported_plugins = []
    if CrunchyPlugin.DEBUG:
        print "Importing plugins"
    for plugin in plugins:
        mod = __import__ (plugin, globals())
        imported_plugins.append(mod)
    register_list = gen_register_list(imported_plugins)
    if CrunchyPlugin.DEBUG:
        print "Registering plugins"
    for mod in register_list:
        if hasattr(mod, "register"):
            if server != ["testplugins"]:  # skip for self-testing
                mod.register()
            if CrunchyPlugin.DEBUG:
                print "  * Registered %s" % mod.__name__

if __name__ == "__main__":
    CrunchyPlugin.DEBUG = True
    init_plugin_system(["testplugins"])