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
from StringIO import StringIO
import tokenize, keyword

import luid
import httprepl
from colourize import Colourizer
from translation import _

#some constants:
EXEC_BUTTON = 0x1
DOCTEST_BUTTON = 0x2
EXTERNAL_BUTTON = 0x4
CONSOLE_BUTTON = 0x8

colourer = Colourizer()

class Interpreter(et._ElementInterface):
    javascript = None
    def __init__(self, text = None):
        uid = luid.next()
        elem = et.Element("div")
        elem.attrib['class'] = "interpreter"
        #make sure the support code is there:
        #js = Javascript(self.javascript) #disabled because we load it all at once for now
        #container for the example code:
        elem.append(parseListing(text))
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
            #todo: styling
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
        elem = parseListing(code)
        self.__dict__ = elem.__dict__
        
class Canvas(et._ElementInterface):
    """Graphics Canvas"""
    javascript = None
    def __init__(self, uid):
        pass
    
class Plotter(Canvas):
    """Like a canvas but for plotting curves"""
    pass

def parseListing(code, line_nos = False):
    """parse some Python code returning an XHTML tree, a simple refactoring of André's colourizer.py"""
    in_buf = StringIO(code)
    out_elem = et.Element("pre")
    out_elem.text = ''
    tokenType = None
    tokenString = ""
    endLine = endColumn = 0
    for tok in tokenize.generate_tokens(in_buf.readline):
        lastTokenType = tokenType
        tokenType = tok[0]
        lastTokenString = tokenString
        tokenString = tok[1]
        beginLine, beginColumn = tok[2]
        endOldLine, endOldColumn = endLine, endColumn
        endLine, endColumn = tok[3]
        internal_elems = out_elem.getchildren()
        if tokenType == tokenize.ENDMARKER:  
            break
        if beginLine != endOldLine:
            if lastTokenType in [tokenize.COMMENT, tokenize.NEWLINE, tokenize.NL]: 
                if line_nos:
                    line_no = et.SubElement(out_elem,"span")
                    line_no.attrib['class'] = "py_linenumber"
                    line_no.text = "%3d" % beginLine
            elif tokenType != tokenize.DEDENT:  # logical line continues
                if len(internal_elems):
                    internal_elems[-1].tail = "\n"
            if not len(internal_elems):
                out_elem.text = " "*(beginColumn - endOldColumn)
            else:
                internal_elems[-1].tail = " "*(beginColumn - endOldColumn)
        else:
            #insert the requisite spaces:
            if not len(internal_elems):
                #spaces at start:
                out_elem.text = " "*(beginColumn - endOldColumn)
            else:
                #spaces after last subelement:
                internal_elems[-1].tail = " "*(beginColumn - endOldColumn)
        #the stuff from htmlFormat():
        if tokenType == tokenize.NAME:
            token_elem = et.SubElement(out_elem, "span")
            token_elem.text = tokenString
            if keyword.iskeyword(tokenString.strip()):
                token_elem.attrib['class']='py_keyword'
            else:
                token_elem.attrib['class']='py_variable'
        elif tokenType == tokenize.STRING:
            tokenString = changeHTMLspecialCharacters(tokenString)
            string_elem = et.SubElement(out_elem, 'span')
            string_elem.attrib['class'] = 'py_string'
            if tokenString[0:3] in ['"""',"'''"]:
                string_elem.attrib['class'] = 'py_comment'
                if line_nos:
                    line_no = 1
                    for line in tkenString.split('\n'):
                        line_lbl = et.SubElement(string_elem,'span')
                        line_lbl.text = "%3d" % line_no
                        line_lbl.attrib['class'] = 'py_linenumber'
                        line_lbl.tail = line
                        line_no += 1
                else:
                    string_elem.text = tokenString
            else:
                string_elem.text = tokenString
        elif tokenType == tokenize.COMMENT:
            comm_elem = et.SubElement(out_elem, 'span')
            comm_elem.attrib['class'] = 'py_comment'
            comm_elem.text = tokenString
        elif tokenType == tokenize.NUMBER:
            num_elem = et.SubElement(out_elem, 'span')
            num_elem.attrib['class'] = 'py_number'
            num_elem.text = tokenString
        elif tokenType == tokenize.OP:
            op_elem = et.SubElement(out_elem, 'span')
            op_elem.attrib['class'] = 'py_op'
            op_elem.text = tokenString
        else:
            other_elem = et.SubElement(out_elem, 'span')
            other_elem.text = tokenString
    return out_elem

def changeHTMLspecialCharacters(aString):
    aString = aString.replace('&', '&amp;')
    aString = aString.replace('<', '&lt;')
    aString = aString.replace('>', '&gt;')
    return aString