# -*- coding: utf-8 -*-
"""gets source code or parts thereof automatically from python file.
"""

import inspect

from src.interface import config, plugin, python_version

def register():
    plugin['register_tag_handler']("div", "title", "getsource", get_source)

def get_source(page, elem, uid):
    elem.text = "Plugin was called; vlam = %s" % elem.attrib["title"]

