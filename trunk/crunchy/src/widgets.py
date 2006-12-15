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

This file should contain none of the VLAM logic, just the code for generating 
the visual elements as XML trees.
"""


from elementtree import ElementTree
et = ElementTree
import luid
import httprepl
from colourize import Colourizer

#some constants:
EXEC_BUTTON = 0x1
DOCTEST_BUTTON = 0x2
EXTERNAL_BUTTON = 0x4

colourer = Colourizer()

class Interpreter(et._ElementInterface):
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
        self.__dict__ = elem.__dict__

class Javascript(et._ElementInterface):
    """Some javascript embedded in appropriate XHTML"""
    def __init__(self, source):
        elem = et.Element("script", type="text/javascript")
        elem.text = source
        self.__dict__ == elem.__dict__
        
class Editor(et._ElementInterface):
    """An editor with one some execute buttons"""
    javascript = None
    def __init__(self, buttons, text, rows=10, cols=80, copy=True, doctest=None):
        """Initialise it, buttons must be a bitwise ORed comination of the constants above"""
        elem = et.Element("div")
        uid = luid.next()
        a = et.SubElement(elem, 'a', id=uid)
        a.text = ' '
        if text:
            elem.append(Code(text))
        textarea = et.SubElement(elem, "textarea", rows=str(rows), cols=str(cols), id=uid+"_code")
        if not copy:
            textarea.text = '\n'
        else:
            textarea.text = text
        et.SubElement(elem, "br")
        if buttons & EXEC_BUTTON:
            btn = et.SubElement(elem, "button", onclick='exec_by_id("'+uid+'")')
            btn.text = _("Evaluate")
        if buttons & DOCTEST_BUTTON:
            btn = et.SubElement(elem, "button", onclick='doctest_by_id("'+uid+'")')
            btn.text = _("Evaluate Doctest")
        if buttons & EXTERNAL_BUTTON:
            btn = et.SubElement(elem, "button", onclick='exec_external("'+uid+'")')
            btn.text = _("Execute Externally")
        if buttons & CONSOLE_BUTTON:
            btn = et.SubElement(elem, "button", onclick='exec_external_console("'+uid+'")')
            btn.text = _("Execute in Console")
        self.__dict__ = elem.__dict__
    
class ExecOutput(et._ElementInterface):
    """An output box with pretty colouring etc"""
    javascript = None
    def __init__(self, uid):
        elem = et.Element("div")
        elem.attrib['class'] = 'term_out'
        elem.attrib['onload'] = "update_output(%s)" % uid
        self.__dict = elem.__dict__
        
class Code(et._ElementInterface):
    """Non-interactive highlighted code"""
    def __init__(self, code):
        """Initialise a simple colouring"""
        elem = et.Element("span")
        elem.text = colourer.parseListing(code)
        
class Canvas(et._ElementInterface):
    """Graphics Canvas"""
    javascript = None
    def __init__(self, uid):
        pass
    
class Plotter(Canvas):
    """Like a canvas but for plotting curves"""
    pass