"""
The widgets used by VLAM:

1.  The Interpreter (Interpreter)
2.  The Code Editor (Editor)
3.  The Execution Output Boxes (ExecOutput)
4.  The Graphics Canvas (Canvas)
5.  The Plotter (Plotter)
6.  'Crunchy Comments' (Comment)
7.  Javascript blocks, containing javascript (Javascript)
8.  Highlighted Python code sections (Code)

All of the widgets inherit ElementTree._ElementEnterface, and so are drop-in XML
trees.
"""

from ElementTree import ElementTree, _ElementInterface
et = ElementTree
import luid
import httprepl

#some constants:
EXEC_BUTTON = 01
DOCTEST_BUTTON = 02

class Interpreter(_ElementInterface):
    javascript = None
    def __init__(self, text = None):
        uid = luid.next()
        elem = et.Element("div")
        elem.attrib['class'] = "interpreter"
        #make sure the support code is there:
        js = Javascript(self.javascript)
        #container for the example code:
        pre = et.SubElement(elem, 'pre')
        #todo: styling
        if text:
            pre.text = text
        output = et.SubElement(elem, 'div', id=uid+'_output_container')
        output.attrib['class'] = "interp_output_container"
        output.text = '\n' # a single space would push the first "output" prompt right
        prompt = et.SubElement(elem, "span", id=uid+"_prompt")
        prompt.attrib['class'] = "stdin"
        prompt.text = ">>> "
        input = et.SubElement(elem, "input", type="text", id=uid+"_input", 
            onkeyup='interp_trapkeys(event, "'+uid+'")')
        input.attrib['class'] = "interp_input"
        httprepl.interps[uid] = httprepl.HTTPrepl()
        tipbar = et.SubElement(self.body, "div", id=uid+"_tipbar")
        tipbar.attrib['class'] = "interp_tipbar"
        tipbar.text = " "
        self.__dict__ = elem.__dict__

class Javascript(_ElementInterface):
    """Some javascript embedded in appropriate XHTML"""
    def __init__(self, source):
        elem = et.Element("script", type="text/javascript")
        elem.text = text
        self.__dict__ == elem.__dict__
        
class Editor(_ElementInterface):
    """An editor with one some execute buttons"""
    javascript = None
    def __init__(self, uid):
        """Initialise it, uid must be a unique string - it is used
        to match the code with it's output box"""
        pass
    
class ExecOutput(_ElementInterface):
    """An output box with pretty colouring etc"""
    javascript = None
    def __init__(self, uid):
        pass
    
class Code(_ElementInterface):
    """Non-interactive highlighted code"""
    def __init__(self, code):
        pass
    
class Canvas(_ElementInterface):
    """Graphics Canvas"""
    javascript = None
    def __init__(self, uid):
        pass
    
class Plotter(Canvas):
    """Like a canvas but for plotting curves"""
    pass