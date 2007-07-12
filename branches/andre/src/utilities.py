'''utilities.py

   a collection of functions used in other modules.
'''
import re
import configuration

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
<style>
/* from colourize.py */
.py_keyword{color: #336699; /* blue */
            font-weight: bold;} /* EditArea does not support font-weight */
.py_number{color: #000000;} /* EditArea does not recognize number; keep black.*/
.py_comment{color: gray;}
.py_string{color: #660066;} /* Indigo */
.py_variable{color: #000000;}
.py_op{color: #993300; font-weight:bold;}
.py_builtins{color: #009900;} /* builtins and string functions */
.py_stdlib{color: #009900;} /* standard library modules */
.py_special{color: #006666;} /* special method of the form __x__ */
.py_linenumber{font-size: small; color: #666666;}
.py_prompt{color:blue; }
.py_output{color:blue;}
.py_warning{background-color:yellow; font-size: large; font-weight: bold;}
.py_pre{text-align: left;}

/* adapted from io_widget.py */
.stdout {
    color: blue;
}

.stderr {
    font-weight: bold;
    color: red;
}

.stdin{
    font-weight: bold;
    color:darkgreen;
}
</style>
</head>
<body>
<h1>Crunchy Session Log</h1>
"""
end_html ="""
</body>
</html>
"""

def log_session():
    f = open(configuration.defaults.log_filename, 'w')
    f.write(begin_html)
    for uid in configuration.defaults.logging_uids:
        log_id = configuration.defaults.logging_uids[uid]
        f.write("<h2>log_id = %s</h2>"%log_id)
        content = ''.join(configuration.defaults.log[log_id])
        f.write("<pre>"+content+"</pre>")
    f.write(end_html)
    f.close()