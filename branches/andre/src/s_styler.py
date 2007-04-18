'''s_styler.py

This simple module is a Crunchy service designed to style Python code
contained inside a <pre> element and possibly insert the it into a more
complicated html structure.

The actual code styling is done by colourize.py.

The current module assumes that html element have been parsed by
ElementTree to become ElementTree Elements.
If we replaced ElementTree by another parser (say, BeautifulSoup), we
would not need to modify colourize.py - only this module.
'''

import re

import colourize
from element_tree import ElementTree as et

def style(elem):
    '''style some Python code (adding html markup) if "title" attribute
    is present and return it inside the original html element
    (<pre> or <code>, most likely) with attributes unchanged.
    Any original markup inside the Python code
    will be removed, except that <br/> will have been converted into "\n".

    To be more specific, style() does the following:
    1. take as input an ElementTree Element corresponding to
       an html element (such as <pre> or <code>) containing some Python code;
       this Python code may already be marked up;
    2. identify if line numbering is required and, if so, if line numbering
       needs to start at a number different from 1;
    3. pass the content of the Element (including any other markup present)
       as an "html string" (i.e. no longer an ElementTree Element)
       to colourize.py so that it can be styled appropriately;
    4. return the new marked up element, as well as the corresponding
       Python code.

    For example (using html notation), we could have as input
    <pre title="some value">
    print <span class="some value">"Hi!"</span>
    </pre>

    and the corresponding output would be
    <pre title="some value">
    <span class="py_keyword">print</span> <span class="string">"Hi!"</span>
    </pre>
    '''
    # styling
    py_code = extract_code(elem)
    if 'title' in elem.attrib:
        offset = get_linenumber_offset(elem.attrib['title'])
        styled_code, py_code = colourize.style(py_code, offset)
    else:
        styled_code = py_code
    # re-creating element
    tag = elem.tag
    new_html = "<%s>\n%s\n</%s>"%(tag, styled_code, tag)
    new_elem = et.fromstring(new_html)
    attrib = duplicate_dict(elem.attrib)
    replace_element(elem, new_elem)
    elem.attrib = attrib
    return py_code

def embed(embed_tag, elem):
    '''style some Python code the same way that style() does it but,
    in addition, embeds the element into a new html one which retains
    the identity of the original one.  For instance, taking the same
    example as the one used in style() above, if we had
    embed_tag = div, the result would be

    <div><pre title="some value">
    <span class="py_keyword">print</span> <span class="string">"Hi!"</span>
    </pre></div>
    '''
    # styling
    py_code = extract_code(elem)
    if 'title' in elem.attrib:
        offset = get_linenumber_offset(elem.attrib['title'])
        styled_code, py_code = colourize.style(py_code, offset)
    else:
        styled_code = py_code
    # re-creating inside element (usually the pre)
    tag = elem.tag
    new_html = "<%s>\n%s\n</%s>"%(tag, styled_code, tag)
    new_elem = et.fromstring(new_html)
    attrib = duplicate_dict(elem.attrib)
    new_elem.attrib = attrib
    # create the container ...
    container = et.Element(embed_tag)
    # ... with the same identity as the original element
    replace_element(elem, container)
    # insert the recreated element in the new container
    elem.append(new_elem)
    return py_code

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
    ''' Determine the desired number for the 1st line of Python code.
        The vlam code is expected to be of the form
        [linenumber [=n]]    (where n is an integer)
        but could contain upper case letters as well.

        Note that the vlam code uses "linenumber" as it is easier to read,
        but we use "offset" (i.e. difference from the normal starting
        number 1) in internal calculations as it is easier to simply
        add an offset without having to remember to subtract 1
        everywhere.'''
    if 'linenumber' in vlam.lower():
        try:
            res = re.search(r'linenumber\s*=\s*([0-9]*)', vlam.lower())
            offset = int(res.groups()[0]) - 1
        except:
            offset = 0 # linenumber will start at 1
    else:
        offset = None # no linenumber will be added
    return offset

def replace_element(elem, replacement):
    '''replace the content of an ElementTree Element by that of another
       one.'''
    elem.clear()
    elem.text = replacement.text
    elem.tail = replacement.tail
    elem.tag = replacement.tag
    elem.attrib = replacement.attrib
    elem[:] = replacement[:]
    return

def duplicate_dict(old):
    '''makes a shallow copy of a dict; appropriate to copy the attributes
    of an ElementTree Element.'''
    new = {}
    for key in old:
        new[key] = old[key]
    return new