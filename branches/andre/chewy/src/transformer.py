'''
transformer.py

Takes an html page with VLAMarkup and outputs an
html page with other elements added.

'''
# Python standard library modules
import os
import os.path
import re
import urlparse
import urllib
from StringIO import StringIO
# chewy modules
import errors
import configuration
prefs = configuration.UserPreferences()
from translation import _

# Third party modules - included in crunchy distribution
from element_tree import ElementTree, HTMLTreeBuilder
et = ElementTree

#the DTD to use:
DTD = '<!DOCTYPE html PUBLIC "-//W3C//DTD XHTML 1.0 Strict//EN" "http://www.w3.org/TR/xhtml1/DTD/strict.dtd">\n\n'

DOCTESTS = {}

class VLAMPage(object):
    """Encapsulates a page containing VLAM"""
    #for locally unique IDs
    __ID = -1

    def __init__(self, filehandle, url):
        """all you have to give it is a file path to read from."""
        try:
            self.tree = HTMLTreeBuilder.parse(filehandle)
        except Exception, info:
            raise errors.HTMLTreeBuilderError(url, info)
        self.url = url
        self.head = self.tree.find("head")
        self.body = self.tree.find("body")
        self.textareas = []
        self.process_body()
        self.process_head()

    def process_head(self):
        """set up <head>"""
        self.append_js_file("/src/javascript/custom_alert.js")
        self.insert_css("/src/css/default.css")
        self.insert_css("/src/css/custom_alert.css")
        for style in prefs.styles:
            self.head.append(style)
        meta_lang = et.Element("meta")
        meta_lang.set("http-equiv", "Content-Type")
        meta_lang.set("content", "text/html; charset=utf-8")
        self.head.append(meta_lang)
        return

    def insert_css(self, filename):
        '''Inserts a css file in the <head>.'''
        css = et.Element("link")
        css.set("rel", "stylesheet")
        css.set("href", filename)
        css.set("type", "text/css")
        self.head.insert(0, css)
        return

    def append_js_file(self, filename):
        '''Appends a js file in the <head>.'''
        js = et.Element("script")
        js.set("src", filename)
        js.set("type", "text/javascript")
        js.text = "\n"  # easier to read source
        self.head.append(js)
        return


    def process_body(self):
        """set up <body>"""
        fileinfo = et.Element("span")
        fileinfo.set("class", "fileinfo")
        fileinfo.text = self.url
        self.body.insert(0, fileinfo)
        for span in self.body.getiterator("span"):
            self.process_span(span)
        for pre in self.body.getiterator('pre'):
            self.process_pre(pre)
        self.body.insert(0, prefs.menu)

    def process_span(self, span):
        """Span can be used in Chewy for:
           1. providing a language selection.
        """
        for attrib in span.attrib.items():
            if attrib[0] == 'title':
                id, text, div = self.prepare_element(span)
                if 'choose' in self.vlamcode and 'language' in self.vlamcode:
                    addLanguageSelect(div, text)
        return

    def process_pre(self, pre):
        """process a pre element and decide what to do with it"""
        return
##        for attrib in pre.attrib.items():
##            if attrib[0] == 'title':
##                if 'none' in attrib[1]: # no interactive element
##                    self.vlamcode = pre.attrib['title'].lower()
##                    if pre.text.startswith('\n'):
##                        pre.text = pre.text[1:]
##                    self.style_code(pre, pre.text)
##                elif 'editor' in attrib[1]: # includes "interpreter to editor"
##                    self.substitute_editor(pre)
##                elif 'interpreter' in attrib[1]:
##                    self.substitute_interpreter(pre)
##                elif 'doctest' in attrib[1]:
##                    self.substitute_editor(pre)
##                elif 'canvas' in attrib[1] or 'plot' in attrib[1]:
##                    self.substitute_canvas(pre)

    def prepare_element(self, elem):
        '''Common code for all vlam elements using the "title" tag.
        '''
        self.__ID += 1
        id = 'code' + str(self.__ID)
        if elem.text:
            if elem.text.startswith("\n"):
                elem.text = elem.text[1:]
        text = elem.text
        tail = elem.tail
        self.vlamcode = elem.attrib['title'].lower()
        elem.clear()
        elem.tail = tail
        elem.tag = 'div'
        elem.attrib['id'] = id + "_container"
        return id, text, elem

    def get(self):
        """vlam file: serialise the tree and return it;
           simply returns the file content otherwise.
        """
        fake_file = StringIO()
        fake_file.write(DTD + '\n')
        self.tree.write(fake_file)
        return fake_file.getvalue()


###================
#
# The following are functions used to insert various "vlam elements".
# These are purely ElementTree constructions, without any "vlam logic"
# They are introduced as a possible first step to refactor them into
# separate classes.
###================


def addLanguageSelect(parent, text):
    """Inserts an html selector for languages.

       Language choice in option is a string of the form:
       'en, English; fr, Francais [; etc.]'
    """
    choices = text.split(";")
    form = et.SubElement(parent, "form", method='get',
                         action="/select_language")
    select = et.SubElement(form, "select")
    select.set("name", "language")
    for choice in choices:
        args = choice.split(",")
        opt = et.SubElement(select, "option")
        opt.set("value", args[0].strip())
        opt.text = args[1].strip()
    br = et.SubElement(form, "br")
    inp = et.SubElement(form, "input")
    inp.set("type", "submit")
    inp.set("value", _("Submit language choice"))
    inp.set("class", "crunchy")
    return
