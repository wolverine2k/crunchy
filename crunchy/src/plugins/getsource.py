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

    if "show_vlam" in vlam:
        elem.insert(0, plugin['services'].show_vlam(page, elem, vlam))

    tut_path = get_tutorial_path(page)
    base, mod_name, source = extract_module_information(vlam)
    mod_path = get_source_fullpath(tut_path, base, mod_name)
    mod_dir = os.path.dirname(mod_path)
    if mod_dir in sys.path:
        remove_from_syspath = False
    else:
        sys.path.insert(0, mod_dir)
        remove_from_syspath = True
    lines, lineno = get_lines(mod_name, source)
    pre = SubElement(elem, "pre")
    if remove_from_syspath:
        sys.path.remove(mod_dir)
    pre.text = "".join(lines)
    return

def get_lines(mod_name, source):
    '''get the lines of code from an object located in module mod_name as well
       as the line number of the first line of the object returned.

    The object is referred to in the usual Python syntax for import statements
    e.g. source == mod_name.A_Class.a_method
    '''
    mod = __import__(mod_name)
    to_inspect = {mod_name: mod}

    source_split = source.split(".")
    _obj = [mod_name]
    for i, s in enumerate(source_split):
        if i != 0:
            _obj.append(_obj[-1] + "." + s)
            to_inspect[_obj[i]] = getattr(to_inspect[_obj[i-1]], s)

    return inspect.getsourcelines(to_inspect[source])

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