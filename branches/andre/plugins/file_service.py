"""  file_service.py

Provides the means to save and load a file.
"""

from urllib import pathname2url
from subprocess import Popen
import os
import sys

# All plugins should import the crunchy plugin API
import CrunchyPlugin

# The set of other "widgets/services" provided by this plugin
provides = set(["/save_file", "/load_file", "/save_and_run", "/run_external"])

def register():
    """The register() function is required for all plugins.
       In this case, we need to register three types of 'actions':
         1. an 'http handler' that deals with requests to save files
         2. an 'http handler' that deals with requuests to load files.
         3. an 'http handler' that deals with request to save (Python)
            scripts and executes them as an external process.
       If needed, we could register two services using internal functions
         1. a custom service to save a file.
         2. a custom service to read content from a file.
       """
    CrunchyPlugin.register_http_handler("/save_file", save_file_request_handler)
    CrunchyPlugin.register_http_handler("/load_file", load_file_request_handler)
    CrunchyPlugin.register_http_handler("/save_and_run%s"%CrunchyPlugin.session_random_id,
                                        save_and_run_request_handler)
    CrunchyPlugin.register_http_handler("/run_external%s"%CrunchyPlugin.session_random_id,
                                        run_external_request_handler)

def save_file_request_handler(request):
    '''extracts the path & the file content from the request and
       saves the content in the path as indicated.'''
    data = request.data
    request.send_response(200)
    request.end_headers()
    # We've sent the file (content) and filename (path) in one
    # "document" written as path+"_::EOF::_"+content; the assumption
    # is that "_::EOF::_" would never be part of a filename/path.
    #
    # There could be more robust ways, like perhaps sending a string
    # containing the path length separated from the path and the content by
    # a separator where we check to make sure the path recreated
    # is of the correct length - but it probably would be an overkill.
    info = data.split("_::EOF::_")
## -------encoding not yet implemented; this is from the "old" crunchy
##    path = info[0].decode(translation.current_page_encoding)
##    path = path.encode(sys.getdefaultencoding())
    path = info[0]
    # the following is in case "_::EOF::_" appeared in the file content
    content = '_::EOF::_'.join(info[1:])
    save_file(path, content)
    return path

def save_and_run_request_handler(request):
    '''saves the code in a file in user specified directory and runs it
       from there'''
    path = save_file_request_handler(request)
    exec_external(path=path)

def run_external_request_handler(request):
    '''saves the code in a default location and runs it from there'''
    code = request.data
    request.send_response(200)
    request.end_headers()
    exec_external(code=code)

def load_file_request_handler(request):
    ''' reads a local file - most likely a Python file that will
        be loaded in an EditArea embeded editor.'''
    path = pathname2url(request.args['path'])
    try:
        content = read_file(path)
    except:
        print "exception found"
        print "path=", path
        return 404
    request.send_response(200)
    request.end_headers()
    request.wfile.write(content)
    request.wfile.flush()

def save_file(full_path, content):
    """saves a file
    """
    f = open(full_path, 'w')
    f.write(content)
    f.close()

def read_file(full_path):
    """reads a file
    """
    f = open(full_path)
    content = f.read()
    return content

def exec_external(code=None,  path=None):
    """execute code in an external process
    currently works under:
        * Windows NT (tested)
        * GNOME
        * OS X
    This also needs to be tested for KDE
    and implemented some form of linux fallback (xterm?)
    """
    if path is None:
        path = os.path.join(os.path.expanduser("~"), ".crunchy", "temp.py")
    if os.name == 'nt' or sys.platform == 'darwin':
        current_dir = os.getcwd()
        target_dir, fname = os.path.split(path)

    if code is not None:
        filename = open(path, 'w')
        filename.write(code)
        filename.close()

    if os.name == 'nt':
        os.chdir(target_dir) # change dir so as to deal with paths that
                             # include spaces
        Popen(["cmd.exe", ('/c start python %s'%fname)])
        os.chdir(current_dir)
    elif sys.platform == 'darwin':  # a much more general method can be found
                                 # in SPE, Stani's Python Editor - Child.py
        activate = 'tell application "Terminal" to activate'
        script = r"cd '\''%s'\'';python '\''%s'\'';exit"%(target_dir, fname)
        do_script = r'tell application "Terminal" to do script "%s"'%script
        command =  "osascript -e '%s';osascript -e '%s'"%(activate, do_script)
        os.popen(command)
    elif os.name == 'posix':
        try:
            os.spawnlp(os.P_NOWAIT, 'gnome-terminal', 'gnome-terminal',
                                '-x', 'python', '%s'%path)
        except:
            try: # untested
                os.spawnlp(os.P_NOWAIT, 'konsole', 'konsole',
                                '-x', 'python', '%s'%path)
            except:
                raise NotImplementedError
    else:
        raise NotImplementedError
