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
        for pre in self.body.getiterator('pre'):
            print "found pre"
            self.process_pre(pre)
            
    def process_pre(self, pre):
        if "title" in pre.attrib:
            if pre.attrib["title"] == "interpreter":
                #pre is to become an interpreter
                pre.tag = "span"
                uid = self.insert_interpreter()
                self.insert_output(pre, uid)
                
                
            elif pre.attrib["title"] == "editor":
                #pre is to become an editor
                pre.tag = "span"
                uid = self.insert_editor(pre)
                self.insert_output(pre, uid)
                
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
        
    def insert_interpreter(self):
        """inserts an interpreter (actually the js code to initialise an interpreter)"""
        uid = uidgen()
        self.add_js_code('init_interp("%s");' % uid)
        return uid
        
    def insert_editor(self, elem):
        uid = uidgen()
        inp = et.SubElement(elem, "textarea")
        inp.attrib["rows"] = "10"
        inp.attrib["cols"] = "80"
        inp.attrib["id"] = "code_" + uid
        inp.text = "\n"
        et.SubElement(elem, "br")
        btn = et.SubElement(elem, "button")
        btn.attrib["onclick"] = "exec_code('%s')" % uid
        btn.text = "Execute"
        et.SubElement(elem, "br")
        return uid
        
    def read(self):
        fake_file = StringIO()
        # use the "private" _write() instead of write() as the latter
        # will add a redundant <xml ...> statement unless the
        # encoding is utf-8 or ascii.
        self.tree.write(fake_file)
        return fake_file.getvalue()
