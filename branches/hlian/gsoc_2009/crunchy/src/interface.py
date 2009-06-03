# -*- coding: utf-8 -*-
'''
interface.py

The purpose of this module is two-fold:

1. Acting as a "dispatcher" to select the appropriate function/module
depending on which Python function is used.

2. Creating an interface (or bridge) between modules (such as plugins)
and the Crunchy core so that these modules can be tested as independently
as possible from those in Crunchy's core.

'''
import imp
import os
import sys
version = sys.version.split('.')
python_version = float(version[0] + '.' + version[1][0])

# StringIO is used for creating in-memory files
# We also take a page from Django's book and create an identifiable
# string/bytes type.
if python_version < 3:  # kept for reference
    from StringIO import StringIO
    crunchy_bytes = str
else:
    from io import StringIO
    crunchy_bytes = bytes

# Some special functions, specific to a given
# Python version are defined below
import src.tools_2k as tools
u_print = tools.u_print
u_join = tools.u_join
exec_code = tools.exec_code

# Rather than having various modules importing the configuration.py,
# CrunchyPlugin.py, etc.,
# we will set things up so that the relevant will populate the
# following dictionary when it is loaded; however, it will be possible
# to artificially populate it as well from other sources enabling
# independent unit testing.

accounts = {}  # initialized in crunchy.py
additional_vlam = {}  # initialized from plugins by CrunchyPlugin.py
additional_menu_items = {}
additional_properties = {}  # initialized by various plugins
names = {}
config = {}  # initialized mostly by configuration.py
plugin = {}  # initialized by CrunchyPlugin.py
preprocessor = {} # initialized via CrunchyPlugin.py
server = {}  # initialized by pluginloader.py
translate = {} # initialized below
exams = {}  #used by pluging exam_mode.py and vlam_doctest.py
from_comet = {} # initialized from cometIO.py

def get_base_dir():
    path = os.path.normpath(os.path.join(os.path.dirname(__file__),
                                         '..'))
    # Python 3: normpath() decodes by default into a string.
    if isinstance(path, unicode):
        return path
    return path.decode(sys.getfilesystemencoding())

config['crunchy_base_dir'] = get_base_dir()

import src.translation
translate['_'] = src.translation._
translate['init_translation'] = src.translation.init_translation

from src.debug import debug
def debug_msg(data):
    """write a debug message, debug messages always appear on stderr"""
    if data is None:
        data = 'None'
    sys.__stderr__.write(data)
    sys.__stderr__.write("\n")

# We use ElementTree, if possible as ElementSoup in combination with
# BeautifulSoup, in order to parse and process files.

ElementTree = None
# ElementTree is part of Python as of version 2.5;
# however, HTMLTreeBuilder is not included in 2.5
# (but another version of parse is included)
# Nonetheless, we use a customized version.  We might be able to simply
# redefine a method or two ... but we'll use the one we customized for now.

from src.element_tree import ElementTree, HTMLTreeBuilder
parse = HTMLTreeBuilder.parse
Element = ElementTree.Element
SubElement = ElementTree.SubElement
fromstring = ElementTree.fromstring
tostring = ElementTree.tostring

interactive = False # used with python crunchy -i option

import pygments.token
generic_output = pygments.token.STANDARD_TYPES[pygments.token.Generic.Output]
generic_traceback = pygments.token.STANDARD_TYPES[pygments.token.Generic.Traceback]
generic_prompt = pygments.token.STANDARD_TYPES[pygments.token.Generic.Prompt]
comment = pygments.token.STANDARD_TYPES[pygments.token.Comment]
