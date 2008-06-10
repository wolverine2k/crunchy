"""
perform vlam substitution

sets up the page and calls appropriate plugins
"""

from StringIO import StringIO

from src.security import remove_unwanted

# Third party modules - included in crunchy distribution
from src.element_tree import ElementSoup
from src.interface import ElementTree, config, from_comet
et = ElementTree

from src.utilities import uidgen

DTD = '<!DOCTYPE html PUBLIC "-//W3C//DTD XHTML 1.0 Strict//EN" '\
'"http://www.w3.org/TR/xhtml1/DTD/strict.dtd">\n'

# The purpose of the following class is to facilitate unit testing.  It can
# be initialized with no further action taking place, and each method
# has then to be called explicitly.
# In production code, we invoke CrunchyPage instead which does all
# the required processing automatically.

class _BasePage(object):
    '''
       Base class used to store html pages and the methods to process them.
    '''
    # We define some class variables that will be shared amongst all instances;
    # they are initialized via CrunchyPlugin.py
    handlers1 = {} # tag -> handler function
    handlers2 = {} # tag -> attribute -> handler function
    handlers3 = {} # tag -> attribute -> keyword -> handler function
    pagehandlers = []

    def __init__(self):  # tested
        '''initialises a few values, and registers the page for comet i/o.'''
        self.included = set([])
        self.pageid = uidgen()
        from_comet['register_new_page'](self.pageid)
        return

    def create_tree(self, filehandle, encoding='utf-8'):  # tested
        '''creates a tree (elementtree object) from an html file'''
        # note: this process removes the existing DTD
        html = ElementSoup.parse(filehandle, encoding = 'utf-8')
        self.tree = et.ElementTree(html)

    def find_head(self):  # tested
        '''finds the head in an html tree; adds one in if none is found.
        '''
        self.head = self.tree.find("head")
        if self.head is None:
            self.head = et.Element("head")
            self.head.text = " "
            html = self.tree.find("html")
            try:
                html.insert(0, self.head)
            except AttributeError:
                html = self.tree.getroot()
                assert html.tag == 'html'
                html.insert(0, self.head)
        return

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
        '''inserts styling code in <head>'''
        css = et.Element("style", type="text/css")
        css.text = code
        try:   # should never be needed in normal call from CrunchyPage
            self.head.insert(0, css)
        except:
            self.find_head()
            self.head.insert(0, css)
        return

    def add_crunchy_style(self):  # tested
        '''inserts a link to the standard Crunchy style file'''
        css = et.Element("link", type= "text/css", rel="stylesheet",
                         href="/crunchy.css")
        try:   # should never be needed in normal call from CrunchyPage
            self.head.insert(0, css)
        except:
            self.find_head()
            self.head.insert(0, css)
        # we inserted first so that it can be overriden by tutorial writer's
        # style and by user's preferences.
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
        style = et.Element("style", type="text/css")
        style.text = ''
        for key in styles:
            if key != 'name':
                style.text += key + "{" + styles[key] + "}\n"
        try:   # should never be needed in normal call from CrunchyPage
            self.head.append(style) # has to appear last to override all others.
        except:
            self.find_head()
            self.head.append(style)
        return

    def add_js_code(self, code):  # tested
        ''' includes some javascript code in the <head>.
            This is the preferred method.'''
        js = et.Element("script", type="text/javascript")
        js.text = code
        try:   # should never be needed in normal call from CrunchyPage
            self.head.append(js)
        except:
            self.find_head()
            self.head.append(js)
        return

    def insert_js_file(self, filename):  # tested
        '''Inserts a javascript file link in the <head>.
           This should only be used for really big scripts
           (like editarea); the preferred method is to add the
           javascript code directly'''
        js = et.Element("script", src=filename, type="text/javascript")
        js.text = " "  # prevents premature closing of <script> tag, misinterpreted by Firefox
        try:   # should never be needed in normal call from CrunchyPage
            self.head.insert(0, js)
        except:
            self.find_head()
            self.head.insert(0, js)
        return

    def add_charset(self):
        '''adds utf-8 charset information on a page'''
        meta = et.Element("meta", content="text/html; charset=UTF-8")
        meta.set("http-equiv", "Content-Type")
        self.head.append(meta)
        return

    def read(self):
        '''create fake file from a tree, adding DTD and charset information
           and return its value as a string'''
        fake_file = StringIO()
        fake_file.write(DTD + '\n')
        self.add_charset()
        self.tree.write(fake_file)
        return fake_file.getvalue()


class CrunchyPage(_BasePage):
    '''class used to store an html page processed by Crunchy with added
       interactive elements.
    '''
    def __init__(self, filehandle, url, remote=False, local=False):
        """
        read a page, processes it and outputs a completely transformed one,
        ready for display in browser.

        url should be just a path if crunchy accesses the page locally, or
        the full URL if it is remote.
        """
        _BasePage.__init__(self)
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
        self.process_tags()

        # adding the javascript for communication between the browser and the server
        self.body.attrib["onload"] = 'runOutput("%s")' % self.pageid
        self.add_js_code(comet_js)

        # Extra styling
        self.add_crunchy_style() # first Crunchy's style
        self.add_user_style()    # user's preferences can override Crunchy's
        return



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


        ## Note: do this via a pagehandler instead of handlers2.
        # perhaps introduce two types of pagehandlers:
        # begin_pagehandlers and end_pagehandlers, and loop through them.

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

    #def read(self):
    #    '''create fake file from a tree, adding DTD and charset information
    #       and return its value as a string'''
    #    fake_file = StringIO()
    #    fake_file.write(DTD + '\n')
    #    self.add_charset()
    #    self.tree.write(fake_file)
    #    return fake_file.getvalue()

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
