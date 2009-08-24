'''utilities.py

   a collection of functions used in other modules.

   unit tests in test_utilities.rst
'''

import codecs
import copy
import re
import sys
import textwrap
from os.path import join
from src.interface import (config, plugin, Element, SubElement, names,
                           StringIO, server, translate)
_ = translate['_']
root_path = join(config['crunchy_base_dir'], "server_root/")

python_version = sys.version_info[0] + sys.version_info[1]/10.0
if python_version < 3:
    from urllib import FancyURLopener
else:
    from urllib.request import FancyURLopener

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

def parse_vlam(vlam):
    parts = vlam.split()
    ret = {}
    for part in parts:
        pp = part.split('=', 1)
        if len(pp) >= 2:
            ret[pp[0]] = pp[1]
        else:
            ret[pp[0]] = ""
    return ret
def trim_empty_lines_from_end(text):  # tested
    '''remove blank lines at beginning and end of code sample'''
    # this is needed to prevent indentation error if a blank line
    # with spaces at different levels is inserted at the end or beginning
    # of some code to be executed.
    return text.strip(' \r\n')

entity_pattern = re.compile("(&amp;#\d{1,4});")
def recover_entity_pattern(match):
    text = match.group().replace("&amp;", "&")
    return text

def changeHTMLspecialCharacters(text):  # tested
    '''replace <>& by their escaped valued so they are displayed properly
       in browser.'''
    # this function is used in colourize.py and cometIO.py
    text = text.replace('&', '&amp;')
    text = text.replace('<', '&lt;')
    text = text.replace('>', '&gt;')
    # this reverse changes like from &amp;1234; to &#1234;
    text = entity_pattern.sub(recover_entity_pattern, text)
    return text

def unChangeHTMLspecialCharacters(text):
    '''reverse of changeHTMLspecialCharacters'''
    text = text.replace('&lt;', '<')
    text = text.replace('&gt;', '>')
    text = text.replace('&amp;', '&')
    return text

def escape_for_javascript(text):
    '''as the name indicates, escape some characters so that they can be
       safely included in javascript'''
    text = text.replace("\\", "\\\\")
    text = text.replace("'", r"\'")
    text = text.replace('"', r'\"')
    text = text.replace("\n", r"\n")
    text = text.replace("\r", r"\r")
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

def wrap_in_div(elem, uid, vlam, element_type, show_vlam):
    '''wraps a styled code inside a div'''
    elem_copy = copy.deepcopy(elem)
    elem.clear()
    elem.text = ''
    elem.tag = "div"
    elem.attrib["id"] = "div_"+uid
    username = names[uid.split("_")[0]]
    # element_type = 'editor', 'doctest', etc.
    elem.attrib['class'] = element_type + " " + config[username]['style']
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
            return
    if show_vlam is not None:
        elem.insert(0, show_vlam)

def extract_code(elem):
    """extract all the text (Python code) from a marked up
    code sample encoded as an ElementTree structure, but converting
    <br/> into "\n" and removing "\r" which are not
    expected in Python code; inspired by F.Lundh's gettext()

    It also remove blank lines at beginning and end of code sample.

    It also removes common leading blank, in case the code written by
    a tutorial writer is uniformly indented.  This is the case sometimes
    for python code extracted by docutils.
    """
    text = elem.text or ""
    for node in elem:
        text += extract_code(node)
        if node.tag == "br":
            text += "\n"
        if node.tail:
            text += node.tail
    text = text.replace("\r", "")
    text = textwrap.dedent(text)
    text = trim_empty_lines_from_end(text)
    return text

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
    child_uid = parent_uid + uidgen("_")
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

# This should match the charset in meta tags with XHTML or HTML tag
# endings. A more robust solution would be an HTML parser, but for
# this it might be overkill.
META_CONTENT_RE = re.compile('<meta.*?charset\s*?=(.*?)"\s*?/?>'.encode('ascii'),
                             re.DOTALL)

def meta_encoding(text):
    """Given the text of an HTML document *as a bytestring in an
    ASCII-superset encoding* or Unicode, returns the encoding read off
    from <meta charset="..."> and returns it. If none found, returns
    None."""

    encoding = None

    # Byte regexp matching bytes here. It's important that this is
    # *not* Unicode since we do not know the encoding yet. But! we can
    # assume that whatever encoding it is, it's a superset of ASCII,
    # hence the bytes.
    m = META_CONTENT_RE.search(text)

    if m and m.groups():
        # And now, back to Unicode.
        encoding = m.group(1).strip().decode('ascii')

    return encoding

def meta_content_open(path):
    """Returns a Unicode file-like object using the codecs module,
    detecting an encoding stored in the <meta content="..."> attribute
    if needed. Falls back to UTF-8."""

    f = open(path, 'rb')
    encoding = meta_encoding(f.read()) or 'utf8'
    f.close()
    return codecs.open(path, encoding=encoding)

def unicode_urlopen(url, accept_lang=None):
    """Returns a *Unicode* file-like object for non-local documents.
    Client must ensure that the URL points to non-binary data. Pass in
    an Accept-Language value to configure the FancyURLopener we
    use."""

    opener = FancyURLopener()

    if accept_lang:
        opener.addheader("Accept-Language", accept_lang)

    # We want to convert the bytes file-like object returned by
    # urllib, which is bytes in both Python 2 and Python 3
    # fortunately, and turn it into a Unicode file-like object
    # with a little help from our StringIO friend.
    page = opener.open(url)
    encoding = page.headers['content-type']
    encoding = encoding.split('charset=')
    if len(encoding) > 1:
        encoding = encoding[-1]
        page = page.read().decode(encoding)
    else:
        page = page.read()
        encoding = meta_encoding(page) or 'utf8'
        page = page.decode(encoding)

    page = StringIO(page)
    return page

def account_exists(request):
    '''Verify that we have a valid user account so that we can proceed.'''
    try:
        dummy = request.crunchy_username
    except:
        request.crunchy_username = "Unknown User"
    return True
