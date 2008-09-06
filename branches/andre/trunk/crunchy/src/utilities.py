'''utilities.py

   a collection of functions used in other modules.

   unit tests in test_utilities.rst
'''
import re
from src.interface import config, plugin, Element, SubElement, names

import copy

COUNT = 0
def uidgen(username):  # tested
    """an suid (session unique ID) generator
    """
    global COUNT
    COUNT += 1
    uid = str(COUNT)
    # uid's get passed around to various modules; by associating a uid
    # to a username, we facilitate adapting behaviour of a given function/method
    # to the preferences of the user.
    names[uid] = username
    # note that Crunchy's uid's are usually composed of TWO uid's - one for
    # the page, the other for a given html "object".
    return uid

def extract_log_id(vlam):  # tested
    '''given a vlam of the form
       "keyword  ... log_id=(some id) ..."
       extracts the value of the log id which would be "some id" in the
       example above.

       Valid id can contain any letter, number, spaces as well as
       any of . , : _
    '''
    # This function should be used in all vlam_plugins that
    # process code inside <pre>.
    if 'log_id' in vlam:
        res = re.search(r'\s+log_id\s*=\s*\(([\s\w.:,]+)\)', vlam)
        return res.groups()[0].strip()
    else:
        return ''

def insert_file_browser(parent, text, action):  # tested
    '''inserts a local file browser object in an html page'''
    # add a unique id to allow more than one file_browser of a given type
    # on a page; use the "action" [e.g. /local, /rst, etc.] as part of the
    # name so that it can be easily parsed by a human reader when viewing
    # the html source.
    name1 = 'browser_%s' % action[1:] + uidgen(None)
    name2 = 'submit_%s' % action[1:] + uidgen(None)
    form1 = SubElement(parent, 'form', name=name1)
    SubElement(form1, 'input', type='file', name='filename', size='80',
               onblur = "document.%s.url.value="%name2+\
                        "document.%s.filename.value"%name1)
    SubElement(form1, 'br')

    form2 = SubElement(parent, 'form', name=name2, method='get',
                action=action)
    SubElement(form2, 'input', type='hidden', name='url')
    input3 = SubElement(form2, 'input', type='submit', value=text)
    input3.attrib['class'] = 'crunchy'
    return

def trim_empty_lines_from_end(text):  # tested
    '''remove blank lines at beginning and end of code sample'''
    # this is needed to prevent indentation error if a blank line
    # with spaces at different levels is inserted at the end or beginning
    # of some code to be executed.
    # This function is used in interpreter.py and colourize.py.
    return text.strip(' \r\n')

def changeHTMLspecialCharacters(text):  # tested
    '''replace <>& by their escaped valued so they are displayed properly
       in browser.'''
    # this function is used in colourize.py and cometIO.py
    text = text.replace('&', '&amp;')
    text = text.replace('<', '&lt;')
    text = text.replace('>', '&gt;')
    return text

def insert_markup(elem, uid, vlam, markup, interactive_type):
    '''clears an element and inserts the new markup inside it'''
    elem.clear()
    elem.tag = "div"
    elem.attrib["id"] = "div_"+uid
    elem.attrib['class'] = interactive_type # 'editor', 'doctest', 'interpreter'
    if not "no_pre" in vlam:
        try:
            new_div = Element("div")
            new_div.append(markup)
            new_div.attrib['class'] = 'sample_python_code'
            elem.insert(0, new_div)
        except AssertionError:  # this should never happen
            elem.insert(0, Element("br"))
            bold = Element("b")
            span = Element("span")
            span.text = "AssertionError from ElementTree"
            bold.append(span)
            elem.insert(1, bold)

def wrap_in_div(elem, uid, vlam, interactive_type):
    '''wraps a styled code inside a div'''
    elem_copy = copy.deepcopy(elem)
    elem.clear()
    elem.text = ''
    elem.tag = "div"
    elem.attrib["id"] = "div_"+uid
    elem.attrib['class'] = interactive_type # 'editor', 'doctest', etc.
    if not "no_pre" in vlam:
        try:
            elem.append(elem_copy)
        except AssertionError:  # this should never happen
            elem.insert(0, Element("br"))
            bold = Element("b")
            span = Element("span")
            span.text = "AssertionError from ElementTree"
            bold.append(span)
            elem.insert(1, bold)

def extract_code(elem):
    """extract all the text (Python code) from a marked up
    code sample encoded as an ElementTree structure, but converting
    <br/> into "\n" and removing "\r" which are not
    expected in Python code; inspired by F.Lundh's gettext()

    It also remove blank lines at beginning and end of code sample.
    """
    # The removal of blank lins is needed to prevent indentation error
    # if a blank line with spaces at different levels is inserted at the end
    # or beginning of some code to be executed.
    text = elem.text or ""
    for node in elem:
        text += extract_code(node)
        if node.tag == "br":
            text += "\n"
        if node.tail:
            text += node.tail
    text = text.replace("\r", "")
    return text.strip(' \n')

def is_interpreter_session(py_code):
    '''determine if the python code corresponds to a simulated
       interpreter session'''
    lines = py_code.split('\n')
    for line in lines:
        if line.strip():  # look for first non-blank line
            if line.startswith(">>>"):
                return True
            else:
                return False

def extract_code_from_interpreter(python_code):
    """ Strips fake interpreter prompts from html code meant to
        simulate a Python session, and remove lines without prompts, which
        are supposed to represent Python output.

        Assumes any '\r' characters have been removed from the Python code.
    """
    if not python_code:
        return
    lines = python_code.split('\n')
    new_lines = [] # will contain the extracted python code

    for line in lines:
        if line.startswith(">>> "):
            new_lines.append(line[4:].rstrip())
        elif line.rstrip() == ">>>": # tutorial writer may forget the
                                     # extra space for an empty line
            new_lines.append(' ')
        elif line.startswith("... "):
            new_lines.append(line[4:].rstrip())
        elif line.rstrip() == "...": # tutorial writer may forget the extra
            new_lines.append('')     # space for an empty line
        else: # output result
            pass
    python_code = '\n'.join(new_lines)
    return python_code


begin_html = """
<html>
<head>
<title>Crunchy Log</title>
<link rel="stylesheet" type="text/css" href="/crunchy.css">
</head>
<body>
<h1>Crunchy Session Log</h1>
<p>In what follows, the log_id is the name given by the tutorial writer
to the element to be logged, the uid is the unique identifier given
to an element on a page by Crunchy.  If the page gets reloaded, uid
will change but not log_id.
</p><p>By convention, original code from the page is styled using the
Crunchy defaults.
</p>
"""
end_html = """
</body>
</html>
"""

def log_session(username):
    '''create a log of a session in a file'''
    f = open(config[username]['log_filename'], 'w')
    f.write(begin_html)
    for uid in config[username]['logging_uids']:
        log_id = config[username]['logging_uids'][uid][0]
        vlam_type = config[username]['logging_uids'][uid][1]
        f.write("<h2>log_id = %s    <small>(uid=%s, type=%s)</small></h2>"%(log_id, uid, vlam_type))
        content = ''.join(config[username]['log'][log_id])
        f.write("<pre>"+content+"</pre>")
    f.write(end_html)
    f.close()

# Some useful function for including some images "dynamically" within
# web pages.  See doc_code_check.py for a sample use.

def append_checkmark(pageid, parent_uid):
    '''appends a checkmark image'''
    attributes = {'width':32, 'height':32, 'src':"/ok.png"}
    append_image(pageid, parent_uid, attributes)

def append_warning(pageid, parent_uid):
    '''appends a warning image'''
    attributes = {'width':32, 'height':32, 'src':"/warning.png"}
    append_image(pageid, parent_uid, attributes)

def append_image(pageid, parent_uid, attributes):
    '''appends an image using dhtml techniques
    '''
    child_uid = parent_uid + "_child"
    plugin['exec_js'](pageid,
                      """var currentDiv = document.getElementById("%s");
                      var newTag = document.createElement("img");
                      newTag.setAttribute('id', '%s');
                      currentDiv.appendChild(newTag);
                      """%(parent_uid, child_uid))
    tag_attr = []
    for key in attributes:
        tag_attr.append("document.getElementById('%s').%s='%s';"%(
                                child_uid, key, attributes[key]))
    plugin['exec_js'](pageid, '\n'.join(tag_attr))
