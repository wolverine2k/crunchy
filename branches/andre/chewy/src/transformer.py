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
DTD = '<!DOCTYPE html PUBLIC "-//W3C//DTD XHTML 1.0 Strict//EN" '\
'"http://www.w3.org/TR/xhtml1/DTD/strict.dtd">\n\n'

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
            # note: we need the uid information for updating *before* we
            # start processing the pre, unlike in the original crunchy
            # where the uid was assigned after.
            self.__ID += 1
            self.uid = 'code' + str(self.__ID)
            self.process_pre(pre)
        self.body.insert(0, prefs.menu)
        self.body.append(update_button())

    def process_span(self, span):
        """Span can be used in Chewy for:
           1. providing a language selection.
        """
        for attrib in span.attrib.items():
            if attrib[0] == 'title':
                text, div = self.prepare_element(span)
                if 'choose' in self.vlamcode and 'language' in self.vlamcode:
                    addLanguageSelect(div, text)
        return

    def process_pre(self, pre):
        """process a pre element and insert the required html controls
           to select the appropriate vlam options"""
        if 'title' in pre.attrib:
            title = pre.attrib['title']
        else:
            title = ''
        assigned = analyze_vlam_code(title)
        text, new_div = self.prepare_element(pre)
        heading = et.SubElement(new_div, 'h3')
        if title:
            heading.text = '<pre title="%s">'%title
        else:
            heading.text = "<pre>"
        new_pre = et.SubElement(new_div, 'pre')
        new_pre.text = text
        addVLAM(new_div, self.uid, assigned)
        return

    def prepare_element(self, elem):
        '''Replaces an element by a <div> as a container
        '''
        if elem.text:
            if elem.text.startswith("\n"):
                elem.text = elem.text[1:]
        text = elem.text
        tail = elem.tail
        original_tag = elem.tag
        elem.clear()
        elem.tail = tail
        elem.tag = 'div'
        if original_tag == 'pre':
            elem.attrib['id'] = self.uid + "_container"
        return text, elem

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
        args = self.args.split(';')
        # build a dict from alternating values (Thank you Python Cookbook)
        changes = dict(zip(args[::2], args[1::2]))
        if self.uid in changes:
            pre.attrib['title'] = changes[self.uid]
        VLAMPage.process_pre(self, pre)

###================

def analyze_vlam_code(vlam):
    """ Parse the vlam code to analyze its content.
        The allowed values are:
        1. none [interpreter] [linenumber]
        2. interpreter [linenumber]
        3. interpreter to editor [linenumber] [size=(rows, cols)] [no-copy]
        4. editor [linenumber] [size=(rows, cols)] [no-copy _or_ no-pre]
                [external console [no-internal]] _or_ [external [no-internal]]
        5. doctest [linenumber] [size=(rows, cols)]
        6. canvas [linenumber] [size=(rows, cols)] [no-copy _or_ no-pre]
                                [area=(width, height)]
        7. plot [linenumber] [size=(rows, cols)] [no-copy _or_ no-pre]
                                [area=(width, height)]
    """
    values = {
    'interactive': '', # default values to return in case someone made an error
    'linenumber': '',       # in a file marked up "by hand".
    'size': '',
    'area': '',
    'execution': '',
    'copied': '',
    }
    vlam = vlam.lower() # in case it was done by hand

    if 'none' in vlam:
        values['interactive'] = 'none'
        if 'interpreter' in vlam:
            values['linenumber'] = ' interpreter'
        if 'linenumber' in vlam:
            values['linenumber'] += ' linenumber'
    elif 'interpreter' in vlam and 'editor' in vlam:
        values['interactive'] = 'interpreter to editor'
        if 'linenumber' in vlam:
            values['linenumber'] = ' linenumber'
        if 'size' in vlam:
            rows, cols = _get_size(vlam)
            values['size'] = {'rows':rows, 'cols':cols}
        if 'no-copy' in vlam:
            values['copied'] = 'no-copy'
    else:
        for choice in ['none', 'interpreter', 'editor', 'doctest',
                       'canvas', 'plot']:
            if choice in vlam:
                values['interactive'] = choice
                if 'linenumber' in vlam:
                    values['linenumber'] = ' linenumber'
                if choice not in ['none', 'interpreter']:
                    if 'size' in vlam:
                        rows, cols = _get_size(vlam)
                        values['size'] = {'rows':rows, 'cols':cols}
                if choice in ['canvas', 'plot']:
                    if 'area' in vlam:
                        width, height = _get_area(vlam)
                        values['area'] = {'width':width, 'height':height}
                if choice == 'editor':
                    if 'external' in vlam:
                        values['execution'] = 'external'
                        if 'console' in vlam:
                            values['execution'] += ' console'
                        if 'no-internal' in vlam:
                            values['execution'] += ' no-internal'
                if choice in ['editor', 'canvas', 'plot']:
                    if 'no-copy' in vlam:
                        values['copied'] = 'no-copy'
                    elif 'no-pre' in vlam:
                        values['copied'] = 'no-pre'
    return values

def _get_size(vlam):
    ''' Extract the default size of the textarea'''
    if 'size' in vlam:
        try:
            res = re.search(r'size\s*=\s*\((.+?),(.+?)\)', vlam)
            rows = int(res.groups()[0])
            cols = int(res.groups()[1])
        except:
            rows, cols = 10, 80
    else:
        rows, cols = 10, 80
    return rows, cols

def _get_area(vlam):
    ''' Extract the drawing canvas dimensions'''
    if 'area' in vlam:
        try:
            res = re.search(r'area=\((.+?),(.+?)\)', vlam)
            width = int(res.groups()[0])
            height = int(res.groups()[1])
        except:
            width, height = 400, 400
    else:
        width, height = 400, 400
    return width, height


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

def update_button():
    button = et.Element('button', onclick="update();")
    button.text = _("Update")
    return button


def addVLAM(parent, uid, pre_assigned):
    '''Intended to add the various vlam options under a <pre>'''
    table = et.SubElement(parent, 'table')
    table.attrib["class"] = "vlam"
    tr = et.SubElement(table, 'tr')
    # first column: interactive elements
    td1 = et.SubElement(tr, 'td', style='vertical-align:top;')
    form1 = et.SubElement(td1, 'form')
    fs1 = et.SubElement(form1, 'fieldset')
    legend1 = et.SubElement(fs1, 'legend')
    legend1.text = _("Interactive element")
    for type in ['none', 'interpreter', 'interpreter to editor',
                  'editor', 'doctest', 'canvas', 'plot']:
        inp = et.SubElement(fs1, 'input', type='radio', name=uid,
                              value=type)
        inp.text = type
        if type == pre_assigned['interactive']:
            inp.attrib['checked'] = 'checked'
        br = et.SubElement(fs1, 'br')
    # 2nd column, top: line number choices
    td2 = et.SubElement(tr, 'td', style='vertical-align:top;')
    form2 = et.SubElement(td2, 'form')
    fs2 = et.SubElement(form2, 'fieldset')
    legend2 = et.SubElement(fs2, 'legend')
    legend2.text = _("Optional line numbering")
    for type in ['linenumber', 't', 'interpreter', 'interpreter linenumber']:
        if type == 't':
            note = et.SubElement(fs2, 'small')
            note.text = _("If interactive element is none:")
        else:
            inp = et.SubElement(fs2, 'input', type='radio', name=uid,
                                  value=type)
            inp.text = type
            if type == pre_assigned['linenumber'].strip():
                inp.attrib['checked'] = 'checked'
        br = et.SubElement(fs2, 'br')
    # 2nd column, bottom: size and area
    form3 = et.SubElement(td2, 'form')
    fs3 = et.SubElement(form3, 'fieldset')
    legend3 = et.SubElement(fs3, 'legend')
    legend3.text = _("Size")
    note = et.SubElement(fs3, 'small')
    note.text = _("Size of editor (if present)")
    br = et.SubElement(fs3, 'br')
    for type in ['rows', 'cols']:
        note = et.SubElement(fs3, 'tt')
        note.text = type + ":"
        inp = et.SubElement(fs3, 'input', type='text', name=uid, value='')
        if type in pre_assigned['size']:
            inp.attrib['value'] = "%d"%pre_assigned['size'][type]
        br = et.SubElement(fs3, 'br')
    note = et.SubElement(fs3, 'small')
    note.text = _("Drawing area (if present)")
    br = et.SubElement(fs3, 'br')
    for type in ['width ', 'height']:  # extra space in 'width ' for alignment
        note = et.SubElement(fs3, 'tt')
        note.text = type + ":"
        inp = et.SubElement(fs3, 'input', type='text', name=uid, value='')
        if type.strip() in pre_assigned['area']:
            inp.attrib['value'] = "%d"%pre_assigned['area'][type.strip()]
        br = et.SubElement(fs3, 'br')
    # 3rd column, top: Code execution options
    td4 = et.SubElement(tr, 'td', style='vertical-align:top;')
    form4 = et.SubElement(td4, 'form')
    fs4 = et.SubElement(form4, 'fieldset')
    legend4 = et.SubElement(fs4, 'legend')
    legend4.text = _("Code execution")
    note = et.SubElement(fs4, 'small')
    note.text = _("Optional values for editor only")
    br = et.SubElement(fs4, 'br')
    for type in ['external', 'external no-internal', 'external console',
                 'external console no-internal']:
        inp = et.SubElement(fs4, 'input', type='radio', name=uid,
                              value=type)
        inp.text = type
        if type == pre_assigned['execution']:
            inp.attrib['checked'] = 'checked'
        br = et.SubElement(fs4, 'br')
    # 3rd column, bottom: Code copying options
    form5 = et.SubElement(td4, 'form')
    fs5 = et.SubElement(form5, 'fieldset')
    legend5 = et.SubElement(fs5, 'legend')
    legend5.text = _("Rarely used options")
    note = et.SubElement(fs5, 'small')
    note.text = _("Code not copied in editor")
    br = et.SubElement(fs5, 'br')
    note = et.SubElement(fs5, 'small')
    note.text = _("- done automatically for doctest")
    br = et.SubElement(fs5, 'br')
    inp = et.SubElement(fs5, 'input', type='radio', name=uid,
                          value='no-copy')
    inp.text = 'no-copy'
    if 'no-copy' == pre_assigned['copied']:
        inp.attrib['checked'] = 'checked'
    br = et.SubElement(fs5, 'br')
    note = et.SubElement(fs5, 'small')
    note.text = _("Code not appearing in <pre>")
    br = et.SubElement(fs5, 'br')
    note = et.SubElement(fs5, 'small')
    note.text = _("- incompatible with no-copy")
    br = et.SubElement(fs5, 'br')
    inp = et.SubElement(fs5, 'input', type='radio', name=uid,
                          value='no-pre')
    inp.text = 'no-pre'
    if 'no-pre' == pre_assigned['copied']:
        inp.attrib['checked'] = 'checked'
    br = et.SubElement(fs5, 'br')
    #button = et.SubElement(parent, 'button', onclick="update();")
    button = et.SubElement(parent, 'button', onclick="record('%s');"%uid)
    button.text = _("Record changes")
    return
