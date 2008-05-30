"""Plugin for loading and transforming ReST files."""

# Note: much of the rst directives code was created as part of the
# Google Highly Open Participation Contest 2007/8 by
# Copyright (C) 2008 Zachary Voase <cracka80 at gmail dot com>
#
# It was adapted and incorporated into Crunchy by A. Roberge

# All plugins should import the crunchy plugin API via interface.py
from src.interface import plugin
from src.utilities import insert_file_browser
from urllib import urlopen

_docutils_installed = True
try:
    from docutils.core import publish_string
    from docutils.parsers import rst as rst_test
    if "Directive" not in dir(rst_test):
        print("rst plugin disabled: docutils installed but version too old.")
        _docutils_installed = False
except:
    _docutils_installed = False

if _docutils_installed:
    provides = set(["/rst"])
    from os import linesep
    from docutils.parsers import rst
    from docutils.writers.html4css1 import HTMLTranslator
    from docutils import nodes

def register():
    """Registers new http handler and new widget for loading ReST files"""
    if _docutils_installed:
        plugin['register_http_handler']("/rst", load_rst)
        plugin['register_tag_handler']("span", "title", "load_rst", insert_load_rst)
        plugin['register_preprocessor']('txt', convert_rst)
        # the following does nothing as Firefox does not recognize rst files as
        # something it can deal with - we may have to find a way to tell
        # Firefox that these are equivalent to text files.
        plugin['register_preprocessor']('rst', convert_rst)

if _docutils_installed:
    def int_or_one(argument):
        """If no argument is present, returns 1.
        Else returns argument as integer."""
        if argument and argument.strip():
            return int(argument)
        else:
            return 1

    class pre(nodes.raw):
        def __init__(self, *args, **kwargs):
            nodes.raw.__init__(self, *args, **kwargs)
            self.tagname = "pre"

    class InterpreterDirective(rst.Directive):
        required_arguments = 1
        optional_arguments = 1
        final_argument_whitespace = False
        option_spec = {
            'linenumber' : int_or_one,
            'log_id' : str
        }
        has_content = True
        def run(self):
            code = linesep.join(self.content)
            if self.arguments[0].strip() not in ['interpreter', 'isolated',
                                        'parrot', 'Parrots', 'TypeInfoConsole']:
                raise ValueError("Wrong interpreter type: %s" % (self.arguments[0].strip(),))
            if len(self.arguments) is 2:
                if self.arguments[1].strip() is not "no_style":
                    raise ValueError("Invalid argument: %s" % (self.arguments[1].strip(),))
            listOut = [ x.strip() for x in self.arguments ]
            for key in [ "linenumber", "log_id" ]:
                if self.options.has_key(key):
                    listOut.append(key + "=%s" % (str(self.options[key]),))
            titleAttr = " ".join(listOut)
            return [ pre(title=titleAttr, text=code) ]

    class EditorDirective(rst.Directive):
        required_arguments = 0
        optional_arguments = 5
        final_argument_whitespace = False
        option_spec = {
            'linenumber' : int_or_one,
            'log_id' : str
        }
        has_content = True
        def run(self):
            code = linesep.join(self.content)
            for arg in self.arguments:
                if arg.strip() not in ['no_style', 'no_copy', 'no_pre',
                                       'external', 'no_internal']:
                    raise ValueError("Invalid argument: %s" % (arg.strip(),))
            listOut = [ x.strip() for x in ['editor'] + self.arguments ]
            for key in [ "linenumber", "log_id" ]:
                if self.options.has_key(key):
                    listOut.append(key + "=%s" % (str(self.options[key]),))
            titleAttr = " ".join(listOut)
            return [ pre(title=titleAttr, text=code) ]

    class DocTestDirective(rst.Directive):
        required_arguments = 0
        optional_arguments = 1
        option_spec = {
            'linenumber' : int_or_one,
            'log_id' : str
        }
        has_content = True
        def run(self):
            self.assert_has_content()
            code = linesep.join(self.content)
            if len(self.arguments) is 1:
                if self.arguments[0] is not 'no_style':
                    raise ValueError("Invalid argument: %s" % (self.arguments[0].strip(),))
            listOut = [ x.strip() for x in ['doctest'] + self.arguments ]
            for key in [ "linenumber", "log_id" ]:
                if self.options.has_key(key):
                    listOut.append(key + "=%s" % (str(self.options[key]),))
            titleAttr = " ".join(listOut)
            return [ pre(title=titleAttr, text=code) ]

    class ImageFileDirective(rst.Directive):
        required_arguments = 1
        optional_arguments = 3
        option_spec = {
            'linenumber' : int_or_one
        }
        has_content = True
        def run(self):
            code = linesep.join(self.content)
            for arg in self.arguments[1:]:
                if arg.strip() not in [ 'no_style', 'no_copy', 'no_pre' ]:
                    raise ValueError("Invalid argument: %s" % (arg.strip(),))
            listOut = [ x.strip() for x in ['image_file'] + self.arguments ]
            if self.options.has_key("linenumber"):
                listOut.append("linenumber=%d" % (self.options["linenumber"],))
            titleAttr = " ".join(listOut)
            return [ pre(title=titleAttr, text=code) ]

    class PythonCodeDirective(rst.Directive):
        required_arguments = 0
        optional_arguments = 0
        option_spec = {
            'linenumber' : int_or_one
        }
        has_content = True
        def run(self):
            code = linesep.join(self.content)
            listOut = ['python_code']
            if self.options.has_key("linenumber"):
                listOut.append("linenumber=%d" % (self.options["linenumber"],))
            titleAttr = " ".join(listOut)
            return [ pre(title=titleAttr, text=code) ]

    class AltPythonVersionDirective(rst.Directive):
        required_arguments = 0
        optional_arguments = 5
        final_argument_whitespace = False
        option_spec = {
            'linenumber' : int_or_one
        }
        has_content = True
        def run(self):
            code = linesep.join(self.content)
            for arg in self.arguments:
                if arg.strip() not in ['no_style', 'no_copy', 'no_pre',
                                       'external', 'no_internal']:
                    raise ValueError("Invalid argument: %s" % (arg.strip(),))
            listOut = [ x.strip() for x in ['alternate_python_version'] + self.arguments ]
            if self.options.has_key("linenumber"):
                listOut.append("linenumber=%d" % (self.options["linenumber"],))
            titleAttr = " ".join(listOut)
            return [ pre(title=titleAttr, text=code) ]

    class NoVLAMDirective(rst.Directive):
        required_arguments = 0
        optional_arguments = 0
        final_argument_whitespace = False
        option_spec = {}
        has_content = True
        def run(self):
            self.assert_has_content()
            code = linesep.join(self.content)
            listOut = ['no_vlam']
            titleAttr = " ".join(listOut)
            return [ pre(title=titleAttr, text=code) ]

    DIRECTIVE_DICT = {
        'interpreter' : InterpreterDirective,
        'editor' : EditorDirective,
        'doctest' : DocTestDirective,
        'image_file' : ImageFileDirective,
        'py_code' : PythonCodeDirective,
        'python_code' : PythonCodeDirective,
        'alternate_python_version' : AltPythonVersionDirective,
        'alt_py' : AltPythonVersionDirective,
        'no_vlam' : NoVLAMDirective
        }

    def visit_pre(translator, node):
        attrDict = {}
        for key, value in node.attributes.items():
            if value and (key is not "xml:space"):
                attrDict[key] = value
        translator.body.append(translator.starttag(node, 'pre', **attrDict))

    def depart_pre(translator, node):
        translator.body.append('\n</pre>\n')

    HTMLTranslator.visit_pre = visit_pre
    HTMLTranslator.depart_pre = depart_pre

if _docutils_installed:
    for key, value in DIRECTIVE_DICT.items():
        rst.directives.register_directive( key, value )

class ReST_file(object):
    """Represents file with transformed text from rst into html.
    vlam thinks it is an ordinary file object"""
    def __init__(self, data):
        self._data = data
    def read(self):
        return self._data

def load_rst(request):
    """Loads rst file from disk,
    transforms it into html and then creates new page"""
    url = request.args["url"]
    file_ = open(url)

    rst_file = ReST_file(publish_string(file_.read(), writer_name="html"))
    page = plugin['create_vlam_page'](rst_file, url, local=True)

    request.send_response(200)
    request.end_headers()
    request.wfile.write(page.read())

def convert_rst(path, local=True):
    '''converts an rst file into a proper crunchy-ready html page'''
    if local:
        file_ = open(path)
    else:
        file_ = urlopen(path)
    rst_file = ReST_file(publish_string(file_.read(), writer_name="html"))
    return rst_file

def insert_load_rst(dummy_page, parent, dummy_uid):
    """Creates new widget for loading rst files.
    Only include <span title="load_rst"> </span>"""
    insert_file_browser(parent, 'Load local ReST file', '/rst')
    return
