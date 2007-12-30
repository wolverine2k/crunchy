"""  file_service.py

Provides the means to save and load a file.
"""

from urllib import pathname2url
from subprocess import Popen
import os
import sys

# All plugins should import the crunchy plugin API via interface.py
from src.interface import python_version, config, plugin
# keep the following dependency as it is needed to set the value of
# defaults.alternate_python_version
from src.configuration import defaults

# The set of other "widgets/services" provided by this plugin
provides = set(["/save_file", "/load_file", "/save_and_run", "/run_external"])

DEBUG = False

def register():
    """The register() function is required for all plugins.
       In this case, we need to register three types of 'actions':
         1. an 'http handler' that deals with requests to save files
         2. an 'http handler' that deals with requests to load files.
         3. an 'http handler' that deals with request to save (Python)
            scripts and executes them as an external process.
       If needed, we could register two services using internal functions
         1. a custom service to save a file.
         2. a custom service to read content from a file.
       """
    plugin['register_http_handler']("/save_file", save_file_request_handler)
    plugin['register_http_handler']("/load_file", load_file_request_handler)
    plugin['register_http_handler']("/save_and_run%s"%plugin['session_random_id'],
                                        save_and_run_request_handler)
    plugin['register_http_handler']("/run_external%s"%plugin['session_random_id'],
                                        run_external_request_handler)
    plugin['register_http_handler']("/save_file_python_interpreter", save_file_python_interpreter_request_handler)
    plugin['register_http_handler']("/save_and_run_python_interpreter%s"%plugin['session_random_id'],
                                        save_and_run_python_interpreter_request_handler)
    plugin['register_http_handler']("/run_external_python_interpreter%s"%plugin['session_random_id'],
                                        run_external_python_interpreter_request_handler)

def save_file_request_handler(request):
    '''extracts the path & the file content from the request and
       saves the content in the path as indicated.'''
    if DEBUG:
        print("Entering save_file_request_handler.")
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
    if python_version >=3:
        data = str(data)
        if DEBUG:
            print('transformed data into str; data = ')
            print(data)
    if python_version >= 3:
        try:
            info = data.split("_::EOF::_")
        except:
            print('could not split data')
    else:
        info = data.split("_::EOF::_")
    if DEBUG:
        print("info = ")
        print(info)
    if python_version < 3:
        path = info[0].decode("utf-8")
    else:
        path = info[0]
    try:
        path = path.encode(sys.getfilesystemencoding())
    except:
        print("   Could not encode path.")
    #path = info[0]
    # the following is in case "_::EOF::_" appeared in the file content
    content = '_::EOF::_'.join(info[1:])
    save_file(path, content)
    return path

def save_and_run_request_handler(request):
    '''saves the code in a file in user specified directory and runs it
       from there'''
    if DEBUG:
        print("Entering save_and_run_request_handler.")
    path = save_file_request_handler(request)
    if DEBUG:
        print("  path = ")
        print(path)
    exec_external(path=path)

def run_external_request_handler(request):
    '''saves the code in a default location and runs it from there'''
    if DEBUG:
        print("Entering run_external_request_handler.")
    code = request.data
    request.send_response(200)
    request.end_headers()
    exec_external(code=code)

def load_file_request_handler(request):
    ''' reads a local file - most likely a Python file that will
        be loaded in an EditArea embeded editor.'''
    if DEBUG:
        print("Entering load_file_request_handler.")
    try:
        content = read_file(request.args['path'])
    except:
        print("  Exception found.")
        print("  path = " + request.args['path'])
        return 404
    request.send_response(200)
    request.end_headers()
    request.wfile.write(content)
    request.wfile.flush()

def save_file(full_path, content):
    """saves a file
    """
    if DEBUG:
        print("Entering save_file.")
    #full_path = full_path.encode(sys.getfilesystemencoding)
    if python_version >=3:
        full_path = str(full_path)
    try:
        f = open(full_path, 'w')
        f.write(content)
        f.close()
    except:
        print("  Could not save file; full_path =")
        print(full_path)
    if DEBUG:
        print("Leaving save_file")

def read_file(full_path):
    """reads a file
    """
    if DEBUG:
        print("Entering read_file.")
    try:
        f = open(full_path)
        content = f.read()
    except:
        print("  Could not open file " + full_path)
        return None
    if DEBUG:
        print("  full_path in read_file = " + full_path)
    return content

def exec_external(code=None,  path=None):
    """execute code in an external process with default interpreter
    """
    if DEBUG:
        print("Entering exec_external.")
    exec_external_python_version(code, path, alternate_version=False)


def save_file_python_interpreter_request_handler(request):
    '''extracts the path & the file content from the request and
       saves the content in the path as indicated.'''
    if DEBUG:
        print("Entering save_file_python_interpreter_request_handler.")
    data = request.data
    request.send_response(200)
    request.end_headers()
    if python_version >=3:
        data = str(data)
    info = data.split("_::EOF::_")
    if python_version < 3:
        path = info[1].decode("utf-8")
    else:
        path = info[1]
    try:
        path = path.encode(sys.getfilesystemencoding())
    except:
        print("  Could not encode path.")

    content = '_::EOF::_'.join(info[2:])
    save_file(path, content)
    
    if info[0]:
        defaults.alternate_python_version = info[0]
        # make sure we update also the indirect reference
        config['alternate_python_version'] = info[0]
    
    return path

def save_and_run_python_interpreter_request_handler(request):
    '''saves the code in a file in user specified directory and runs it
       from there'''
    if DEBUG:
        print("Entering save_and_run_python_interpreter_request_handler.")
    path = save_file_python_interpreter_request_handler(request)
    if DEBUG:
        print("  path = " + str(path))
    exec_external_python_version(path=path)

def run_external_python_interpreter_request_handler(request):
    '''saves the code in a default location and runs it from there'''
    if DEBUG:
        print("Entering run_external_python_interpreter_request_handler.")
    code = request.data
    request.send_response(200)
    request.end_headers()
    exec_external_python_version(code=code)

def exec_external_python_version(code=None,  path=None, alternate_version=True,
                                 write_over=True):
    """execute code in an external process with the choosed python intepreter
    currently works under:
        * Windows NT
        * GNOME (Tested)
        * OS X
    This also needs to be tested for KDE
    and implemented some form of linux fallback (xterm?)
    """
    if DEBUG:
        print("Entering exec_external_python_interpreter.")
        print("path =" + str(path))
        print("alternate version = " + str(alternate_version))
    if python_version >= 3:
        path = str(path)
    if alternate_version:
        python_interpreter = config['alternate_python_version']
    else:
        python_interpreter = 'python'  # default interpreter
    if path is None:
        path = os.path.join(config['temp_dir'], "temp.py")
    if os.name == 'nt' or sys.platform == 'darwin':
        current_dir = os.getcwd()
        target_dir, fname = os.path.split(path)
    if code is not None and write_over:
        try:
            filename = open(path, 'w')
            filename.write(code)
            filename.close()
        except:
            print("Could not save file in file_service.exec_external_python_version()")
        
    if os.name == 'nt':
        os.chdir(target_dir) # change dir so as to deal with paths that
                             # include spaces
        try:
            Popen(["command", ('/c start %s %s'%(python_interpreter,fname))])
        except:
            Popen(["cmd.exe", ('/c start %s %s'%(python_interpreter,fname))])
            print("  Launching program did not work with command; used cmd.exe")
        os.chdir(current_dir)
    elif sys.platform == 'darwin': # a much more general method can be found
                                   # in SPE, Stani's Python Editor - Child.py
        activate = 'tell application "Terminal" to activate'
        script = r"cd '\''%s'\'';%s '\''%s'\'';exit"%(target_dir, python_interpreter, fname)
        do_script = r'tell application "Terminal" to do script "%s"'%script
        command =  "osascript -e '%s';osascript -e '%s'"%(activate, do_script)
        os.popen(command)
    elif os.name == 'posix':
        try:
            os.spawnlp(os.P_NOWAIT, 'gnome-terminal', 'gnome-terminal', '-x', python_interpreter, '%s'%path)
        except:
            try:
                os.spawnlp(os.P_NOWAIT, 'konsole', 'konsole',
                                '-x', python_interpreter, '%s'%path)
            except:
                raise NotImplementedError
    else:
        raise NotImplementedError

