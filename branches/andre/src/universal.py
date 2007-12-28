# -*- coding: utf-8 -*-
'''
universal.py

This file contains references to various functions in a way that it works
regardless of the Python version.

Until we succeed in making Crunchy compatible with both Python 2.x and 3.x,
we keep this file (and tools*) at the top level of the package so that
we can run tests successfully.
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

# Special functions are defined below
if python_version < 3:
    import src.tools_2k as tools
else:
    import src.tools_3k as tools
u_print = tools.u_print
exec_code = tools.exec_code

ElementTree = None
# ElementTree is part of Python as of version 2.5.
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

