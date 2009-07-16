"""
perform vlam substitution

sets up the page and calls appropriate plugins
"""

import codecs
import traceback
from StringIO import StringIO
from os.path import join

from src.security import remove_unwanted
from src.utilities import uidgen

# Third party modules - included in crunchy distribution
from src.element_tree import ElementSoup
from src.interface import ElementTree, config, from_comet, plugin
et = ElementTree

import src.interface as interface

DTD = u"""<!DOCTYPE html PUBLIC "-//W3C//DTD XHTML 1.0 Strict//EN" "http://www.w3.org/TR/xhtml1/DTD/strict.dtd">\n"""

TRACE = u"""Please file a bug report at http://code.google.com/p/crunchy/issues/list
================================================================================
"""

# The purpose of the following class is to facilitate unit testing.  It can
# be initialized with no further action taking place, and each method
# has then to be called explicitly.
# In production code, we invoke CrunchyPage instead which does all
# the required processing automatically.

def handle_exception(full_page=True):
    '''Basic handler for exceptions.'''

    root_path = join(plugin['get_root_dir'](), "server_root/")
    if full_page:
        path = join(root_path, "exception.html")
        text = codecs.open(path, encoding='utf8').read()
    else:
        text = u"TRACEBACK"

    trace = traceback.format_exc()
    text = text.replace(u"TRACEBACK", TRACE + trace)
    return text

class BasePage(object): # tested
    '''
       Base class used to store html pages and the methods to process them.
    '''
    # We define some class variables that will be shared amongst all instances;
    # they are initialized via CrunchyPlugin.py
    handlers1 = {} # tag -> handler function
    handlers2 = {} # tag -> attribute -> handler function
    handlers3 = {} # tag -> attribute -> keyword -> handler function
    begin_handlers1 = {}  # tag -> handler function
    final_handlers1 = {}  # tag -> handler function
    begin_pagehandlers = []
    end_pagehandlers = []

    def __init__(self, username):  # tested
        '''initialises a few values, and registers the page for comet i/o.'''
        self.included = set([])
        self.username = username
        self.pageid = uidgen(self.username)
        from_comet['register_new_page'](self.pageid)
        return

    def create_tree(self, filehandle):  # tested
        '''creates a tree (elementtree object) from an html file'''
        # note: this process removes the existing DTD
        html = ElementSoup.parse(filehandle)
        self.tree = et.ElementTree(html)

    def find_head(self):  # tested
        '''finds the head in an html tree; adds one in if none is found.
        '''
        self.head = self.tree.find("head")
        if self.head is None:
            self.head = et.Element("head")
            self.head.text = u" "
            html = self.tree.find("html")
            try:
                html.insert(0, self.head)
            except AttributeError:
                html = self.tree.getroot()
                assert html.tag == 'html'
                html.insert(0, self.head)

    def find_body(self):  # tested
        '''finds the body in an html tree; adds one if none is found.
        '''
        self.body = self.tree.find("body")
        if self.body is None:
            html = self.tree.find("html")
            try:
                self.body = et.SubElement(html, "body")
            except AttributeError:
                html = self.tree.getroot()
                assert html.tag == 'html'
                self.body = et.SubElement(html, "body")
            warning = et.SubElement(self.body, 'h1')
            warning.text = "Missing body from original file"
        return

    def add_include(self, include_str):  # tested
        '''keeps track of information included on a page'''
        self.included.add(include_str)

    def includes(self, include_str):  # tested
        '''returns information about string included on a page'''
        return include_str in self.included

    def add_css_code(self, code):  # tested
        '''Inserts styling code in <head>. Raises AssertionError if
        code is not a Unicode string.'''

        assert isinstance(code, unicode)

        css = et.Element(u"style", type=u"text/css")
        css.text = code
        try:
            self.head.insert(0, css)
        # should never be needed in normal call from CrunchyPage
        except AttributeError, e:
            self.find_head()
            self.head.insert(0, css)

    def add_crunchy_style(self):  # tested
        '''inserts a link to the standard Crunchy style file'''
        css = et.Element("link",
                         type=u"text/css",
                         rel=u"stylesheet",
                         href=u"/css/crunchy.css")
        try:
            self.head.insert(0, css)
        # should never be needed in normal call from CrunchyPage
        except AttributeError:
            self.find_head()
            self.head.insert(0, css)
        # we inserted first so that it can be overriden by tutorial writer's
        # style and by user's preferences.
        return

    def insert_css_file(self, path):
        '''inserts a link to the standard Crunchy style file'''
        css = et.Element("link",
                         type=u"text/css",
                         rel=u"stylesheet",
                         href=path)
        try:
            self.head.append(css)
        # should never be needed in normal call from CrunchyPage
        except AttributeError:
            self.find_head()
            self.head.append(css)
        return

    def add_user_style(self):  # tested
        '''adds user style meant to replace Crunchy's default if
        so desired by the user'''
        if 'my_style' not in config:   # should normally be found
            return
        if not config['my_style']:
            return
        if 'styles' not in config:    # should normally be found
            return
        else:
            styles = config['styles']

        if styles == {}:
            return
        style = et.Element("style", type=u"text/css")
        style.text = u''
        for key in styles:
            if key != 'name':
                style.text += key + u"{" + styles[key] + u"}\n"
        try:
            self.head.append(style) # has to appear last to override all others.
        # Should never be needed in normal call from CrunchyPage
        except AttributeError:
            self.find_head()
            self.head.append(style)
        return

    def add_js_code(self, code):  # tested
        ''' Includes some javascript code in the <head>. This is the
        preferred method. Raises AssertionError if code is not a
        Unicode string.'''

        assert isinstance(code, unicode)

        js = et.Element("script", type=u"text/javascript")
        js.text = code
        try:
            self.head.append(js)
        # should never be needed in normal call from CrunchyPage
        except AttributeError:
            self.find_head()
            self.head.append(js)
        return

    def insert_js_file(self, filename):  # tested
        '''Inserts a javascript file link in the <head>. This should
           only be used for really big scripts (like editarea); the
           preferred method is to add the javascript code directly.
           Raises AssertionError if filename is not a Unicode
           string.'''

        assert isinstance(filename, unicode)

        js = et.Element("script",
                        src=filename,
                        type=u"text/javascript")
        # prevents premature closing of <script> tag, misinterpreted by Firefox
        js.text = u" "
        try:
            self.head.insert(0, js)
        # should never be needed in normal call from CrunchyPage
        except AttributeError:
            self.find_head()
            self.head.insert(0, js)
        return

    def add_charset(self):  # tested
        '''adds utf-8 charset information on a page'''
        meta = et.Element("meta",
                          content=u"text/html; charset=UTF-8")
        meta.set(u"http-equiv", u"Content-Type")
        try:
            self.head.append(meta)
        # should never be needed in normal call from CrunchyPage
        except AttributeError:
            self.find_head()
            self.head.append(meta)
        return

    def extract_keyword(self, elem, attr): # tested
        '''extract a "keyword" from a vlam string.

        A "keyword" is the first complete word in a vlam string; for
        example: vlam="keyword some other options"

        attr is assumed to be a valid key for elem[].
        '''
        try:
            keyword = [x for x in elem.attrib[attr].split(" ") if x != ''][0]
        except IndexError:
            keyword = None
        return keyword

    def process_handlers3(self):  # tested
        '''
        For all registered "tags" of "type 3", this method
        processes:  (tag, attribute, keyword) -> handler function
        '''
        for tag in self.handlers3:
            for elem in self.tree.getiterator(tag):
                # elem.attrib  size may change during the loop
                attributes = dict(elem.attrib)
                for attr in attributes:
                    if attr in self.handlers3[tag]:
                        keyword = self.extract_keyword(elem, attr)
                        if keyword in self.handlers3[tag][attr]:
                            self.handlers3[tag][attr][keyword]( self,
                                            elem, self.pageid + "_" + uidgen(self.username))
                            break

    def process_handlers2(self):  # tested
        '''
        For all registered "tags" of "type 2", this method
        processes:  (tag, attribute) -> handler function
        as long as more specific instructions of
        "type 3" : (tag, attribute, keyword) -> handler function
        have not been defined.
        '''
        for tag in self.handlers2:
            for elem in self.tree.getiterator(tag):
                # elem.attrib size may change during the loop
                attributes = dict(elem.attrib)
                for attr in attributes:
                    if attr in self.handlers2[tag]:
                        do_it = True
                        if attr in self.handlers3[tag]:
                            keyword = self.extract_keyword(elem, attr)
                            if keyword in self.handlers3[tag][attr]:
                                do_it = False
                        if do_it:
                            uid = self.pageid + "_" + uidgen(self.username)
                            self.handlers2[tag][attr](self, elem, uid)
        return

    def process_type1(self, handlers):  # tested
        '''
        For all registered "tags" of "type 1", this method
        processes:  tag -> handler function
        as long as more specific instructions of either
        "type 2" : (tag, attribute) -> handler function, or
        "type 3" : (tag, attribute, keyword) -> handler function
        have not been defined.
        '''
        for tag in handlers:
            for elem in self.tree.getiterator(tag):
                do_it = True
                if tag in self.handlers2:  # may need to skip
                    for attr in elem.attrib:
                        if attr in self.handlers2[tag]:
                            do_it = False
                            break
                if tag in self.handlers3:  # may need to skip
                    for attr in elem.attrib:
                        if attr in self.handlers3[tag]:
                            keyword = self.extract_keyword(elem, attr)
                            if keyword in self.handlers3[tag][attr]:
                                do_it = False
                                break
                if do_it:
                    uid = self.pageid + "_" + uidgen(self.username)
                    handlers[tag](self, elem, uid)
        return

    def process_begin_handlers1(self, handlers):
        '''
        Processes handlers based on their tag.

        Used, for example, to modify existing markup on a page.
        '''
        for tag in handlers:
            for elem in self.tree.getiterator(tag):
                handlers[tag](self, elem, 'dummy')
        return

    def process_handlers1(self):  # tested
        '''processes special handlers of type 1.'''
        self.process_type1(self.handlers1)

    def process_final_handlers1(self):  # tested
        '''processes special handlers of type 1 after other handlers have been
        processed on that page'''
        self.process_type1(self.final_handlers1)

    def read(self):  # tested
        '''create fake file from a tree, adding DTD and charset information
           and return its value as a string'''
        fake_file = StringIO()
        fake_file.write(DTD + u'\n')
        self.add_charset()
        try:
            self.tree.write(fake_file)
        except Exception:
            return handle_exception()
        return fake_file.getvalue()

class CrunchyPage(BasePage):
    '''class used to store an html page processed by Crunchy with added
       interactive elements.
    '''
    def __init__(self, filehandle, url, username=None, remote=False, local=False):
        """
        read a page, processes it and outputs a completely transformed one,
        ready for display in browser.

        url should be just a path if crunchy accesses the page locally, or
        the full URL if it is remote.
        """
        if username is None:
            try:
                username = interface.username_at_start
            except:
                pass
        BasePage.__init__(self, username=username)
        self.url = url

        # Assign tutorial type
        self.is_remote = remote # True if remote tutorial, on the web
        self.is_local = local  # True if local tutorial, not from the server root
        if not (remote or local):
            self.is_from_root = True # if local tutorial from server root
        else:
            self.is_from_root = False

        # Create the proper tree structure from the html file
        self.create_tree(filehandle)  # assigns self.tree

        # Removing pre-existing javascript, unwanted objects and
        # all kinds of other potential security holes
        remove_unwanted(self.tree, self) # from the security module

        self.find_head()  # assigns self.head
        self.find_body()  # assigns self.body

        # Crunchy's main work: processing vlam instructions, etc.
        try:
            self.process_tags()
        except Exception:
            self.body.clear()
            self.body.tag = "body"
            pre = et.Element('pre')
            pre.text = handle_exception(False)
            self.body.append(pre)
            return

        # adding the javascript for communication between the browser and the server
        self.insert_js_file(u"/javascript/jquery.js")
        self.add_js_code(comet_js % self.pageid)

        # Extra styling
        self.add_crunchy_style() # first Crunchy's style
        self.add_user_style()    # user's preferences can override Crunchy's
        return

    def process_tags(self):
        """process all the customised tags in the page"""

        self.process_begin_handlers1(self.begin_handlers1)

        for handler in CrunchyPage.begin_pagehandlers:
            handler(self)

        # Since handlers of type 2 or 3 can, in principle, add elements (tags)
        # with no vlam, and since such elements could be processed by
        # handlers of type 1, we must make sure we process the type 1
        # elements before type 2, and finish with type 3.
        self.process_handlers1()
        self.process_handlers2()
        self.process_handlers3()

        # An exception to the above is the case of handling the "no markup"
        # where we add interactive elements when no vlam was present -
        # for example, to transform the official Python tutorial into
        # an interactive session.
        self.process_final_handlers1()

        for handler in CrunchyPage.end_pagehandlers:
            handler(self)
        return


# jquery compatible javascript:
comet_js = u"""
function runOutput(channel){
    $.ajax({type : "GET",
            url : "/comet?pageid=" + channel,
            cache : false,
            dataType: "script",
            success : function(data, status){
                runOutput(channel);
            }
            })
};

$(document).ready(function(){
    runOutput("%s");
});
"""
