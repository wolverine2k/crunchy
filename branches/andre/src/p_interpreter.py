'''p_interpreter.py

Plugin module whose purpose is to style Python code contained in a <pre>
element, and insert a Python interpreter.

'''

from translation import _
import s_styler
from element_tree import ElementTree as et


# name(s) appearing in a vlam code for calling this plugin
name = 'interpreter'
# valid html tags to which this element can be added
html_tags = ['pre']
# link to javascript file that needs to be included with this plugin
js_crunchy_link = 'to be defined'
js_chewy_link = None
# javascript code that needs to be included for each element added
js_crunchy = 'to be defined'
# javascript code that needs to be included for the markup tool
js_chewy = {'code': 'to be defined', 'pre': 'to be defined'}

def add_crunchy_markup(elem, uid=None):
    '''add the html markup to style the code

    For an interpreter, we have the styled Python code
    followed by the output element followed by the Python
    interpreter prompt (and input).  A tipbar is added for displaying
    interactively result from help, etc.  A (hidden) canvas might be added
    in a future version'''
    if elem.tag in html_tags:
        python_code = s_styler.embed('div', elem)
        elem.attrib['id'] = '%s_container'%uid
        output = et.SubElement(elem, 'pre', id=uid+'_output_container')
        output.attrib['class'] = "interp_output_container"
        output.text = '\n' # a single space would push the first "output" prompt right
        prompt = et.SubElement(elem, "span", id=uid+"_prompt")
        prompt.attrib['class'] = "stdin"
        prompt.text = ">>> "
        input = et.SubElement(elem, "input", type="text", id=uid+"_input",
               onkeypress='interp_trapkeys(event, "'+uid+'","%s")'%_("Waiting..."))
        input.attrib['class'] = "interp_input"
        # the following used to be a subelement of self.body - need to check that it works
        tipbar = et.SubElement(elem, "div", id=uid+"_tipbar")
        tipbar.attrib['class'] = "interp_tipbar"
        tipbar.text = " "
        #interpreters.interps[uid] = interpreters.HTTPrepl()
    else:
        raise Exception # needs to improve on this
    return python_code # note that we are not usually interested in the actual code for an interpreter


def add_chewy_markup(elem):
    pass # to be defined
