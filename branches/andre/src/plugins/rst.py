"""Plugin for loading and transforming ReST files."""

# Note: much of the rst directives code was created as part of the
# Google Highly Open Participation Contest 2007/8 by
# Copyright (C) 2008 Zachary Voase <cracka80 at gmail dot com>
#
# It was adapted and incorporated into Crunchy by A. Roberge

# All plugins should import the crunchy plugin API via interface.py
from src.interface import plugin, SubElement

_docutils_installed = True
try:
    from docutils.core import publish_string
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
                if arg.strip() not in ['no_style', 'no-copy', 'no-pre',
                                       'external', 'no-internal']:
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
                if arg.strip() not in [ 'no_style', 'no-copy', 'no-pre' ]:
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
                if arg.strip() not in ['no_style', 'no-copy', 'no-pre',
                                       'external', 'no-internal']:
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
            listOut = ['no-vlam']
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
        'no-vlam' : NoVLAMDirective
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

class ReST_file:
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

def insert_load_rst(dummy_page, parent, dummy_uid):
    """Creates new widget for loading rst files.
    Only include <span title="load_rst"> </span>"""
    name1 = 'browser_rst'
    name2 = 'submit_rst'
    form1 = SubElement(parent, 'form', name=name1,
                        onblur = "document.%s.url.value="%name2+\
                        "document.%s.filename.value"%name1)
    SubElement(form1, 'input', type='file', name='filename', size='80')
    SubElement(form1, 'br')

    form2 = SubElement(parent, 'form', name=name2, method='get', action='/rst')
    SubElement(form2, 'input', type='hidden', name='url')
    input3 = SubElement(form2, 'input', type='submit',
                        value='Load local ReST file')
    input3.attrib['class'] = 'crunchy'
