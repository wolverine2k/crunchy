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
if python_version < 3:  # kept for reference
    from StringIO import StringIO
else:
    from io import StringIO

# Some special functions, specific to a given
# Python version are defined below
import src.tools_2k as tools
u_print = tools.u_print
exec_code = tools.exec_code


# Rather than having various modules importing the configuration.py,
# CrunchyPlugin.py, etc.,
# we will set things up so that the relevant will populate the
# following dictionary when it is loaded; however, it will be possible
# to artificially populate it as well from other sources enabling
# independent unit testing.

config = {}  # initialized mostly by configuration.py
plugin = {}  # initialized by CrunchyPlugin.py
preprocessor = {} # initialized via CrunchyPlugin.py
server = {}  # initialized by pluginloader.py
translate = {} # initialized below
from_comet = {} # initialized from cometIO.py

config['crunchy_base_dir'] = os.path.dirname(imp.find_module("crunchy")[1]
    ).decode(sys.getfilesystemencoding())

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
