'''et_colour.py

This simple module is designed to

1. take as input an ElementTree Element corresponding to
   an html element (such as <pre> or <code>) containing some Python code;
   this Python code may already be marked up;
2. identify if line numbering is required and the offset (i.e. if we do not
   start line numbers at 1, but at "1+offset";
3. pass the content of the Element (including any other markup present)
   as an "html string" (i.e. no longer an ElementTree Element)
   to colourize.py (which works with html - not ElementTree Elements)
   so that it can be styled appropriately;
4. return the new marked up element, as well as the corresponding Python code.

For example (using html notation), we could have as input
<pre title="some value">
print <span class="some value">"Hello World!"</span>
</pre>

and the corresponding output would be
<pre title="some value">
<span class="py_keyword">print</span> <span class="string">"Hello World!"</span>
</pre>

If we replaced ElementTree by another parser (say, BeautifulSoup), we
would not need to modify colourize.py - only this module.
'''

import re

import colourize
from element_tree import ElementTree, HTMLTreeBuilder
et = ElementTree


def style(elem):
    '''style some Python code (adding html markup) if "title" attribute
    is present and return it inside the original html element
    (<pre> or <code>, most likely) with attributes unchanged.
    Any original markup inside the Python code
    will be lost, except that <br/> will have been converted into "\n"'''
    tag = elem.tag
    py_code = extract_code(elem)
    if 'title' in elem.attrib:
        offset = get_linenumber_offset(elem.attrib['title'])
        styled_code = colourize.style(py_code, offset)
    else:
        styled_code = py_code
    new_html = "<%s>\n%s\n</%s>"%(tag, styled_code, tag)
    new_elem = et.fromstring(new_html)
    new_elem.attrib = elem.attrib
    return new_elem, py_code


def extract_code(elem):
    ''' extract all the text (Python code) from a marked up
    code sample encoded as an ElementTree structure, but converting
    <br/> into "\n"; inspired by F.Lundh's gettext() '''
    text = elem.text or ""
    for e in elem:
        text += extract_code(e)
        if e.tag == 'br':
            text += '\n'
        if e.tail:
            text += e.tail
    return text

def get_linenumber_offset(vlam):
    ''' Extract the offset value if present
        The vlam code is expected to be of the form
        [linenumber [start=n]]
        (where n is an integer)
        but could contain upper case letters as well.

        Note that the vlam code uses "start" as it is easier to read,
        but we use "offset" (i.e. difference from the normal starting
        number 1) in internal calculations as it is easier to simply
        add an offset without having to remember to subtract 1
        everywhere.'''
    if 'linenumber' in vlam.lower():
        try:
            res = re.search(r'linenumber\s*=\s*([0-9]*)', vlam.lower())
            offset = int(res.groups()[0])-1
        except:
            offset = 0 # linenumber will start at 1
    else:
        offset = None # no linenumber will be added
    return offset

