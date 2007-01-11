'''
crunchyfier.py

Takes an html page with VLAMarkup and outputs an
html page with interactive (and other) elements added.

'''
# Python standard library modules
import mimetools
import os
import os.path
import re
import urlparse
import urllib
from StringIO import StringIO
# crunchy modules
import interpreters
import errors
import colourize
import configuration
prefs = configuration.UserPreferences()
import security
from translation import _

# Third party modules - included in crunchy distribution
from element_tree import ElementTree, HTMLTreeBuilder
et = ElementTree

#the DTD to use:
DTD = '<!DOCTYPE html PUBLIC "-//W3C//DTD XHTML 1.0 Strict//EN" '\
'"http://www.w3.org/TR/xhtml1/DTD/strict.dtd">\n\n'
DOCTESTS = {}

# Some javascript code
editAreaLoader = """
editAreaLoader.init({
id: %s,
font_size: "11",
allow_resize: "both",
allow_toggle: true,
language: "%s",
toolbar: "new_document, save, load, |, fullscreen, |, search, go_to_line, |, undo, redo, |, select_font, |, change_smooth_selection, highlight, reset_highlight, |, help",
syntax: "python",
start_highlight: true,
load_callback:"my_load_file",
save_callback:"my_save_file",
display: "later",
replace_tab_by_spaces:4,
min_height: 150});"""

editArea_load_and_save = """
function my_load_file(id){
var obj = document.getElementById('hidden_load'+id);
obj.style.visibility = "visible";
}
function my_save_file(id){
var obj = document.getElementById('hidden_save'+id);
obj.style.visibility = "visible";
}
"""


class TreeBuilder(object):
    """Base class used to build a tree from a filehandle pointing to a
       well formed html file.
    """
    def __init__(self, filehandle, url):
        """all you have to give it is a file handle to read from and an url."""
        try:
            # We let HTMLTreeBuilder figure out the encoding on its own
            # as it can do it very well.  This does create one limitation:
            # the encoding has to be an ascii-compatible encoding.
            self.tree = HTMLTreeBuilder.parse(filehandle)
        except Exception, info:
            raise errors.HTMLTreeBuilderError(url, info)
        # We retrieve the encoding so that we can use it if needed
        # when interacting between an html page and the local file system.
        # This will also allow us to reinsert it when writing the file,
        # if needed
        self.get_encoding()
        self.url = url
        # unique id for interactive elements
        self._ID = -1
        return

    def get_encoding(self):
        """retrieves the encoding from a well-formed tree;
           assumes iso-8859-1 if none found.
        """
        self.encoding = 'iso-8859-1'
        for meta in self.tree.getiterator("meta"):
            http_equiv = content = None
            for attrib in meta.attrib.items():
                if attrib[0] == 'http-equiv':
                    http_equiv = attrib[1]
                elif attrib[0] == 'content':
                    content = attrib[1]
            if http_equiv == "content-type" and content:
            # use mimetools to parse the http header
            # (copied from HTMLTreeBuilder)
                header = mimetools.Message(
                    StringIO.StringIO("%s: %s\n\n" % (http_equiv, content))
                    )
                encoding = header.getparam("charset")
                if encoding:
                    self.encoding = encoding
        return

    def get(self):
        """vlam file: serialise the tree and return it;
           simply returns the file content otherwise.
        """
        fake_file = StringIO()
        fake_file.write(DTD + '\n')
        # use the "private" _write() instead of write() as the latter
        # will add a redundant <xml ...> statement unless the
        # encoding is utf-8 or ascii.
        self.tree._write(fake_file, self.tree._root, self.encoding, {})
        return fake_file.getvalue()

class VLAMPage(TreeBuilder):
    """Encapsulates a page containing VLAM"""
    def __init__(self, filehandle, url, external_flag=False, local_flag=False):
        TreeBuilder.__init__(self, filehandle, url)

        # The security module removes all kinds of potential security holes
        # including some meta tags with an 'http-equiv' attribute.
        self.tree = security.remove_unwanted(self.tree)
        self.get_base()
        # If self.external_flag or self.local_flag is True, which means
        # that the original page was loaded via an input box
        # (/load_local or /load_external)
        # all links in the page are converted to use the same
        self.external_flag = external_flag
        self.local_flag = local_flag
        if self.external_flag or self.local_flag:
            self.convert_all_links()
        self.colourizer = colourize.Colourizer()
        self.head = self.tree.find("head")
        self.body = self.tree.find("body")
        self.textareas = []
        self.process_body()
        self.process_head()

    def process_head(self):
        """set up <head>"""
        if self.textareas:
            # we want edit_area_full.js to be loaded first
            self.append_js_file("/src/javascript/edit_area/edit_area_crunchy.js")
        self.append_js_file(security.commands['/get_user_js'])
        self.append_js_file("/src/javascript/custom_alert.js")
        if self.textareas:
            for id in self.textareas:
                self.append_editarea_script(id)
            self.add_editarea_add_callbacks()
        self.insert_css("/src/css/default.css")
        self.insert_css("/src/css/custom_alert.css")
        for style in prefs.styles:
            self.head.append(style)
        # reinsert the encoding information that was removed.
        meta_lang = et.Element("meta")
        meta_lang.set("http-equiv", "Content-Type")
        meta_lang.set("content", "text/html; charset=%s"%self.encoding)
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

    def append_editarea_script(self, id):
        '''Appends a js script for each editarea/textarea'''
        js = et.Element("script")
        js.set("type", "text/javascript")
        # editAreaLoader is defined near the top of this file
        js.text = editAreaLoader%(id, prefs.editarea_language)
        self.head.append(js)
        return

    def add_editarea_add_callbacks(self):
        '''Appends the EditArea call back functions to enable saving and
           loading programs from the editor.  Actually, these function only
           trigger the visibility of the required <form> elements that do
           the actual work.
        '''
        js = et.Element("script")
        js.set("type", "text/javascript")
        # editArea_load_and_save is defined near the top of this file
        js.text = editArea_load_and_save
        self.head.append(js)
        return

    def process_body(self):
        """set up <body>"""
        self.body.attrib['spellcheck'] = 'false' # turn off Firefox spell check
        fileinfo = et.Element("span")            # in all <textarea> & <input>
        fileinfo.set("class", "fileinfo")
        fileinfo.text = self.url
        self.body.insert(0, fileinfo)
        for span in self.body.getiterator("span"):
            self.process_span(span)
        for pre in self.body.getiterator('pre'):
            self.process_pre(pre)
        self.body.insert(0, prefs.menu)

    def process_span(self, span):
        """Span can be used for:
           1. hiding comments,
           2. requesting to load local or remote Crunchy tutorials,
              possibly for editing them (only local ones), or
           3. providing a language selection.
        """
        for attrib in span.attrib.items():
            if attrib[0] == 'class':
                if 'vlam_comment' in attrib[1].lower():
                    text = span.text
                    tail = span.tail
                    span.clear()
                    span.tag = 'span'
                    span.set("class", 'crunchy_comment')
                    span.text = text
                    span.tail = tail
            elif attrib[0] == 'title':
                id, text, div = self.prepare_element(span)
                if 'load' in self.vlamcode:
                    if 'local' in self.vlamcode:
                        addLoadLocal(div)
                    elif 'remote' in self.vlamcode:
                        addLoadRemote(div, text)
                elif 'choose' in self.vlamcode and 'language' in self.vlamcode:
                    addLanguageSelect(div, text)
                elif 'edit' in self.vlamcode and 'tutorial' in self.vlamcode:
                    addLoadForEdit(div, text)
        return

    def process_pre(self, pre):
        """process a pre element and decide what to do with it"""
        if 'title' not in pre.attrib:
            id, text, new_div = self.prepare_element(pre)
            title = ''
            pre_heading = "%s <pre>"%_("Previous value")
            assigned = analyze_vlam_code(title)
            new_pre = et.SubElement(new_div, 'pre')
            new_pre.text = text
        else:
            title = pre.attrib['title'].lower()
            assigned = analyze_vlam_code(title)
            id, text, new_div = self.prepare_element(pre)
            self.python_code = text
            pre_heading = '%s <pre title="%s">'%(_("Previous value"), title)
            self.vlamcode = title# reconstruct(title)
            if 'none' in assigned['interactive']: # no interactive element
                self.style_code(pre, pre.text)
            elif 'editor' in assigned['interactive']: # includes "interpreter to editor"
                self.substitute_editor(new_div, id, text)
            elif 'interpreter' in assigned['interactive']:
                self.substitute_interpreter(new_div, id, text)
            elif 'doctest' in assigned['interactive']:
                self.substitute_editor(new_div, id, text)
            elif 'canvas' in assigned['interactive'] or\
                 'plot' in assigned['interactive']:
                self.substitute_canvas(new_div, id, text)
        addVLAM(new_div, id, assigned, pre_heading)

    def prepare_element(self, elem):
        '''Common code for all vlam elements using the "title" tag.
        '''
        self._ID += 1
        id = 'code' + str(self._ID)
        if elem.text:
            if elem.text.startswith("\n"):
                elem.text = elem.text[1:]
        text = elem.text
        tail = elem.tail
        # new from chewy
        if 'title' in elem.attrib:
            self.vlamcode = elem.attrib['title'].lower()
        elem.clear()
        elem.tail = tail
        elem.tag = 'div'
        elem.attrib['id'] = id + "_container"
        # temporary Kludge for chewy
        self.new_div = elem
        self.uid = id
        return id, text, elem

    def substitute_interpreter(self, elem, id, text):
        """substitute an interpreter for elem"""
        #self.interpreter_present = True
        elem.attrib['class'] = "interpreter"
        #container for the example code:
        pre = et.SubElement(elem, 'pre')
        if text:
            self.style_code(pre, text)
        output = et.SubElement(elem, 'pre', id=id+'_output_container')
        output.attrib['class'] = "interp_output_container"
        output.text = '\n' # a single space would push the first "output" prompt right
        prompt = et.SubElement(elem, "span", id=id+"_prompt")
        prompt.attrib['class'] = "stdin"
        prompt.text = ">>> "
        input = et.SubElement(elem, "input", type="text", id=id+"_input", onkeyup='interp_trapkeys(event, "'+id+'")')
        input.attrib['class'] = "interp_input"
        interpreters.interps[id] = interpreters.HTTPrepl()
        tipbar = et.SubElement(self.body, "div", id=id+"_tipbar")
        tipbar.attrib['class'] = "interp_tipbar"
        tipbar.text = " "

    def substitute_editor(self, elem, id, text):
        """Substitutes an editor for elem.  It is used for 'editor', 'doctest',
           as well as 'interpreter to editor' options."""
        global DOCTESTS

        pre = et.SubElement(elem, 'pre')
        textarea_text = self._apportion_code(pre, text)
        textarea_id = id+"_code"
        self.textareas.append('\"'+textarea_id+'\"')

        rows, cols = self._get_size()
        textarea = et.SubElement(elem, "textarea", rows=rows, cols=cols,
                                 id=textarea_id)
        textarea.text = textarea_text
        add_hidden_load_and_save(elem, id, textarea_id, "_code")

        if 'external' in self.vlamcode:
            if not 'no-internal' in self.vlamcode:
                btn = et.SubElement(elem, "button",
                                    onclick='exec_by_id("'+id+'")')
                btn.text = _("Evaluate")
            if 'console' in self.vlamcode:
                btn2 = et.SubElement(elem, "button",
                                     onclick='exec_external_console("'+id+'")')
            else:
                btn2 = et.SubElement(elem, "button",
                                             onclick='exec_external("'+id+'")')
            btn2.text = _("Execute externally")
        else:
            btn = et.SubElement(elem, "button", onclick='exec_by_id("'+id+'")')
            btn.text = _("Evaluate")
        out = et.SubElement(elem, "pre", id=id+"_output")
        out.text = ' '
        out.attrib['class'] = 'term_out'
        if 'doctest' in self.vlamcode:
            btn.attrib['onclick'] = 'doctest_by_id("'+id+'")'
            DOCTESTS[id] = text
            out.attrib['class'] = 'doctest_out'
        return

    def substitute_canvas(self, new_div, id, text):
        """substitute a canvas for elem"""
        rows, cols = self._get_size()
        width, height = self._get_area()
        if 'canvas' in self.vlamcode:
            id = "canvas%s_%s"%(width, height) + id
            klass = 'canvas'
            btn_text = _("Draw")
        else:
            id = "plot%s_%s"%(width, height) + id
            klass = 'plot'
            btn_text = _("Plot")

        pre = et.SubElement(new_div, 'pre')
        textarea_text = self._apportion_code(pre, text)
        textarea_id = id+"_input"
        self.textareas.append('\"'+textarea_id+'\"')
        add_hidden_load_and_save(new_div, id, textarea_id, "_input")

        addCanvas(new_div, width=width, height=height, id=id, klass=klass,
                  btn_text=btn_text, rows=rows, cols=cols,
                  textarea_id=textarea_id, textarea_text=textarea_text)
        return

    def _get_size(self):
        ''' Extract the default size of the textarea'''
        if 'size' in self.vlamcode:
            try:
                res = re.search(r'size\s*=\s*\((.+?),(.+?)\)', self.vlamcode)
                rows = int(res.groups()[0])
                cols = int(res.groups()[1])
            except:
                rows, cols = 10, 80
        else:
            rows, cols = 10, 80
        return str(rows), str(cols)

    def _get_area(self):
        ''' Extract the drawing canvas dimensions'''
        if 'area' in self.vlamcode:
            try:
                res = re.search(r'area=\((.+?),(.+?)\)', self.vlamcode)
                width = int(res.groups()[0])
                height = int(res.groups()[1])
            except:
                width, height = 400, 400
        else:
            width, height = 400, 400
        return str(width), str(height)

    def _apportion_code(self, pre, code):
        '''Decide on what code (if any) to put in the pre element and
           in the textarea.'''
        if code:
            textarea_code = code
            if 'no-copy' in self.vlamcode or 'doctest' in self.vlamcode:
                self.style_code(pre, code)
                textarea_code = '\n'
            elif 'interpreter' in self.vlamcode:
                self.style_code(pre, code)
                textarea_code = self.python_code
            elif 'no-pre' in self.vlamcode:
                pre.text = '\n'
            else:
                self.style_code(pre, code)
        else:
            textarea_code = '\n'
        return textarea_code

    def get_base(self):
        """retrieve the base that relative links are relative to and store it
           in self.base; see http://www.faqs.org/rfcs/rfc1808.html, in
           particular 10.  Appendix - Embedding the Base URL in HTML documents
           In future this probably should check through the document
           to see if the base has been redefined.
        """
        self.base = self.url

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
            if self.external_flag:
                self._convert_external_link(elem)
            elif self.local_flag:
                self._convert_local_link(elem)
            else:
                raise # this should never happen
        return

    def _convert_external_link(self, elem):
        '''Converts all relativelinks to html files to use the "/load_external"
           command and relative links to absolute ones; the browser can
           handle loading of images, css files, etc. without using the
           "/load_external" command.  Absolute links (starting with "http://"
           are left untouched - and so, the browser will load them directly,
           bypassing crunchy.'''
        if 'src' in elem.attrib:
            e = elem.attrib['src']
            if not 'http://' in e:
                if e.endswith('.html') or e.endswith('.htm'):
                    elem.attrib['src'] = security.commands['/load_external']\
                                        + '?path=' + \
                             urllib.quote_plus(urlparse.urljoin(self.base, e))
                else:
                    elem.attrib['src'] = urlparse.urljoin(self.base, e)
        elif 'href' in elem.attrib:
            e = elem.attrib['href']
            if not 'http://' in e:
                if e.startswith('#'):
                    pass # the browser will handle these "as is"
                elif e.endswith('.html') or e.endswith('.htm'):
                    elem.attrib['href'] = security.commands['/load_external']\
                                        + '?path=' + \
                             urllib.quote_plus(urlparse.urljoin(self.base, e))
                else:
                    elem.attrib['href'] = urlparse.urljoin(self.base, e)

    def _convert_local_link(self, elem):
        '''Converts all links, except external links using "http://",
           to use the "/load_local" command.'''
        if 'src' in elem.attrib:
            e = elem.attrib['src']
            if not 'http://' in e:
                elem.attrib['src'] = security.commands['/load_local'] +\
                      '?path=' + urllib.quote_plus(os.path.join(self.base, e))
        elif 'href' in elem.attrib:
            e = elem.attrib['href']
            if not 'http://' in e:
                if e.startswith('#'):
                    pass # the browser will handle these "as is"
                else:
                    elem.attrib['href'] = security.commands['/load_local'] +\
                       '?path=' + urllib.quote_plus(os.path.join(self.base, e))

    def strip_prompts(self, text):
        """ Strips fake interpreter prompts from html code meant to
            simulate a Python session, and remove lines without prompts, which
            are supposed to represent Python output."""
        self.lines_of_prompt = []
        new_lines = []
        if not text:
            return
        lines = text.split('\n')
        linenumber = 0
        for line in lines:
            if line.endswith('\r'):
                line = line[:-1]
            if line.startswith(">>> "):
                new_lines.append(line[4:].rstrip())
                self.lines_of_prompt.append(("&gt;&gt;&gt; ", linenumber))
                linenumber += 1
            elif line.rstrip() == ">>>": # tutorial writer may forget the
                                         # extra space for an empty line
                new_lines.append('')
                self.lines_of_prompt.append((">>> ", linenumber))
                linenumber += 1
            elif line.startswith("... "):
                new_lines.append(line[4:].rstrip())
                self.lines_of_prompt.append(("... ", linenumber))
                linenumber += 1
            elif line.rstrip() == "...": # tutorial writer may forget the extra
                new_lines.append('')     # space
                self.lines_of_prompt.append(("... ", linenumber))
                linenumber += 1
            else:
                self.lines_of_prompt.append(('', line))
        self.python_code = '\n'.join(new_lines) + '\n'
        return

    def style_code(self, pre, code):
        '''Add css styling to Python code inside a <pre>.'''
            # wrap in a <span> so HTMLTreeBuilder can find root and use it.

        if 'linenumber' in self.vlamcode:
            add_line = True
            # the following is reset by self.colourizer;
            # do not attempt to use directly
            self.colourizer.outputLineNumber = True
            length = len("<span class='py_linenumber'>999 </span>")
        else:
            add_line = False
            self.colourizer.outputLineNumber = False

        if 'interpreter' in self.vlamcode or 'doctest' in self.vlamcode:
            newlines = []
            self.strip_prompts(code) # will initialise self.python_code
            try:
                # the following may raise an exception
                lines = self.colourizer.parseListing(self.python_code).split('\n')
                for (pr, info) in self.lines_of_prompt:
                    if pr:
                        if add_line:
                            newlines.append(lines[info][:length] +
                                            '<span class="py_prompt">' + pr +
                                  '</span>' + lines[info][length:])
                        else:
                            newlines.append('<span class="py_prompt">' + pr +
                                  '</span>' + lines[info])
                    elif info:
                        info = self.colourizer.changeHTMLspecialCharacters(info)
                        if add_line:  # get the spacing right...
                            newlines.append("<span class='py_linenumber'>    </span>"
                                           + '<span class="py_output">' + info +
                                           '</span>')
                        else:
                            newlines.append('<span class="py_output">' + info +
                                        '</span>')
                code = "<span>" + '\n'.join(newlines) + "</span>\n"
            except Exception, parsingErrorMessage:
                error_message = errors.parsing_error_dialog(
                                                          parsingErrorMessage)
                code = "<span><span class='warning'>%s</span>\n%s</span>"%(
                                               error_message, self.python_code)
        else:
            self.python_code = code
            try:
                code = "<span>" + self.colourizer.parseListing(code) + "</span>"
            except Exception, parsingErrorMessage:
                error_message = errors.parsing_error_dialog(
                                                          parsingErrorMessage)
                code = "<span><span class='warning'>%s</span>\n%s</span>"%(
                                               error_message, self.python_code)
        inp = StringIO(code)
        sub_tree = HTMLTreeBuilder.parse(inp)
        root = sub_tree.getroot()
        pre.clear()
        pre.append(root)
        inp.close()
        self.colourizer.reset()

####=== Additions from chewy

class HTMLUpdater(TreeBuilder):
    def __init__(self, filehandle, url, args):
        TreeBuilder.__init__(self, filehandle, url)
        self.args = args
        info = self.args.split(';')
        # Decoding the "=" sign encoding we used in addVLAM()
        for index, item in enumerate(info):
            if '_EQ_' in item:
                info[index] = item.replace('_EQ_', '=')
        # build a dict from alternating values (Thank you Python Cookbook)
        changes = dict(zip(info[::2], info[1::2]))
        for pre in self.tree.getiterator('pre'):
            # note: we need the uid information for updating *before* we
            # start processing the pre, unlike in the original crunchy
            # where the uid was assigned after.
            self._ID += 1
            self.uid = 'code' + str(self._ID)
            if self.uid in changes:
                pre.attrib['title'] = reconstruct_vlam(changes[self.uid])
        return


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
    'copied': ''
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
                        values['execution'] = ' external'
                        if 'console' in vlam:
                            values['execution'] += ' console'
                        if 'no-internal' in vlam:
                            values['execution'] += ' no-internal'
                if choice in ['editor', 'canvas', 'plot']:
                    if 'no-copy' in vlam:
                        values['copied'] = ' no-copy'
                    elif 'no-pre' in vlam:
                        values['copied'] = ' no-pre'
    return values

def reconstruct_vlam(new_vlam):
    ''' Reconstruct a sensible string as some of the options recorded
        may be irrelevant.
    '''
    values = analyze_vlam_code(new_vlam)
    print "values = ", values
    vlam = values['interactive'] + values['linenumber']
    if 'rows' in values['size']:
        vlam += ' size=(' + str(values['size']['rows']) + ', ' + \
                            str(values['size']['cols']) + ')'
    if 'width' in values['area']:
        vlam += ' area=(' + str(values['area']['width']) + ', ' + \
                            str(values['area']['height']) + ')'
    vlam += values['execution'] + values['copied']
    return vlam

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



####== end addtions from chewy

####================
#
# The following are functions used to insert various "vlam elements".
# These are purely ElementTree constructions, without any "vlam logic"
# They are introduced as a possible first step to refactor them into
# separate classes.


def addLoadLocal(parent):
    '''Inserts the two forms required to browse for and load a local tutorial.
    '''
    name1 = 'browser_'
    name2 = 'submit_'
    form1 = et.SubElement(parent, 'form', name=name1,
                        onblur = "document.%s.path.value="%name2+\
                        "document.%s.filename.value"%name1)
    input1 = et.SubElement(form1, 'input', type='file',
                 name='filename', size='80')
    br = et.SubElement(form1, 'br')

    form2 = et.SubElement(parent, 'form', name=name2, method='get',
                action=security.commands['/load_local'])
    input2 = et.SubElement(form2, 'input', type='hidden',
                           name='path')
    input3 = et.SubElement(form2, 'input', type='submit',
             value=_('Load local tutorial'))
    input3.attrib['class'] = 'crunchy'
    return

def addLoadForEdit(parent):
    '''Inserts the two forms required to browse for and load a local tutorial
       for editing it (adding or changing interactive elements).
    '''
    name1 = 'edit_browser_'
    name2 = 'submit_for_edition'
    form1 = et.SubElement(parent, 'form', name=name1,
                        onblur = "document.%s.path.value="%name2+\
                        "document.%s.filename.value"%name1)
    input1 = et.SubElement(form1, 'input', type='file',
                 name='filename', size='80')
    br = et.SubElement(form1, 'br')

    form2 = et.SubElement(parent, 'form', name=name2, method='get',
                action=security.commands['/edit_tutorial'])
    input2 = et.SubElement(form2, 'input', type='hidden',
                           name='path')
    input3 = et.SubElement(form2, 'input', type='submit',
             value=_('Edit tutorial'))
    input3.attrib['class'] = 'crunchy'
    return

def addLoadPython(parent, hidden_load_id, textarea_id):
    '''Inserts the two forms required to browse for and load a local Python
       file.  This is intended to be used to load a file in the editor.
    '''
    filename = 'filename' + hidden_load_id
    path = 'path' + hidden_load_id
    br = et.SubElement(parent, 'br')
    form1 = et.SubElement(parent, 'form',
                onblur = "a=getElementById('%s');b=getElementById('%s');a.value=b.value"%(path, filename))
    input1 = et.SubElement(form1, 'input', type='file', id=filename, size='80')
    br = et.SubElement(form1, 'br')

    form2 = et.SubElement(parent, 'form')
    input2 = et.SubElement(form2, 'input', type='hidden', id=path)
    btn = et.SubElement(parent, 'button',
        onclick="c=getElementById('%s');path=c.value;load_python_file('%s');"%(path, textarea_id))
    btn.text = _("Load Python file")
    btn2 = et.SubElement(parent, 'button',
        onclick="c=getElementById('%s');path=c.style.visibility='hidden';"%hidden_load_id)
    btn2.text = _("Cancel")
    return

def addSavePython(parent, hidden_save_id, textarea_id):
    '''Inserts the two forms required to browse for and load a local Python
       file.  This is intended to be used to load a file in the editor.
    '''
    filename = 'filename' + hidden_save_id
    path = 'path' + hidden_save_id
    br = et.SubElement(parent, 'br')
    form1 = et.SubElement(parent, 'form')
    input1 = et.SubElement(form1, 'input', type='file', id=filename, size='80')
    br = et.SubElement(form1, 'br')

    form2 = et.SubElement(parent, 'form')
    input2 = et.SubElement(form2, 'input', type='hidden', id=path)
    btn = et.SubElement(parent, 'button',
        onclick="a=getElementById('%s');b=getElementById('%s');a.value=b.value;"%(path, filename)+
        "c=getElementById('%s');path=c.value;save_python_file(path,'%s');"%(path, textarea_id))
    btn.text = _("Save Python file")
    btn2 = et.SubElement(parent, 'button',
        onclick="c=getElementById('%s');path=c.style.visibility='hidden';"%hidden_save_id)
    btn2.text = _("Cancel")
    btn3 = et.SubElement(parent, 'button',
        onclick="a=getElementById('%s');b=getElementById('%s');a.value=b.value;"%(path, filename)+
        "c=getElementById('%s');path=c.value;save_and_run(path,'%s');"%(path, textarea_id))
    btn3.text = _("Save and Run")
    return

def addLoadRemote(parent, url=''):
    '''Inserts a form to load a remote tutorial.'''
    form = et.SubElement(parent, 'form', name='path', size='80', method='get',
                       action=security.commands['/load_external'])
    input1 = et.SubElement(form, 'input', name='path', size='80',  value=url)
    input2 = et.SubElement(form, 'input', type='submit',
                           value=_('Load remote tutorial'))
    input2.attrib['class'] = 'crunchy'
    return

def addLanguageSelect(parent, text):
    """Inserts an html selector for languages.

       Language choice in option is a string of the form:
       'en, English; fr, Francais [; etc.]'
    """
    choices = text.split(";")
    form = et.SubElement(parent, "form", method='get',
                         action=security.commands["/select_language"])
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

def addCanvas(parent, width='400', height='400', id='', klass='',
                  btn_text='', rows='10', cols='80',
                  textarea_id='', textarea_text='\n'):
    """ Insert the required elements for a drawing canvas."""
    canvas = et.SubElement(parent, "canvas", width=width,
                            height=height, id=id,)
    canvas.attrib['class'] = klass
    canvas.text = '\n'
    br = et.SubElement(parent, "br")
    btn = et.SubElement(parent, "button", onclick='exec_canvas("'+id+'")')
    btn.text = btn_text
    br = et.SubElement(parent, "br")
    textarea = et.SubElement(parent, "textarea", rows=rows,
                             cols=cols, id=textarea_id)
    textarea.text = textarea_text
    return

def add_hidden_load_and_save(elem, id, textarea_id, id_string):
    hidden_load_id = 'hidden_load' + id + id_string
    hidden_load = et.SubElement(elem, 'div', id=hidden_load_id)
    hidden_load.attrib['class'] = 'load_python'
    addLoadPython(hidden_load, hidden_load_id, textarea_id)

    hidden_save_id = 'hidden_save' + id + id_string
    hidden_save = et.SubElement(elem, 'div', id=hidden_save_id)
    hidden_save.attrib['class'] = 'save_python'
    addSavePython(hidden_save, hidden_save_id, textarea_id)
    return

####== Chewy additions

def update_button():
    '''Inserts a button on a page used to update the entire page, based
       on previously recorded changes.'''
    button = et.Element('button', onclick="update();")
    button.attrib['class']='recorder'
    button.text = _("Update")
    return button


def addVLAM(parent, uid, pre_assigned, current_pre_tag):
    '''Intended to add the various vlam options under a <pre>'''
    js_changes = 'var vlam="";' # will be used to record a local
                                # javascript function to record changes
    # we show, as a heading, the previously recorded <pre ...>
    heading = et.SubElement(parent, 'h3')
    heading.attrib['class'] = "pre_vlam"
    heading.text = current_pre_tag
    br = et.SubElement(parent, 'br')
    # note: button is inserted here; its complete parameters are
    # determined at the end of this function.
    button = et.SubElement(parent, 'button', id='myButton'+uid)
    button.text = _("Record changes")
    table = et.SubElement(parent, 'table')
    table.attrib["class"] = "vlam"
    tr = et.SubElement(table, 'tr')
    # first column: interactive elements
    td1 = et.SubElement(tr, 'td', style='vertical-align:top;')
    form_name = uid + '_form1'
    form1 = et.SubElement(td1, 'form', name=form_name)
    fs1 = et.SubElement(form1, 'fieldset')
    legend1 = et.SubElement(fs1, 'legend')
    legend1.text = _("Interactive element")
    for type in ['none', 'interpreter', 'interpreter to editor',
                  'editor', 'doctest', 'canvas', 'plot']:
        inp = et.SubElement(fs1, 'input', type='radio', name='radios',
                            value=type)
        inp.text = type
        if type == pre_assigned['interactive']:
            inp.attrib['checked'] = 'checked'
        br = et.SubElement(fs1, 'br')
    # Note: can not embed "<" as a javascript character; hence use "!="
    js_changes += """
    for (i=0; i!=document.%s.radios.length;i++){
        if (document.%s.radios[i].checked){
            vlam += ' '+document.%s.radios[i].value;}
        };"""%(form_name, form_name, form_name)
    # 2nd column, top: line number choices
    td2 = et.SubElement(tr, 'td', style='vertical-align:top;')
    form_name = uid + '_form2'
    form2 = et.SubElement(td2, 'form', name=form_name)
    fs2 = et.SubElement(form2, 'fieldset')
    legend2 = et.SubElement(fs2, 'legend')
    legend2.text = _("Optional line numbering")
    for type in [' linenumber', 't', ' interpreter', ' interpreter linenumber']:
        if type == 't':
            note = et.SubElement(fs2, 'small')
            note.text = _("If interactive element is none:")
        else:
            inp = et.SubElement(fs2, 'input', type='radio', name='radios',
                                value=type)
            inp.text = type
            if type == pre_assigned['linenumber']:
                inp.attrib['checked'] = 'checked'
        br = et.SubElement(fs2, 'br')
    js_changes += """
    for (i=0; i!=document.%s.radios.length;i++){
        if (document.%s.radios[i].checked){
            vlam += ' '+document.%s.radios[i].value;}
        };"""%(form_name, form_name, form_name)
    # 2nd column, bottom: size and area
    form_name = uid + '_form3'
    form3 = et.SubElement(td2, 'form', name=form_name)
    fs3 = et.SubElement(form3, 'fieldset')
    legend3 = et.SubElement(fs3, 'legend')
    legend3.text = _("Size")
    note = et.SubElement(fs3, 'small')
    note.text = _("Size of editor (if present)")
    br = et.SubElement(fs3, 'br')
    for type in ['rows', 'cols']:
        note = et.SubElement(fs3, 'tt')
        note.text = type + ":"
        inp = et.SubElement(fs3, 'input', type='text', value='',
                            name=type)
        if type in pre_assigned['size']:
            inp.attrib['value'] = "%d"%pre_assigned['size'][type]
        br = et.SubElement(fs3, 'br')
    note = et.SubElement(fs3, 'small')
    note.text = _("Drawing area (if present)")
    br = et.SubElement(fs3, 'br')
    for type in ['width ', 'height']:  # extra space in 'width ' for alignment
        note = et.SubElement(fs3, 'tt')
        note.text = type + ":"
        inp = et.SubElement(fs3, 'input', type='text', value='',
                            name=type.strip())
        if type.strip() in pre_assigned['area']:
            inp.attrib['value'] = "%d"%pre_assigned['area'][type.strip()]
        br = et.SubElement(fs3, 'br')
    rows = ''
    cols = ''
    width = ''
    height = ''
    if pre_assigned['size']:
        rows = str(pre_assigned['size']['rows'])
        cols = str(pre_assigned['size']['cols'])
    if pre_assigned['area']:
        width = str(pre_assigned['area']['width'])
        height = str(pre_assigned['area']['height'])
    # WARNING: apparently can't use "width" (and perhaps "height")
    # as variable in js.
    # WARNING: when the changes are passed, the presence of an "=" sign is
    # taken to mean that a dict is being passed.  So, we "encode" it as "_EQ_"
    js_changes += """
    rows='%s'; cols='%s'; _width='%s'; _height='%s';
    if (document.%s.rows.value != rows || document.%s.cols.value != cols ||
        rows != '' || cols != ''){
    vlam += ' size_EQ_('+document.%s.rows.value+','+document.%s.cols.value+')';
    };
    if (document.%s.width.value != _width ||
        document.%s.height.value != _height ||
        _width != '' || _height != ''){
    vlam += ' area_EQ_('+document.%s.width.value+','+document.%s.height.value+')';
    };
    """%(rows, cols, width, height,
        form_name, form_name, form_name, form_name,
        form_name, form_name, form_name, form_name)
    # 3rd column, top: Code execution options
    td4 = et.SubElement(tr, 'td', style='vertical-align:top;')
    form_name = uid + '_form4'
    form4 = et.SubElement(td4, 'form', name=form_name)
    fs4 = et.SubElement(form4, 'fieldset')
    legend4 = et.SubElement(fs4, 'legend')
    legend4.text = _("Code execution")
    note = et.SubElement(fs4, 'small')
    note.text = _("Optional values for editor only")
    br = et.SubElement(fs4, 'br')
    for type in [' external', ' external no-internal', ' external console',
                 ' external console no-internal']:
        inp = et.SubElement(fs4, 'input', type='radio', name='radios',
                              value=type)
        inp.text = type
        if type == pre_assigned['execution']:
            inp.attrib['checked'] = 'checked'
        br = et.SubElement(fs4, 'br')
    js_changes += """
    for (i=0; i!=document.%s.radios.length;i++){
        if (document.%s.radios[i].checked){
            vlam += ' '+document.%s.radios[i].value;}
        };"""%(form_name, form_name, form_name)
    # 3rd column, bottom: Code copying options
    form_name = uid + '_form5'
    form5 = et.SubElement(td4, 'form', name=form_name)
    fs5 = et.SubElement(form5, 'fieldset')
    legend5 = et.SubElement(fs5, 'legend')
    legend5.text = _("Rarely used options")
    note = et.SubElement(fs5, 'small')
    note.text = _("Code not copied in editor")
    br = et.SubElement(fs5, 'br')
    note = et.SubElement(fs5, 'small')
    note.text = _("- done automatically for doctest")
    br = et.SubElement(fs5, 'br')
    inp = et.SubElement(fs5, 'input', type='radio', name='radios',
                        value='no-copy')
    inp.text = 'no-copy'
    if ' no-copy' == pre_assigned['copied']:
        inp.attrib['checked'] = 'checked'
    br = et.SubElement(fs5, 'br')
    note = et.SubElement(fs5, 'small')
    note.text = _("Code not appearing in <pre>")
    br = et.SubElement(fs5, 'br')
    note = et.SubElement(fs5, 'small')
    note.text = _("- incompatible with no-copy")
    br = et.SubElement(fs5, 'br')
    inp = et.SubElement(fs5, 'input', type='radio', name='radios',
                        value='no-pre')
    inp.text = 'no-pre'
    if ' no-pre' == pre_assigned['copied']:
        inp.attrib['checked'] = 'checked'
    br = et.SubElement(fs5, 'br')
    js_changes += """
    for (i=0; i!=document.%s.radios.length;i++){
        if (document.%s.radios[i].checked){
            vlam += ' '+document.%s.radios[i].value;}
        };"""%(form_name, form_name, form_name)
    # We now have all the information we need for the button
    button.attrib['onclick'] = "%s record('%s', vlam);"%(js_changes, uid)
    return
