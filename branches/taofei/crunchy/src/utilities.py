'''utilities.py

   a collection of functions used in other modules.
'''
import re
from src.interface import python_version, config, plugin, SubElement

COUNT = 0
def uidgen():
    """an suid (session unique ID) generator
    """
    global COUNT
    COUNT += 1
    return str(COUNT)

def extract_log_id(vlam):
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

def insert_file_browser(parent, text, action):
    '''inserts a local file browser object in an html page'''
    # add a unique id to allow more than one file_browser of a given type
    # on a page; use the "action" [e.g. /local, /rst, etc.] as part of the
    # name so that it can be easily parsed by a human reader when viewing
    # the html source.
    name1 = 'browser_%s' % action[1:] + uidgen()
    name2 = 'submit_%s' % action[1:] + uidgen()
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

def trim_empty_lines_from_end(text):
    '''remove blank lines at beginning and end of code sample'''
    # this is needed to prevent indentation error if a blank line
    # with spaces at different levels is inserted at the end or beginning
    # of some code to be executed.
    # This function is used in interpreter.py and colourize.py.
    return text.strip(' \r\n')

def changeHTMLspecialCharacters(text):
    '''replace <>& by their escaped valued so they are displayed properly
       in browser.'''
    # this function is used in colourize.py and cometIO.py
    if python_version >= 3:
        text = str(text)
    text = text.replace('&', '&amp;')
    text = text.replace('<', '&lt;')
    text = text.replace('>', '&gt;')
    return text

def unChangeHTMLspecialCharacters(text):
    '''reverse of changeHTMLspecialCharacters'''
    if python_version >= 3:
        text = str(text)
    text = text.replace('&lt;', '<')
    text = text.replace('&gt;', '>')
    text = text.replace('&amp;', '&')
    return text

def escape_for_javascript(text):
    if python_version >= 3:
        text = str(text)
    text = text.replace("\\", "\\\\")
    text = text.replace("'", r"\'")
    text = text.replace('"', r'\"')
    text = text.replace("\n", r"\n")
    text = text.replace("\r", r"\r")
    return text

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

def log_session():
    '''create a log of a session in a file'''
    f = open(config['log_filename'], 'w')
    f.write(begin_html)
    for uid in config['logging_uids']:
        log_id = config['logging_uids'][uid][0]
        vlam_type = config['logging_uids'][uid][1]
        f.write("<h2>log_id = %s    <small>(uid=%s, type=%s)</small></h2>"%(log_id, uid, vlam_type))
        content = ''.join(config['log'][log_id])
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
