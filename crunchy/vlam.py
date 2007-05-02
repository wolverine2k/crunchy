"""
perform vlam substitution

sets up the page and calls appropriate plugins
"""

from StringIO import StringIO

import security

# Third party modules - included in crunchy distribution
from element_tree import ElementTree, HTMLTreeBuilder
et = ElementTree

from cometIO import register_new_page

count = 0

def uidgen():
    """an suid (session unique ID) generator
    """
    global count
    count += 1
    return str(count)

class CrunchyPage(object):
    # handlers ::  string -> string -> handler function
    # pagehandlers :: 
    # (sorry, a weird mix of haskell and OCaml notation in a python program :)
    handlers = {}
    pagehandlers = []
    null_handlers = {}
    def __init__(self, filehandle, url):
        """url should be just a path if crunchy accesses the page locally, or the full URL if it is remote"""
        self.pageid = uidgen()
        self.url = url
        register_new_page(self.pageid)
        self.tree = HTMLTreeBuilder.parse(filehandle)
        # The security module removes all kinds of potential security holes
        # including some meta tags with an 'http-equiv' attribute.
        self.tree = security.remove_unwanted(self.tree)
        self.included = set([])
        self.head = self.tree.find("head")
        self.body = self.tree.find("body")
        self.process_tags()
        # we have to check wether there is a body element
        # because sometimes there is just a frameset elem.
        if self.body:
            self.body.attrib["onload"] = 'runOutput("%s")' % self.pageid
        else:
            print "No body, assuming frameset"
        self.add_js_code(comet_js)

    def add_include(self, include_str):
        self.included.add(include_str)

    def includes(self, include_str):
        return include_str in self.included

    def add_js_code(self, code):
        ''' includes some javascript code in the <head>.
            This is the preferred method.'''
        js = et.Element("script")
        js.set("type", "text/javascript")
        js.text = code
        self.head.append(js)

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
        css = et.Element("style")
        css.set("type", "text/css")
        css.text = code
        self.head.insert(0, css)

    def process_tags(self):
        """process all the customised tags in the page"""
        for tag in CrunchyPage.handlers:
            for elem in self.tree.getiterator(tag):
                if "title" in elem.attrib:
                    keyword = elem.attrib["title"].split(" ")[0]
                    if keyword in CrunchyPage.handlers[tag]:
                        CrunchyPage.handlers[tag][keyword](self, elem,
                                         self.pageid + ":" + uidgen(),
                                         elem.attrib["title"].lower())
        for tag in CrunchyPage.null_handlers:
            for elem in self.tree.getiterator(tag):
                CrunchyPage.null_handlers[tag](self, elem, self.pageid +
                                                      ":" + uidgen(), None)

    def read(self):
        fake_file = StringIO()
        # May want to use the "private" _write() instead of write() as the
        # latter will add a redundant <xml ...> statement unless the
        # encoding is utf-8 or ascii.
        self.tree.write(fake_file)
        return fake_file.getvalue()

comet_js = """
function runOutput(channel)
{
    var h = new XMLHttpRequest();
    h.onreadystatechange = function(){
        if (h.readyState == 4)
        {
            try
            {
                var status = h.status;
            }
            catch(e)
            {
                var status = "NO HTTP RESPONSE";
            }
            switch (status)
            {
            case 200:
                //alert(h.responseText);
                eval(h.responseText);
                runOutput(channel);
                break;
            default:
                //alert("Output seems to have finished");
            }
        }
    };
    h.open("GET", "/comet?pageid="+channel, true);
    h.send("");
};
"""
