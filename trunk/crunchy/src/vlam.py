"""
perform vlam substitution

sets up the page and calls appropriate plugins
"""

from StringIO import StringIO

import src.security as security

# Third party modules - included in crunchy distribution
from src.element_tree import ElementSoup
from src.interface import ElementTree, config, from_comet
et = ElementTree

from src.utilities import uidgen

DTD = '<!DOCTYPE html PUBLIC "-//W3C//DTD XHTML 1.0 Strict//EN" '\
'"http://www.w3.org/TR/xhtml1/DTD/strict.dtd">\n\n'

class CrunchyPage(object):
    '''class used to store an html page processed by Crunchy so
       as to add interactive elements.'''

    # We could do with defining a single variable "handlers" but doing
    # it this way makes it a bit easier to distinguish the various cases
    # (sorry, a weird mix of haskell and OCaml notation in a python program :)
    # handler1 ::  tag -> handler function
    handlers1 = {}
    # handler2 ::  tag -> attribute -> handler function
    handlers2 = {}
    # handler3 ::  tag -> attribute -> keyword -> handler function
    handlers3 = {}
    pagehandlers = []

    def __init__(self, filehandle, url, remote=False, local=False):
        """url should be just a path if crunchy accesses the page locally, or
           the full URL if it is remote"""
        self.is_remote = remote # True if remote tutorial, on the web
        self.is_local = local  # True if local tutorial, not from the server root
        if not (remote or local):
            self.is_from_root = True # if local tutorial from server root; default
        else:
            self.is_from_root = False
        self.pageid = uidgen()
        self.url = url
        from_comet['register_new_page'](self.pageid)
        # "old" method using ElementTree directly
        #self.tree = HTMLTreeBuilder.parse(filehandle, encoding = 'utf-8')
        html = ElementSoup.parse(filehandle, encoding = 'utf-8')
        self.tree = et.ElementTree(html)

        # The security module removes all kinds of potential security holes
        # including some meta tags with an 'http-equiv' attribute.
        self.tree = security.remove_unwanted(self.tree, self)
        self.included = set([])
        self.head = self.tree.find("head")
        if not self.head:
            self.head = et.Element("head")
            self.head.text = " "
            html = self.tree.find("html")
            try:
                html.insert(0, self.head)
            except AttributeError:
                html = self.tree.getroot()
                html.insert(0, self.head)
        self.body = self.tree.find("body")
        if not self.body:
            html = self.tree.find("html")
            try:
                self.body = et.SubElement(html, "body")
            except AttributeError:
                html = self.tree.getroot()
                self.body = et.SubElement(html, "body")
            self.body.attrib["onload"] = 'runOutput("%s")' % self.pageid
            warning = et.SubElement(self.body, 'h1')
            warning.text = "Missing body from original file"
        self.process_tags()
        self.body.attrib["onload"] = 'runOutput("%s")' % self.pageid
        self.add_js_code(comet_js)
        # first crunchy's style, then user's so it can override crunchy's
        self.add_crunchy_style()
        self.add_user_style()
        return

    def add_include(self, include_str):
        '''keeps track of information included on a page'''
        self.included.add(include_str)

    def includes(self, include_str):
        '''returns information about string included on a page'''
        return include_str in self.included

    def add_js_code(self, code):
        ''' includes some javascript code in the <head>.
            This is the preferred method.'''
        js = et.Element("script")
        js.set("type", "text/javascript")
        js.text = code
        self.head.append(js)

    def add_charset(self):
        '''adds utf-8 charset information on a page'''
        c = et.Element("meta")
        c.set("http-equiv", "Content-Type")
        c.set("content", "text/html; charset=UTF-8")
        self.head.append(c)

    def insert_js_file(self, filename):
        '''Inserts a javascript file link in the <head>.
           This should only be used for really big scripts
           (like editarea); the preferred method is to add the
           javascript code directly'''
        js = et.Element("script")
        js.set("src", filename)
        js.set("type", "text/javascript")
        js.text = " "  # prevents premature closing of <script> tag, misinterpreted by Firefox
        self.head.insert(0, js)
        return

    def add_css_code(self, code):
        '''inserts styling code in <head>'''
        css = et.Element("style")
        css.set("type", "text/css")
        css.text = code
        self.head.insert(0, css)

    def add_crunchy_style(self):
        '''inserts a link to the standard Crunchy style file'''
        css = et.Element("link")
        css.set("type", "text/css")
        css.set("rel", "stylesheet")
        css.set("href", "/crunchy.css")
        self.head.insert(0, css)
        return

    def add_user_style(self):
        '''adds user style meant to replace Crunchy's default if
        so desired by the user'''
        if not config['my_style']:
            return
        styles = config['styles']
        if styles == {}:
            return
        style = et.Element("style")
        style = et.Element("style")
        style.set("type", "text/css")
        style.text = ''
        for key in styles:
            if key != 'name':
                style.text += key + "{" + styles[key] + "}\n"
        self.head.append(style)  # has to appear last to override choices

    def process_tags(self):
        """process all the customised tags in the page"""

        #==================================================
        #
        # The following is the core of Crunchy processing - as such
        # it deserves a bit of an explanation.
        #
        # We will consider 5 examples:
        #
        # 1. <pre title="interpreter isolated"> ...</pre>
        #
        # 2. <meta name="crunchy_menu" content="filename.html"/>
        #
        # 3. <a href="some_file.html"> ...</a>
        #
        # 4. <pre> ...</pre>
        #
        # 5. No <meta> tag for a special menu
        #
        # Handlers are registered in CrunchyPlugin.py via the function
        # register_tag_handler(tag, attribute, keyword, handler)
        #
        # In example 1, we would have registered
        # tag = "pre"
        # attribute = "title"
        # The corresponding value would be: "interpreter isolated"
        # The keyword would be: "interpreter"
        #
        # In example 2, we would have registered
        # tag = "meta"
        # attribute = "name"
        # The corresponding value would be: "crunchy_menu"
        # The keyword would be: "crunchy_menu"
        #
        # In example 3, we would have registered
        # tag = "a"
        # attribute = None
        # This would register a null_handler
        #
        # In example 4, we would not have registered anything; instead
        # we could instruct Crunchy to add some custom markup based
        # on a user's choice so that, for example, it could reproduce
        # example 1.
        #
        # Example 5 refers to the absence of a special menu;
        # we thus use a default Crunchy value.
        #
        #============================================
        #
        # IMPORTANT: we must convert existing links on the page
        # before creating new ones - but not those that have been identified
        # as external links.  This means that handlers1 must
        # be dealt with first - with one exception.

        # First, we insert the security advisory, so that security information
        # is available to other plugins if required (like custom menus...)
        CrunchyPage.handlers2["no_tag"]["security"](self)

        #  The following for loop deals with example 3
        for tag in CrunchyPage.handlers1:
            for elem in self.tree.getiterator(tag):
            # vlam option <a title="external_link"> needs special treatment
                if (('title' not in elem.attrib) or
                           (elem.attrib['title'] != 'external_link')):
                    CrunchyPage.handlers1[tag](self, elem)

        #  The following for loop deals with examples 1 and 2
        for tag in CrunchyPage.handlers3:
            for elem in self.tree.getiterator(tag):
                # elem.attrib  size may change during the loop
                attributes = dict(elem.attrib)
                for attr in attributes:
                    if attr in CrunchyPage.handlers3[tag]:
                        try:
                            keyword = [x for x in elem.attrib[attr].split(" ")
                                    if x != ''][0]
                        except IndexError:
                            keyword = None
                        if keyword in CrunchyPage.handlers3[tag][attr]:
                            CrunchyPage.handlers3[tag][attr][keyword]( self,
                                            elem, self.pageid + ":" + uidgen())
                            break
        #  The following for loop deals with example 4
        # Crunchy can treat <pre> that have no markup as though they
        # are marked up with a default value
        n_m = config['no_markup'].lower()
        if n_m != 'none':
            keyword = n_m.split(" ")[0]
            for elem in self.tree.getiterator("pre"):
                if "title" not in elem.attrib:
                    elem.attrib["title"] = n_m
                    CrunchyPage.handlers3["pre"]["title"][keyword](self, elem,
                                                self.pageid + ":" + uidgen())
        #  The following for loop deals with example 5; we do need the
        # security information to be included in the menu...
        if "menu_included" not in self.included:
            CrunchyPage.handlers2["no_tag"]["menu"](self)
        return

    def read(self):
        '''create fake file from a tree, adding DTD and charset information
           and return its value as a string'''
        fake_file = StringIO()
        fake_file.write(DTD + '\n')
        self.add_charset()
        self.tree.write(fake_file)
        return fake_file.getvalue()

comet_js = """
function runOutput(channel){
    var h = new XMLHttpRequest();
    h.onreadystatechange = function(){
        if (h.readyState == 4){
            try{
                var status = h.status;
            }
            catch(e){
                var status = "NO HTTP RESPONSE";
            }
            switch (status){
                case 200:
                    eval(h.responseText);
                    runOutput(channel);
                    break;
            }
        }
    };
    h.open("GET", "/comet?pageid="+channel, true);
    h.send("");
};
"""
