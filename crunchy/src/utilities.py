'''utilities.py

   a collection of functions used in other modules.
'''
import re
import configuration
import urlparse

level = 'display trusted'
def security_level(url):
    global level
    info = urlparse.urlsplit(url)
    if info.netloc == '':
        level = configuration.defaults.local_security
    else:
        level = configuration.defaults._get_site_security(info.netloc)
    return level

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
    lines = text.split('\n')
    top = 0
    for line in lines:
        if line.strip():
            break
        else:
            top += 1
    bottom = 0
    for line in lines[::-1]:
        if line.strip():
            break
        else:
            bottom += 1
    if bottom == 0:
        return '\n'.join(lines[top:])
    return '\n'.join(lines[top:-bottom])

def changeHTMLspecialCharacters(text):
    '''replace <>& by their escaped valued so they are displayed properly
       in browser.'''
    # this function is used in colourize.py and cometIO.py
    text = text.replace('&', '&amp;')
    text = text.replace('<', '&lt;')
    text = text.replace('>', '&gt;')
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