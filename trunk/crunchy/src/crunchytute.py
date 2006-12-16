'''
Process VLAM pages and describe each one as a class instance,

based on treetools.py by André Roberge

'''
from elementtree import ElementTree, HTMLTreeBuilder
et = ElementTree
from StringIO import StringIO
import re
import os.path
import os
import urlparse
import urllib

import httprepl
import errorhandler
import colourize
import security
import preferences
prefs = preferences.UserPreferences()
import widgets
from translation import _

#the DTD to use:
DTD = '<!DOCTYPE html PUBLIC "-//W3C//DTD XHTML 1.0 Strict//EN" "http://www.w3.org/TR/xhtml1/DTD/strict.dtd">\n\n'

DOCTESTS = {}

class VLAMPage(object):
    """Encapsulates a page containing VLAM"""
    #for LUIDs:
    COUNT = 0
    
    def __init__(self, filehandle, url, remoteflag=False):
        """all you have to give it is a file handle to read from and an url."""
        
        try:
            self.tree = HTMLTreeBuilder.parse(filehandle)
        except Exception, info:
            raise errorhandler.HTMLTreeBuilderError(url, info)
        self.tree = security.remove_unwanted(self.tree)
        self.url = url
        # If self.remoteflag is True (and this is a vlam file), 
        # all links in the page are converted to refer to the 
        # local crunchy frog server.
        self.remoteflag = remoteflag
        self.colourizer = colourize.Colourizer()
        self.get_base()
        if self.remoteflag:
            self.convert_all_links()
        # The following two flags are set in process_head()

        self.head = self.tree.find("head")
        self.body = self.tree.find("body")
        self.process_head()
        self.process_body()

    def process_head(self):
        """set up <head>"""
        #add the standard crunchy includes
        #self.insert_js("/src/javascript/code_exec.js")
        #"file:" + 
        self.insert_js(security.commands['/get_user_js']+"?"+urllib.pathname2url(security.js_name))
        self.insert_js("/src/javascript/custom_alert.js")
        self.insert_css("/src/css/default.css")
        self.insert_css("/src/css/custom_alert.css")
        for style in prefs.styles:
            self.head.append(style)
        meta_lang = et.Element("meta")
        meta_lang.set("http-equiv", "Content-Type")
        meta_lang.set("content", "text/html; charset=iso-8859-1")
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

    def insert_js(self, filename):
        '''Inserts a js file in the <head>.'''
        js = et.Element("script")
        js.set("src", filename)
        js.set("type", "text/javascript")
        self.head.insert(0, js)
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
        """Span can be used for hidden comments or for requesting to load
           local or remote Crunchy tutorials."""
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
                if 'local_tutorial' in attrib[1].lower():
                    form = et.SubElement(span, "form")
                    form.set("name", "browserform")
                    form.set("onblur", 
                        'document.submitform.path.value=document.browserform.filename.value')
                    inp = et.SubElement(form, "input")
                    inp.set("type", "file")
                    inp.set("name", "filename")
                    inp.set("size", "80")
                    br = et.SubElement(form, "br")
                    form2 = et.SubElement(span, "form")
                    form2.set("name", "submitform")
                    form2.set("action", security.commands["/load_local"])
                    form2.set("method", "get")
                    inp2 = et.SubElement(form2, "input")
                    inp2.set("type", "hidden")
                    inp2.set("name", "path")
                    inp3 = et.SubElement(form2, "input")
                    inp3.set("type", "submit")
                    inp3.set("value", _("Load local tutorial"))
                    inp3.set("class", "crunchy")
                elif 'remote_tutorial' in attrib[1].lower():
                    form = et.SubElement(span, "form")
                    form.set("action", security.commands["/load_external"])
                    form.set("method", "get")
                    inp = et.SubElement(form, "input")
                    inp.set("type", "text")
                    inp.set("name", "path")
                    inp.set("size", "80")
                    inp.set("value", span.text)
                    br = et.SubElement(form, "br")
                    inp2 = et.SubElement(form, "input")
                    inp2.set("type", "submit")
                    inp2.set("value", _("Load remote tutorial"))
                    inp2.set("class", "crunchy")
                elif 'choose_language' in attrib[1].lower():
                    span.tag = "form"
                    # language choice in option is a string of the form:
                    # en, English; fr, Francais [; etc.]
                    choices = span.text.split(";")
                    span.clear()
                    span.set("action", security.commands["/select_language"])
                    span.set("method", "get")
                    select = et.SubElement(span, "select")
                    select.set("name", "language")
                    for choice in choices:
                        args = choice.split(",")
                        opt = et.SubElement(select, "option")
                        opt.set("value", args[0].strip())
                        opt.text = args[1].strip()
                    br = et.SubElement(span, "br")
                    inp = et.SubElement(span, "input")
                    inp.set("type", "submit")
                    inp.set("value", _("Submit language choice"))

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

    def prepare_elem(self, elem):
        '''Common code to substitute_x.'''
        id = 'code' + str(self.COUNT)
        self.COUNT += 1
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
        id, text, elem = self.prepare_elem(elem)
        #neutralise the element
        elem.tag = "span"
        #and add an interpreter
        elem.append(widgets.Interpreter(text))

    def substitute_editor(self, elem):
        """Substitutes an editor for elem.  It is used for 'editor', 'doctest',
           as well as 'interpreter to editor' options."""
        id, text, elem = self.prepare_elem(elem)
        #neutralise it:
        elem.tag = "span"
        #this needs support for finessing the buttons:
        elem.append(widgets.Editor(widgets.EXEC_BUTTON, text))

    def substitute_canvas(self, elem):
        """substitute a canvas for elem"""
        id, text, elem = self.prepare_elem(elem)
        if 'size' in self.vlamcode:
            res = re.search(r'size=\((.+?),(.+?)\)', self.vlamcode)
            rows = int(res.groups()[0])
            cols = int(res.groups()[1])
        else:
            rows, cols = (10, 80)
            
        if 'area' in self.vlamcode:
            res = re.search(r'area=\((.+?),(.+?)\)', self.vlamcode)
            width = int(res.groups()[0])
            height = int(res.groups()[1])
        else:
            width, height = 400, 400
        pre = et.SubElement(elem, 'pre')
        # no-pre does not show the code inside the <pre> element, but
        # only the editor.  This does not make sense 
        # if the code is not copied into the textarea!
        if 'no-pre' in self.vlamcode and not 'no-copy' in self.vlamcode:
            pre.text = '\n'
        else:
            self.style_code(pre, text)
        if 'canvas' in self.vlamcode:
            id = "canvas%d_%d"%(width, height) + id
            klass = 'canvas'
            btn_text = _("Draw")
        else:
            id = "plot%d_%d"%(width, height) + id
            klass = 'plot'
            btn_text = _("Plot")
            
        canvas = et.SubElement(elem, "canvas", width=str(width), 
                                height=str(height), id=id,)
        canvas.attrib['class'] = klass
        canvas.text = '\n'

        et.SubElement(elem, "br")
        btn = et.SubElement(elem, "button", onclick='exec_canvas("'+id+'")')
        btn.text = btn_text
        et.SubElement(elem, "br")
        textarea = et.SubElement(elem, "textarea", rows=str(rows), cols=str(cols), id=id+"_input")
        if 'no-copy' in self.vlamcode:
            textarea.text = '\n'
        else:
            textarea.text = text
        
    def get(self):
        """vlam file: serialise the tree and return it;
           simply returns the file content otherwise.
        """
        fake_file = StringIO()
        fake_file.write(DTD + '\n')
        self.tree.write(fake_file)
        return fake_file.getvalue()
    
    def get_base(self):
        """retrieve the base that relative links are relative to and store it in self.base
        see http://www.faqs.org/rfcs/rfc1808.html
        In future this should check through the document to see if the base has been redefined.
        """
        self.base = self.url
        
    def convert_all_links(self):
        """looks for any attribute anywhere in the document, called 'src' or 'href' and converts it if it's relative
        In future this should be user-configurable, the user should be able to specify whether or not external links are loaded as vlam
        It might also be good if tute writers can specify a preference too.
        """
        for elem in self.tree.getiterator():
            if 'src' in elem.attrib:
                if not 'http://' in elem.attrib['src']:
                    if elem.attrib['src'].endswith('.html') or elem.attrib['src'].endswith('.htm'):
                        elem.attrib['src'] = '/load_external?path=' + \
                            urllib.quote_plus(urlparse.urljoin(self.base, elem.attrib['src']))
                    else:
                        elem.attrib['src'] = urlparse.urljoin(self.base, elem.attrib['src'])
            elif 'href' in elem.attrib:
                if not 'http://' in elem.attrib['href']:
                    if elem.attrib['href'].endswith('.html') or elem.attrib['href'].endswith('.htm'):
                        elem.attrib['href'] = '/load_external?path=' + \
                            urllib.quote_plus(urlparse.urljoin(self.base, elem.attrib['href']))
                    else:
                        elem.attrib['href'] = urlparse.urljoin(self.base, elem.attrib['href'])

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
            elif line.rstrip() == "...": # tutorial writer may forget the extra space
                new_lines.append('')
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
            # the following is reset by self.colourizer; do not attempt to use directly
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
                error_message = errorhandler.parsing_error_dialog(
                                                          parsingErrorMessage)
                code = "<span><span class='warning'>%s</span>\n%s</span>"%(
                                               error_message, self.python_code)
        else:
            self.python_code = code
            try:
                code = "<span>" + self.colourizer.parseListing(code) + "</span>"
            except Exception, parsingErrorMessage:
                error_message = errorhandler.parsing_error_dialog(
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


