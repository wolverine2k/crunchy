#!/usr/bin/env python
# -*- coding: utf-8 -*-
# Author: André Roberge
# Copyright: This module has been placed in the public domain.

"""
crst2s5.py (or: Crunchy rst2s5.py) is an extension of rst2s5.py, the
minimal front end to the Docutils Publisher, producing HTML slides using
the S5 template system.

It assumes the use of an updated version (1.2a2) of slides.js by Eric Meyer
which allows speaker notes to appear in separate window.
[Actually, in the distribution, we include a customized version of slides.js
so that it could work better for our purpose.]

Special Crunchy directives are also available.
"""
# There were three possible approaches to create crst2s5:
# 1. Fork the docutils distribution, make the small changes required to
#    the existing files so that crst2s5.py would essentially be identical
#    to rst2s5.py.   Doing so would mean having folks install essentially
#    two copies of (some parts of) docutils, which seems a bit of a waste.
#
# 2. Use the approach mentioned in 1. above, and use it to create a patch
#    that would be submitted to the docutils developers, and wait with
#    fingers crossed for their approval.
#
# 3. Create a messy hack which relies on the presence of docutils.  This means
#    less file to be distributed and, if the docutils developers are interested,
#    it should be fairly simple to port back the changes into the docutils
#    trunk.  This is the approach we have chosen.

import sys

try:
    import locale
    locale.setlocale(locale.LC_ALL, '')
except:
    pass

from os import linesep
from docutils.core import publish_cmdline, default_description
from docutils.writers import s5_html, html4css1
from docutils.parsers import rst
from docutils.writers.html4css1 import HTMLTranslator
from docutils import nodes

description = ('Generates S5 (X)HTML slideshow documents from standalone '
               'reStructuredText sources.  ' + default_description)


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
        content = linesep.join(self.content)
        listOut = [ x.strip() for x in self.arguments]
        titleAttr = " ".join(listOut)
        return [ crunchy(title=titleAttr, text=content, CLASS="crunchy_widget") ]

class GetPythonSourceDirective(rst.Directive):
    required_arguments = 1
    optional_arguments = 20  # make sure we have enough!
    final_argument_whitespace = False
    has_content = True
    def run(self):
        content = linesep.join(self.content)
        listOut = [ x.strip() for x in ['getsource'] + self.arguments]
        titleAttr = " ".join(listOut)
        return [ getpythonsource(title=titleAttr, text=content, CLASS="crunchy_widget") ]

class CrunchySlideTranslator(s5_html.S5HTMLTranslator):
    def __init__(self, *args):
        s5_html.S5HTMLTranslator.__init__(self, *args)
        meta = '<meta name="true generator" content="crst2s5.py pre-alpha"/>\n'
        self.meta.append(meta)
        self.head.append(meta)
        meta = '<meta name="true version" content="S5 1.2a modified"/>\n'
        self.meta.append(meta)
        self.head.append(meta)

    def visit_crunchy(self, node):
        attrDict = {}
        for key, value in list(node.attributes.items()):
            if value and (key is not "xml:space"):
                attrDict[key] = value
        self.body.append(self.starttag(node, 'pre', **attrDict))

    def depart_crunchy(self, node):
        self.body.append('\n</pre>\n')

    def visit_getpythonsource(self, node):
        attrDict = {}
        for key, value in list(node.attributes.items()):
            if value and (key is not "xml:space"):
                attrDict[key] = value
        self.body.append(self.starttag(node, 'pre', **attrDict))

    def depart_getpythonsource(self, node):
        self.body.append('\n</pre>\n')

rst.directives.register_directive('crunchy', CrunchyDirective)
rst.directives.register_directive('getpythonsource', GetPythonSourceDirective)

class CrunchySlideWriter(s5_html.Writer):
    def __init__(self):
        html4css1.Writer.__init__(self)
        self.translator_class = CrunchySlideTranslator

def main():
    source = sys.argv[-2]
    destination = sys.argv[-1]
    writer = CrunchySlideWriter()
    publish_cmdline(writer=writer, description=description)

if __name__ == '__main__':
    if ((len(sys.argv) == 2 and sys.argv[1] in ['-h', '--help'])
        or (
            len(sys.argv) >= 3 and not sys.argv[-1].startswith("-")
            and not sys.argv[-2].startswith("-")
           )
       ):
        main()
    else:
        print("You must specify files as both source and destination.")