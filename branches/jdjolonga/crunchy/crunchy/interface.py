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
python_version = sys.version_info[0] + sys.version_info[1]/10.0

# StringIO is used for creating in-memory files
# We also take a page from Django's book and create an identifiable
# string/bytes type.
if python_version < 3:  # kept for reference
    from StringIO import StringIO
    crunchy_bytes = str
    crunchy_unicode = unicode
else:
    from io import StringIO
    crunchy_bytes = bytes
    crunchy_unicode = str


# Some special functions, specific to a given
# Python version are defined below
import crunchy.tools as tools
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
unknown_user_name = None
last_local_base_url = None
path_info = {}  # see rst_directives plugin

def get_base_dir():
    path = os.path.dirname(__file__)
    # Python 3: normpath() decodes by default into a string.

    if isinstance(path, str):
        return path
    return path.decode(sys.getfilesystemencoding())
config['crunchy_base_dir'] = get_base_dir()
plugin['crunchy_base_dir'] = get_base_dir

import crunchy.translation as translation
translate['_'] = translation._
translate['init_translation'] = translation.init_translation

from crunchy.debug import debug
def debug_msg(data):
    """write a debug message, debug messages always appear on stderr"""
    if data is None:
        data = 'None'
    sys.__stderr__.write(data)
    sys.__stderr__.write("\n")

# We use ElementTree, if possible as ElementSoup in combination with
# BeautifulSoup, in order to parse and process files.
# ElementTree is part of Python as of version 2.5;
# Nonetheless, we use a slightly customized version ... and an even
# more customized one for Python 3.

if python_version < 3:
    from crunchy.element_tree import ElementTree
else:
    from crunchy.element_tree3 import ElementTree

Element = ElementTree.Element
SubElement = ElementTree.SubElement
fromstring = ElementTree.fromstring
tostring = ElementTree.tostring

interactive = False # used with python crunchy -i option

if python_version < 3:
    import pygments.token
    generic_output = pygments.token.STANDARD_TYPES[pygments.token.Generic.Output]
    generic_traceback = pygments.token.STANDARD_TYPES[pygments.token.Generic.Traceback]
    generic_prompt = pygments.token.STANDARD_TYPES[pygments.token.Generic.Prompt]
    comment = pygments.token.STANDARD_TYPES[pygments.token.Comment]
else:
    import pygments3.token
    generic_output = pygments3.token.STANDARD_TYPES[pygments3.token.Generic.Output]
    generic_traceback = pygments3.token.STANDARD_TYPES[pygments3.token.Generic.Traceback]
    generic_prompt = pygments3.token.STANDARD_TYPES[pygments3.token.Generic.Prompt]
    comment = pygments3.token.STANDARD_TYPES[pygments3.token.Comment]
