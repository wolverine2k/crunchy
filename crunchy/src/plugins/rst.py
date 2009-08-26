"""Plugin for loading and transforming ReST files."""

# Note: much of the rst directives code was created as part of the
# Google Highly Open Participation Contest 2007/8 by
# Copyright (C) 2008 Zachary Voase <cracka80 at gmail dot com>
#
# It was adapted and incorporated into Crunchy by A. Roberge

# All plugins should import the crunchy plugin API via interface.py
import codecs
import os
from src.interface import plugin, python_version, StringIO, translate
_ = translate['_']
from src.utilities import unicode_urlopen

_docutils_installed = True
try:
    from docutils.core import publish_string
    from docutils.parsers import rst as rst_test
    if "Directive" not in dir(rst_test):
        print("rst plugin disabled: docutils installed but version too old.")
        _docutils_installed = False
except:
    _docutils_installed = False
    print("rst plugin disabled: docutils not installed.")

if _docutils_installed:
    provides = set(["/rst"])
    requires = set(["filtered_dir", "insert_file_tree"])
    from os import linesep
    from docutils.parsers import rst
    from docutils.writers.html4css1 import HTMLTranslator
    from docutils import nodes

def register(): # tested
    """Registers new http handler and new widget for loading ReST files"""
    if _docutils_installed:
        plugin['register_http_handler']("/rst", load_rst)
        plugin['register_tag_handler']("div", "title", "local_rst_file", insert_load_rst)
        plugin['register_preprocessor']('txt', convert_rst)
        # the following does nothing as Firefox does not recognize rst files as
        # something it can deal with - we may have to find a way to tell
        # Firefox that these are equivalent to text files.
        plugin['register_preprocessor']('local_rst', convert_rst)
        plugin['add_vlam_option']('power_browser', 'rst')
        plugin['register_http_handler']("/jquery_file_tree_rst", jquery_file_tree_rst)
        plugin['register_service']("local_rst", insert_load_rst)

if _docutils_installed:

    class crunchy(nodes.raw):
        def __init__(self, *args, **kwargs):
            nodes.raw.__init__(self, *args, **kwargs)
            self.tagname = "pre"

    class CrunchyDirective(rst.Directive):
        required_arguments = 0
        optional_arguments = 20  # make sure we have enough!
        final_argument_whitespace = False
        has_content = True
        def run(self):
            content = linesep.join(self.content)
            listOut = [ x.strip() for x in self.arguments]
            titleAttr = " ".join(listOut)
            return [ crunchy(title=titleAttr, text=content, CLASS="rst_crunchy") ]
            # the class is going to be a class attribute and is simply included
            # as a demo - something like this is to be used in crst2s5.py
            # for a better purpose...

    def visit_crunchy(translator, node):
        attrDict = {}
        for key, value in list(node.attributes.items()):
            if value and (key is not "xml:space"):
                attrDict[key] = value
        translator.body.append(translator.starttag(node, 'pre', **attrDict))

    def depart_crunchy(translator, node):
        translator.body.append('\n</pre>\n')

    HTMLTranslator.visit_crunchy = visit_crunchy
    HTMLTranslator.depart_crunchy = depart_crunchy

    rst.directives.register_directive('crunchy', CrunchyDirective)

class ReST_file(StringIO):
    """Represents file with transformed text from rst into html.
    vlam thinks it is an ordinary file object"""
    pass

def load_rst(request):
    """Loads rst file from disk,
    transforms it into html and then creates new page"""
    url = request.args["url"]
    file_ = codecs.open(url, 'r', 'utf-8')

    # docutils returns bytes (Python 3)
    data = publish_string(file_.read(), writer_name="html").decode('utf-8')
    rst_file = ReST_file(data)
    page = plugin['create_vlam_page'](rst_file, url, local=True,
                                      username=request.crunchy_username)
    page = page.read().encode('utf-8') # encoding required for Python 3

    request.send_response(200)
    request.end_headers()
    request.wfile.write(page)

def convert_rst(path, local=True):
    '''converts an rst file into a proper crunchy-ready html page'''
    if local:
        file_ = codecs.open(path, 'r', 'utf-8')
    else:
        file_ = unicode_urlopen(path)
    data = publish_string(file_.read(), writer_name="html").decode('utf-8')
    rst_file = ReST_file(data)
    return rst_file

def insert_load_rst(page, elem, uid):
    "Inserts a javascript browser object to load a local reStructuredText file."
    plugin['services'].insert_file_tree(page, elem, uid, '/jquery_file_tree_rst',
                                '/rst', _('Load local reStructuredText file'),
                                _('Load rst file'))
    return
plugin['rst'] = insert_load_rst

def filter_rst(filename, basepath):
    '''filters out all files and directory with filename so as to include
       only files whose extensions are ".rst" or ".txt" with the possible
       exception of ".crunchy" - the usual crunchy default directory.
    '''
    if filename.startswith('.') and filename != ".crunchy":
        return True
    else:
        fullpath = os.path.join(basepath, filename)
        if os.path.isdir(fullpath):
            return False   # do not filter out directories
        ext = os.path.splitext(filename)[1][1:] # get .ext and remove dot
        if ext == 'rst' or ext == "txt":
            return False
        else:
            return True

def jquery_file_tree_rst(request):
    '''extract the file information and formats it in the form expected
       by the jquery FileTree plugin, but excludes some normally hidden
       files or directories, to include only reStructuredText files.'''
    plugin['services'].filtered_dir(request, filter_rst)
    return
