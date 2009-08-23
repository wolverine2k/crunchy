# -*- coding: utf-8 -*-
"""gets source code or parts thereof automatically from python file.
"""

import inspect
import os
import sys

from src.interface import config, plugin, python_version, SubElement

def register():
    plugin['register_tag_handler']("div", "title", "getsource", get_source)

def get_source(page, elem, uid):
    elem.text = "Plugin was called; vlam = %s; url = %s; local = %s" % (elem.attrib["title"], page.url, page.is_local)
    vlam = elem.attrib["title"]
    tut_path = get_tutorial_path(page)
    base, mod_name, source = extract_module_information(vlam)
    mod_path = get_source_fullpath(tut_path, base, mod_name)
    previous_cwd = os.getcwd()
    os.chdir(os.path.dirname(mod_path))
    cwd = os.getcwd()
    sys.path.insert(0, cwd)
    mod = __import__(mod_name)
    to_inspect = {}
    source_split = source.split(".")
    source_path = [mod_name]
    for i, s in enumerate(source_split):
        if i != 0:
            source_path.append(source_path[-1] + "." + s)
            print i, s, source_path[i]

    to_inspect[mod_name] = mod
    for i, s in enumerate(source_split):
        if i != 0:
            print i, s, source_path[i]
            to_inspect[source_path[i]] = getattr(to_inspect[source_path[i-1]], s)

    pre = SubElement(elem, "pre")
    _info = inspect.getsourcelines(to_inspect[source])
    lines = _info[0]
    linenumber = _info[1]
    for line in lines:
        print line
    print linenumber
    print "-"*66
    os.chdir(previous_cwd)
    sys.path.remove(cwd)
    pre.text = "".join(lines)

def get_tutorial_path(page):
    '''obtains the full path of the local tutorial'''
    if page.is_local:   # tutorial loaded from browser - full path is known
        tutorial_fullpath = page.url
    elif page.is_from_root:
        tutorial_fullpath = os.path.join(config['crunchy_base_dir'], "server_root", page.url[1:])
    else:
        raise Exception
    return tutorial_fullpath

def extract_module_information(vlam):
    '''extracts the module relative path from vlam, the module name and the
       required information (source) to import.

       It is assumed that the path contains no spaces and
       that the path separator is /'''
       # format vlam = "getsource path [optional arguments]"
    path_ = vlam.split()[1]
    if "/" in path_:
        parts = path_.split("/")
        base = '/'.join(parts[:-1])
        source = parts[-1]
    else:
        base = ''
        source = path_
    if "." in source:  # e.g. module.function
        module_name = source.split(".")[0]
    else:
        module_name = source
    return base, module_name, source

def get_source_fullpath(tutorial_fullpath, base, module_name):
    '''combine the tutorial full path, the relative base path of the
    module to be imported and the module name to give the path
    of the module to import'''
    return os.path.normpath(os.path.join(os.path.dirname(tutorial_fullpath), base, module_name))