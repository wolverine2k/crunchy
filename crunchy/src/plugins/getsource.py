# -*- coding: utf-8 -*-
"""gets source code or parts thereof automatically from python file.
"""

import inspect
import os
import sys
import traceback

from src.interface import config, plugin, python_version, SubElement, Element

def register():
    plugin['register_tag_handler']("div", "title", "getsource", get_source)

def get_source(page, elem, uid):
    elem.text = " "
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
    if remove_from_syspath:
        sys.path.remove(mod_dir)
    if lineno == "Exception":
        insert_traceback(page, elem, lines)
        return
    if lineno == 0:
        lineno = 1
    insert_code(page, elem, uid, lines, lineno)
    return

def insert_traceback(page, elem, tb):
    '''inserts a traceback, nicely styled.'''
    pre = SubElement(elem, "pre")
    vlam = "pytb"
    pre.attrib['title'] = vlam
    pre.text = tb
    dummy, dummy = plugin['services'].style(page, pre, None, vlam)
    # prevent any further processing
    pre.attrib["title"] = "no_vlam"
    return

def insert_code(page, elem, uid, lines, lineno):
    '''insert the code in the element and style it appropriately'''
    # Note: in developping this plugin, we observed that the code was styled
    # automatically - that is the "div/getsource" handler was called before the
    # "pre" handler was.  This could just be a coincidence on which we can not
    # rely.
    pre = Element("pre")
    if 'editor' in elem.attrib['title']:
        vlam = "editor"
    elif 'interpreter' in elem.attrib['title']:
        vlam = "interpreter"
    elif python_version < 3:
        vlam = "python"
    else:
        vlam = "python3"
    if "linenumber" in elem.attrib['title']:
        vlam += " linenumber=%s"%lineno
    pre.attrib['title'] = vlam
    pre.text ="".join(lines)
    if 'editor' in vlam:
        insert_editor(page, elem, uid, lines, lineno)
    elif 'interpreter' in vlam:
        insert_interpreter(page, elem, uid, lines, lineno)
    else:
        dummy, dummy = plugin['services'].style(page, pre, None, vlam)
        elem.append(pre)
    # prevent any further processing
    pre.attrib["title"] = "no_vlam"
    return

def insert_editor(page, elem, uid, lines, lineno):
    '''insert the an editor as usual'''
    # Note: in developping this plugin, we observed that the code was styled
    # automatically - that is the "div/getsource" handler was called before the
    # "pre" handler was.  This could just be a coincidence on which we can not
    # rely.
    pre = SubElement(elem, "pre")
    if python_version < 3:
        vlam = "python"
    else:
        vlam = "python3"
    if "linenumber" in elem.attrib['title']:
        vlam += " linenumber=%s"%lineno
    pre.attrib['title'] = vlam
    pre.text ="".join(lines)
    plugin['services'].insert_editor(page, pre, uid)
    # prevent any further processing
    pre.attrib["title"] = "no_vlam"
    return

def insert_interpreter(page, elem, uid, lines, lineno):
    '''insert the an editor as usual'''
    # Note: in developping this plugin, we observed that the code was styled
    # automatically - that is the "div/getsource" handler was called before the
    # "pre" handler was.  This could just be a coincidence on which we can not
    # rely.
    pre = SubElement(elem, "pre")
    if python_version < 3:
        vlam = "python"
    else:
        vlam = "python3"
    if "linenumber" in elem.attrib['title']:
        vlam += " linenumber=%s"%lineno
    pre.attrib['title'] = vlam
    pre.text ="".join(lines)
    plugin['services'].insert_interpreter(page, pre, uid)
    # prevent any further processing
    pre.attrib["title"] = "no_vlam"
    return


def get_lines(mod_name, source):
    '''get the lines of code from an object located in module mod_name as well
       as the line number of the first line of the object returned.

    The object is referred to in the usual Python syntax for import statements
    e.g. source == mod_name.A_Class.a_method
    '''
    try:
        mod = __import__(mod_name)
    except:
        return traceback.format_exc(), "Exception"

    to_inspect = {mod_name: mod}

    source_split = source.split(".")
    _obj = [mod_name]
    for i, s in enumerate(source_split):
        if i != 0:
            _obj.append(_obj[-1] + "." + s)
            try:
                to_inspect[_obj[i]] = getattr(to_inspect[_obj[i-1]], s)
            except:
                return traceback.format_exc(), "Exception"

    try:
        return inspect.getsourcelines(to_inspect[source])
    except:
        return traceback.format_exc(), "Exception"

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