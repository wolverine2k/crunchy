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
            self.tree = HTMLTreeBuilder.parse(filehandle, encoding='utf-8')
            filehandle.close()
        except Exception, info:
            raise errors.HTMLTreeBuilderError(url, info)
        self.url = url
        self.convert_all_links()
        self.head = self.tree.find("head")
        self.body = self.tree.find("body")
        self.textareas = []
        self.process_body()
        self.process_head()

    def process_head(self):
        """set up <head>"""
        self.append_js_file("/src/javascript/custom_alert.js")
        self.append_js_file("/src/javascript/chewy.js")
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
        """process a pre element and insert the required html controls
           to select the appropriate vlam options"""
        id, text, new_div = self.prepare_element(pre)
        new_pre = et.SubElement(new_div, 'pre')
        new_pre.text = text
        addVLAM(new_div, id)
        return

    def prepare_element(self, elem):
        '''Replaces an element by a <div> as a container
        '''
        self.__ID += 1
        id = 'code' + str(self.__ID)
        if elem.text:
            if elem.text.startswith("\n"):
                elem.text = elem.text[1:]
        text = elem.text
        tail = elem.tail
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
        self.tree.write(fake_file, encoding='utf-8')
        return fake_file.getvalue()

    def convert_all_links(self):
        """looks for any attribute anywhere in the document, called
           'src' or 'href' and converts it if it's a relative link -
            absolute links (starting with http://) are left alone.
            In future this might be user-configurable, the user could be able
            to specify whether or not external links are loaded as vlam
            It might also be desirable if tutorial writers could specify
            a preference too.
        """
        for elem in self.tree.getiterator():
            if 'src' in elem.attrib:
                e = elem.attrib['src']
                if not 'http://' in e:
                    elem.attrib['src'] = '/load_local?path=' +\
                           urllib.quote_plus(os.path.join(self.url, e))
            elif 'href' in elem.attrib:
                e = elem.attrib['href']
                if not 'http://' in e:
                    if e.startswith('#'):
                        pass # the browser will handle these "as is"
                    else:
                        elem.attrib['href'] = '/load_local?path=' +\
                           urllib.quote_plus(os.path.join(self.url, e))

class VLAMUpdater(VLAMPage):
    def __init__(self, filehandle, url, args):
        self.args = args
        VLAMPage.__init__(self, filehandle, url)

    def process_pre(self, pre):
        pre.attrib['title'] = self.args

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

def addVLAM(parent, id):
    '''Intended to add the various vlam options under a <pre>'''
    form = et.SubElement(parent, 'form')
    table = et.SubElement(form, 'table')
    table.attrib["class"] = "vlam"
    tr = et.SubElement(table, 'tr')
    # first column: interactive elements
    td1 = et.SubElement(tr, 'td')
    fs1 = et.SubElement(td1, 'fieldset')
    legend1 = et.SubElement(fs1, 'legend')
    legend1.text = _("Interactive elements")
    input1 = et.SubElement(fs1, 'input', type='radio', name=id,
                            value="none", checked='')
    input1.text = "none"
    br = et.SubElement(fs1, 'br')
    input2 = et.SubElement(fs1, 'input', type='radio', name=id,
                            value="interpreter")
    input2.text = "interpreter"
    br = et.SubElement(fs1, 'br')
    input3 = et.SubElement(fs1, 'input', type='radio', name=id,
                            value="interpreter editor")
    input3.text = "interpreter to editor"
    br = et.SubElement(fs1, 'br')
    input4 = et.SubElement(fs1, 'input', type='radio', name=id,
                            value="editor")
    input4.text = "editor"
    br = et.SubElement(fs1, 'br')
    input5 = et.SubElement(fs1, 'input', type='radio', name=id,
                            value="doctest")
    input5.text = "doctest"
    br = et.SubElement(fs1, 'br')
    input6 = et.SubElement(fs1, 'input', type='radio', name=id,
                            value="canvas")
    input6.text = "canvas"
    br = et.SubElement(fs1, 'br')
    input7 = et.SubElement(fs1, 'input', type='radio', name=id,
                            value="plot")
    input7.text = "plot"
    # 2nd column: line number choices
    td2 = et.SubElement(tr, 'td')
    fs2 = et.SubElement(td2, 'fieldset')
    legend2 = et.SubElement(fs2, 'legend')
    legend2.text = _("Line numbers")
    input21 = et.SubElement(fs2, 'input', type='radio', name=id,
                            value="", checked='')
    input21.text = "No linenumbers"
    br = et.SubElement(fs2, 'br')
    input22 = et.SubElement(fs2, 'input', type='radio', name=id,
                            value="linenumber")
    input22.text = "With linenumbers"
    # 3rd column: code options
    td3 = et.SubElement(tr, 'td')
    fs3 = et.SubElement(td3, 'fieldset')
    legend3 = et.SubElement(fs3, 'legend')
    legend3.text = _("Code options")
    input31 = et.SubElement(fs3, 'input', type='radio', name=id,
                            value="", checked='')
    input31.text = "Default"
    br = et.SubElement(fs3, 'br')
    input32 = et.SubElement(fs3, 'input', type='radio', name=id,
                            value="no-pre")
    input32.text = "no-pre"
    br = et.SubElement(fs3, 'br')
    input33 = et.SubElement(fs3, 'input', type='radio', name=id,
                            value="no-copy")
    input33.text = "no-copy"
    button = et.SubElement(parent, 'button', onclick="update();")
    button.text = id
##    updater_link = et.SubElement(parent, 'a', href="/update?id=%s"%id)
##    updater_link.text = id
    return
