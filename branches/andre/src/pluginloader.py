"""
pluginloader.py: Loading plugins
"""

import sys
import os
from imp import find_module
import os.path

import src.interface as interface

DEBUG = False
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
    interface.server['server'] = server

    # In case Crunchy was not started from its root directory via
    # python crunchy.py, but instead from another directory like
    # python /this/path/to/crunchy.py
    # we need to add explictly the path to the
    sys.path.insert(0, os.path.join(interface.plugin['get_root_dir'](),
                                    "src", "plugins"))

    # In addition, add the same for the non-plugins files that are meant to be
    # imported by the user, such as graphics.py, etc.
    # For this, we always need the absolute path as the base path may be changed
    # by the user through some code execution.
    sys.path.insert(0, os.path.join(interface.plugin['get_root_dir'](),
                                    "src", "imports"))

    imported_plugins = []
    if DEBUG:
        print("Importing plugins.")
    for plugin in plugins:
        mod = __import__ (plugin, globals())
        imported_plugins.append(mod)
    register_list = gen_register_list(imported_plugins)
    if DEBUG:
        print("Registering plugins.")
    for mod in register_list:
        if hasattr(mod, "register"):
            if server != ["testplugins"]:  # skip for self-testing
                mod.register()
            if DEBUG:
                print("  * Registered %s" % mod.__name__)

if __name__ == "__main__":
    DEBUG = True
    init_plugin_system(["testplugins"])