"""
perform vlam substitution
right now this supports a tiny subset of the complete VLAM syntax
"""

from StringIO import StringIO
import time
import socket
import random
import md5


# Third party modules - included in crunchy distribution
from element_tree import ElementTree, HTMLTreeBuilder
et = ElementTree

def uidgen():
    """a moderately decent uid generator,
    see http://aspn.activestate.python.com/ASPN/Cookbook/Python/Recipe/213761
    """
    t = long(time.time() * 1000)
    r = long(random.random()*1000000000000000L)
    try:
        a = socket.gethostbyname(socket.gethostname())
    except:
        a = random.random()*1000000000000L
    data = str(t) + str(r) + str(a)
    data = md5.md5(data).hexdigest()
    return data

class CrunchyPage(object):
    # hander is string -> string -> handler function
    handlers = {}
    def __init__(self, filehandle):
        self.tree = HTMLTreeBuilder.parse(filehandle)
        self.head = self.tree.find("head")
        self.body = self.tree.find("body")
        self.process_head()
        self.process_body()
        
    def process_head(self):
        self.load_css("/comet.css")
        self.load_js("/comet.js")
        self.load_js("/graphics.js")
        
    def load_css(self, filename):
        '''Inserts a css file in the <head>.'''
        css = et.Element("link")
        css.set("rel", "stylesheet")
        css.set("href", filename)
        css.set("type", "text/css")
        self.head.insert(0, css)
        return
    
    def load_js(self, filename):    
        js = et.Element("script")
        js.set("src", filename)
        js.set("type", "text/javascript")
        js.text = "\n"  # easier to read source
        self.head.append(js)
    
    def add_js_code(self, code):    
        js = et.Element("script")
        js.set("type", "text/javascript")
        js.text = code
        self.head.append(js)
            
    def process_body(self):
        self.body.attrib["onload"] = 'runOutput("0")'
        for tag in CrunchyPage.handlers:
            for elem in self.body.getiterator(tag):
                if "title" in elem.attrib:
                    if elem.attrib["title"] in CrunchyPage.handlers[tag]:
                        CrunchyPage.handlers[tag][elem.attrib["title"]](self, elem, uidgen())
                
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
