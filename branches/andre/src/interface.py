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

import sys
version = sys.version.split('.')
python_version = float(version[0] + '.' + version[1][0])
python_minor_version = version[1][1:3]

# StringIO is used for creating in-memory files
if python_version < 3:
    from StringIO import StringIO
else:
    from io import StringIO

# Some special functions, specific to a given
# Python version are defined below
if python_version < 3:
    import src.tools_2k as tools
else:
    import src.tools_3k as tools
u_print = tools.u_print
exec_code = tools.exec_code


# We use ElementTree, if possible as ElementSoup in combination with
# BeautifulSoup, in order to parse and process files.

ElementTree = None
# ElementTree is part of Python as of version 2.5; however, HTMLTreebuilder
# is not part of the standard distribution - but we may not need to retain it...
# ... this needs to be explored further at a later time.
if python_version == 2.4:
    from src.element_tree import ElementTree, HTMLTreeBuilder
    parse = HTMLTreeBuilder.parse
else:
    from xml.etree import ElementTree
    parse = ElementTree.parse
Element = ElementTree.Element
SubElement = ElementTree.SubElement
fromstring = ElementTree.fromstring
tostring = ElementTree.tostring

# Rather than having various modules importing the configuration one,
# we will set things up so that configuration.py will populate the
# following dictionary when it is loaded; however, it will be possible
# to artificially populate it as well from other sources enabling
# independent unit testing.

config = {}

# In the absence of either HTMLTreeBuilder or, even better,
# ElementSoup/BeautifulSoup in Python 3.x, we provide a basic, but extremely
# strict, x(h)tml parser.

import src.translation
config['_'] = src.translation._

XmlFile = None
if python_version >= 3:
    import src.my_htmlentitydefs
    class XmlFile(ElementTree.ElementTree):
        def __init__(self, file=None):
            ElementTree.ElementTree.__init__(self)
            parser = ElementTree.XMLTreeBuilder(
                target=ElementTree.TreeBuilder(ElementTree.Element))
            ent = src.my_htmlentitydefs.entitydefs
            for entity in ent:
                if entity not in parser.entity:
                    parser.entity[entity] = ent[entity]
            self.parse(source=file, parser=parser)
            return 

