"""Plugin for loading and transforming python files."""

import os
from src.interface import plugin, interactive
from src.utilities import changeHTMLspecialCharacters

provides = set(["/py"])
requires = set(["filtered_dir", "insert_file_tree"])

def register():
    """Registers new http handler and new widget for loading ReST files"""
    plugin['register_http_handler']("/py", load_python)
    plugin['register_tag_handler']("div", "title", "local_python_file", insert_load_python)
    plugin['add_vlam_option']('power_browser', 'python')
    plugin['register_http_handler']("/jquery_file_tree_py", jquery_file_tree_py)
    plugin['register_service']("local_python", insert_load_python)

class Python_file(object):
    """Simplest object that vlam will take as a file"""
    def __init__(self, data):
        self._data = data
    def read(self):
        '''
        return the only class attribute as a string; used to simulate a file
        '''
        return self._data

def load_python(request):
    """Loads python file from disk, inserts it into an html template
       and then creates new page
       """
    url = request.args["url"]
    # we may want to use urlopen for this?
    python_code = open(url).read()
    python_code = changeHTMLspecialCharacters(python_code)

    if interactive:
        interpreter_python_code = "__name__ = '__main__'\n" + python_code
    else:
        interpreter_python_code = python_code
    html_template = """
    <html>
    <head><title>%s</title></head>
    <body>
    <h1> %s </h1>
    <p>You can either use the interpreter to interact "live" with the
    Python file, or the editor.  To "feed" the file to the interpreter,
    first click on the editor icon next to it, and then click on the
    "Execute" button.
    <h3 > Using the interpreter </h3>
    <p>Click on the editor icon and feed the code to the interpreter.</p>
    <pre title="interpreter no_pre"> %s </pre>
     <h3 > Using the editor</h3>
    <pre title="editor"> %s </pre>

    </body>
    </html>
    """ % (url, url, interpreter_python_code, python_code)

    fake_file = Python_file(html_template)
    page = plugin['create_vlam_page'](fake_file, url, local=True,
                                      username=request.crunchy_username)

    request.send_response(200)
    request.end_headers()
    request.wfile.write(page.read().encode('utf-8'))

def insert_load_python(page, elem, uid):
    "Inserts a javascript browser object to load a local python file."
    plugin['services'].insert_file_tree(page, elem, uid, '/jquery_file_tree_py',
                                '/py', 'Load local Python file', 'Load Python file')
    return

def filter_py(filename, basepath):
    '''filters out all files and directory with filename so as to include
       only files whose extensions are ".py" with the possible
       exception of ".crunchy" - the usual crunchy default directory.
    '''
    if filename.startswith('.') and filename != ".crunchy":
        return True
    else:
        fullpath = os.path.join(basepath, filename)
        if os.path.isdir(fullpath):
            return False   # do not filter out directories
        ext = os.path.splitext(filename)[1][1:] # get .ext and remove dot
        if ext == 'py':
            return False
        else:
            return True

def jquery_file_tree_py(request):
    '''extract the file information and formats it in the form expected
       by the jquery FileTree plugin, but excludes some normally hidden
       files or directories, to include only python files.'''
    plugin['services'].filtered_dir(request, filter_py)
    return
