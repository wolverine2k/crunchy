'''
crunchyfier.py

Takes an html page with VLAMarkup and outputs an
html page with interactive (and other) elements added.

'''
# Python standard library modules
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
DTD = '<!DOCTYPE html PUBLIC "-//W3C//DTD XHTML 1.0 Strict//EN" "http://www.w3.org/TR/xhtml1/DTD/strict.dtd">\n\n'

DOCTESTS = {}

class VLAMPage(object):
    """Encapsulates a page containing VLAM"""
    #for locally unique IDs
    __ID = -1

    def __init__(self, filehandle, url, external_flag=False, local_flag=False):
        """all you have to give it is a file handle to read from and an url."""
        print "filehandle = ", filehandle
        print "url=", url
        try:
            self.tree = HTMLTreeBuilder.parse(filehandle)
        except Exception, info:
            raise errors.HTMLTreeBuilderError(url, info)
        self.tree = security.remove_unwanted(self.tree)
        self.url = url
        self.colourizer = colourize.Colourizer()
        # If self.external_flag or self.local_flag is True, which means
        # that the original page was loaded via an input box
        # (/load_local or /load_external)
        # all links in the page are converted to use the same
        self.external_flag = external_flag
        self.local_flag = local_flag
        self.get_base()
        if self.external_flag or self.local_flag:
            self.convert_all_links()
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

    def append_editarea_script(self, id):
        '''Appends a js script for each editarea/textarea'''
        js = et.Element("script")
        js.set("type", "text/javascript")
        # unfortunately, it appears that the load (and possibly save) options
        # on the toolbar do not work with Firefox 2.0. This has been checked
        # with the example included in the EditArea distribution. Instead,
        # we will use the custom controls; these have to be included as
        # buttons appearing below the textarea.
        js.text = """
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
min_height: 150});"""%(id, prefs._editarea_lang)
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
        js.text = """
function my_load_file(id){
var obj = document.getElementById('hidden'+id);
obj.style.visibility = "visible";
}
function my_save_file(id){
var obj = document.getElementById('hidden_save'+id);
obj.style.visibility = "visible";
}
"""
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
           2. requesting to load local or remote Crunchy tutorials, or
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
        return

    def process_pre(self, pre):
        """process a pre element and decide what to do with it"""
        for attrib in pre.attrib.items():
            if attrib[0] == 'title':
                if 'none' in attrib[1]: # no interactive element
                    self.vlamcode = pre.attrib['title'].lower()
                    if pre.text.startswith('\n'):
                        pre.text = pre.text[1:]
                    self.style_code(pre, pre.text)
                elif 'editor' in attrib[1]: # includes "interpreter to editor"
                    self.substitute_editor(pre)
                elif 'interpreter' in attrib[1]:
                    self.substitute_interpreter(pre)
                elif 'doctest' in attrib[1]:
                    self.substitute_editor(pre)
                elif 'canvas' in attrib[1] or 'plot' in attrib[1]:
                    self.substitute_canvas(pre)

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

    def substitute_interpreter(self, elem):
        """substitute an interpreter for elem"""
        #self.interpreter_present = True
        id, text, elem = self.prepare_element(elem)
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

    def substitute_editor(self, elem):
        """Substitutes an editor for elem.  It is used for 'editor', 'doctest',
           as well as 'interpreter to editor' options."""
        global DOCTESTS
        id, text, elem = self.prepare_element(elem)
        pre = et.SubElement(elem, 'pre')
        textarea_text = self._apportion_code(pre, text)
        textarea_id = id+"_code"
        self.textareas.append('\"'+textarea_id+'\"')

        rows, cols = self._get_size()
        textarea = et.SubElement(elem, "textarea", rows=rows, cols=cols,
                                 id=textarea_id)
        textarea.text = textarea_text
        hidden_load_id = 'hidden'+id+"_code"
        hidden_load = et.SubElement(elem, 'div', id=hidden_load_id)
        hidden_load.attrib['class'] = 'load_python'
        addLoadPython(hidden_load, hidden_load_id, textarea_id)

        hidden_save_id = 'hidden_save'+id+"_code"
        hidden_save = et.SubElement(elem, 'div', id=hidden_save_id)
        hidden_save.attrib['class'] = 'save_python'
        addSavePython(hidden_save, hidden_save_id, textarea_id)

        if 'external' in self.vlamcode:
            if not 'nointernal' in self.vlamcode:
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

    def substitute_canvas(self, elem):
        """substitute a canvas for elem"""
        id, text, new_div = self.prepare_element(elem)
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
        hidden_load_id = 'hidden'+id+"_input"
        hidden_load = et.SubElement(elem, 'div', id=hidden_load_id)
        hidden_load.attrib['class'] = 'load_python'
        addLoadPython(hidden_load, hidden_load_id, textarea_id)

        hidden_save_id = 'hidden_save'+id+"_input"
        hidden_save = et.SubElement(elem, 'div', id=hidden_save_id)
        hidden_save.attrib['class'] = 'save_python'
        addSavePython(hidden_save, hidden_save_id, textarea_id)


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

    def get(self):
        """vlam file: serialise the tree and return it;
           simply returns the file content otherwise.
        """
        fake_file = StringIO()
        fake_file.write(DTD + '\n')
        self.tree.write(fake_file)
        return fake_file.getvalue()

    def get_base(self):
        """retrieve the base that relative links are relative to and store it
           in self.base; see http://www.faqs.org/rfcs/rfc1808.html
           In future this probably should check through the document to see if
           the base has been redefined.
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

###================
#
# The following are functions used to insert various "vlam elements".
# These are purely ElementTree constructions, without any "vlam logic"
# They are introduced as a possible first step to refactor them into
# separate classes.
###================


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

