'''
Code common to Crunchy (rst.py plugin) and crst2s5

'''
import inspect
import os
import sys
import traceback

from docutils.parsers import rst
from docutils import nodes

info = {}  # initialized from calling module

class crunchy(nodes.raw):
    def __init__(self, *args, **kwargs):
        nodes.raw.__init__(self, *args, **kwargs)
        self.tagname = "pre"

class getpythonsource(nodes.raw):
    def __init__(self, *args, **kwargs):
        nodes.raw.__init__(self, *args, **kwargs)
        self.tagname = "pre"

class CrunchyDirective(rst.Directive):
    required_arguments = 0
    optional_arguments = 20  # make sure we have enough!
    final_argument_whitespace = False
    has_content = True
    def run(self):
        content = "\n".join(self.content)
        listOut = [ x.strip() for x in self.arguments]
        titleAttr = " ".join(listOut)
        return [ crunchy(title=titleAttr, text=content) ]

class GetPythonSourceDirective(rst.Directive):
    # Note that this version is intentionnally different from the one in
    # Crunchy itself.
    required_arguments = 1
    optional_arguments = 20  # make sure we have enough!
    final_argument_whitespace = False
    has_content = True
    def run(self):
        to_be_inspected, listOut = extract_object_name(self.arguments)
        base, module_name, source = extract_module_information(to_be_inspected)
        content, lineno = get_source_content(base, module_name, source)
        content = ''.join(content)
        if lineno == 0:
            lineno = 1
        titleAttr = " ".join(listOut)
        try:
            int(lineno)
            if 'linenumber' in titleAttr:
                titleAttr = titleAttr.replace('linenumber', 'linenumber=%s'%lineno)
        except:
            pass
        return [ getpythonsource(title=titleAttr, text=content) ]

rst.directives.register_directive('crunchy', CrunchyDirective)
rst.directives.register_directive('getpythonsource', GetPythonSourceDirective)

def extract_object_name(arguments):
    '''extract the object name (of which the source is to be inspected)
       and removes it from the list of arguments'''
    to_be_inspected = arguments[0]
    others = arguments[1:]
    return to_be_inspected, others

def extract_module_information(path_):
    '''extracts the module relative path from path_, the module name and the
       required information (source) to import.

       It is assumed that the path contains no spaces and
       that the path separator is /'''
       # sample format path_ = "../src/module.function"]  should yield
       # ("../src", "module", "module.function")
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

def get_source_content(base, mod_name, source):
    mod_dir = os.path.normpath(os.path.join(info['source_base_dir'], base))
    if mod_dir in sys.path:
        remove_from_syspath = False
    else:
        sys.path.insert(0, mod_dir)
        remove_from_syspath = True
    content, lineno = get_lines(mod_name, source) # lineno could be == "Exception"
    if remove_from_syspath:
        sys.path.remove(mod_dir)
    return content, lineno

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
