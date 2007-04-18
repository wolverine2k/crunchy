"""
perform vlam substitution

sets up the page and calls appropriate plugins
"""

from StringIO import StringIO
import time
import socket
import random
import md5


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
    # handlers ::  string -> string -> handler function (sorry, a weird mix of haskell and OCaml notation in a python program :)
    handlers = {}
    pagehandlers = []
    def __init__(self, filehandle):
        self.pageid = uidgen()
        register_new_page(self.pageid)
        self.tree = HTMLTreeBuilder.parse(filehandle)
        self.head = self.tree.find("head")
        self.body = self.tree.find("body")
        self.process_body()
        self.add_js_code(comet_js)
    
    def add_js_code(self, code):    
        js = et.Element("script")
        js.set("type", "text/javascript")
        js.text = code
        self.head.append(js)
    
    def add_css_code(self, code):
        css = et.Element("style")
        css.set("type", "text/css")
        css.text = code
        self.head.insert(0, css)
        
    def process_body(self):
        self.body.attrib["onload"] = 'runOutput("%s")' % self.pageid
        for tag in CrunchyPage.handlers:
            for elem in self.body.getiterator(tag):
                if "title" in elem.attrib:
                    keyword = elem.attrib["title"].split(" ")[0]
                    if keyword in CrunchyPage.handlers[tag]:
                        CrunchyPage.handlers[tag][keyword](self, elem, self.pageid + ":" + uidgen(), elem.attrib["title"].lower())
                
    def insert_output(self, elem, uid):
        """insert an output widget into elem, usable for editors and interpreters,
        includes a canvas :-)
        """
        output = et.SubElement(elem, "span")
        output.attrib["class"] = "output"
        output.attrib["id"] = "out_" + uid
        output.text = "\n"
        inp = et.SubElement(elem, "input")
        inp.attrib["id"] = "in_" + uid
        inp.attrib["onkeydown"] = 'push_keys(event, "%s")' % uid
        inp.attrib["type"] = "text"
        inp.attrib["class"] = "input"
        canvas = et.SubElement(elem, "canvas")
        canvas.attrib["id"] = "canvas_" + uid
        canvas.attrib["width"] = "400"
        canvas.attrib["height"] = "400"
        canvas.attrib["class"] = "crunchy_canvas"
        canvas.text = "You need a browser that supports &lt;canvas&gt; for this to work"
        
    def read(self):
        fake_file = StringIO()
        # use the "private" _write() instead of write() as the latter
        # will add a redundant <xml ...> statement unless the
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
