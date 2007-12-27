'''utilities.py

   a collection of functions used in other modules.
'''
import re
import src.configuration as configuration
from src.universal import python_version

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

def sanitize_html_for_elementtree(text):
    '''performs a number of replacements on some html content so that
    it can hopefully be parsed appropriately by ElementTree.
    In a way, this is intended to be a very poor replacement for a subset of BeautifulSoup,
    to be used with Py3k'''
    # as of December 27, this is still work in progress...
    text = close_link(text)
    text = close_meta(text)
    text = close_input(text)
    text = close_img(text)
    text = remove_script(text)
    return text

link_pattern = re.compile('<link([^>]*)>')
def close_link(text):
    '''replace <link ....> by <link .../>'''
    text = link_pattern.sub( r'<link\1/>', text)
    return text

meta_pattern = re.compile('<meta([^>]*)>')
def close_meta(text):
    '''replace <meta ....> by <meta .../>'''
    text = meta_pattern.sub( r'<meta\1/>', text)
    return text

input_pattern = re.compile('<input([^>]*)>')
def close_input(text):
    '''replace <input ....> by <input .../>'''
    text = input_pattern.sub( r'<input\1/>', text)
    return text

img_pattern = re.compile('<img([^>]*)>')
def close_img(text):
    '''replace <img ....> by <img .../>'''
    text = img_pattern.sub( r'<img\1/>', text)
    return text

script_pattern = re.compile('<script([^<]*)</script>')
def remove_script(text):
    '''removing <script ....> ...</script>'''
    text = script_pattern.sub('', text)
    return text

begin_html ="""
<head>
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
end_html ="""
</body>
</html>
"""

def log_session():
    f = open(configuration.defaults.log_filename, 'w')
    f.write(begin_html)
    for uid in configuration.defaults.logging_uids:
        log_id = configuration.defaults.logging_uids[uid][0]
        vlam_type = configuration.defaults.logging_uids[uid][1]
        f.write("<h2>log_id = %s    <small>(uid=%s, type=%s)</small></h2>"%(log_id, uid, vlam_type))
        content = ''.join(configuration.defaults.log[log_id])
        f.write("<pre>"+content+"</pre>")
    f.write(end_html)
    f.close()