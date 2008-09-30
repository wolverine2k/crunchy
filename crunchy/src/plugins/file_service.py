"""  file_service.py

Provides the means to save and load a file.
"""

from subprocess import Popen
import os
import sys
import urllib

# All plugins should import the crunchy plugin API via interface.py
from src.interface import config, plugin, SubElement

# The set of other "widgets/services" provided by this plugin
provides = set(["/save_file", "/load_file", "/save_and_run", "/run_external"])

DEBUG = False

# Sorted list of ('terminal', 'parameters to start a program') for linux systems
linux_terminals = (
    ('xdg-terminal', ''),
    ('gnome-terminal', '-x'),
    ('konsole', '-e'),
    ('xfce4-terminal', '-x'),
    ('xterm', '-e'),
)

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
    plugin['register_tag_handler']("div", "title", "file_tree",
                                          insert_file_tree)
    plugin['register_http_handler']("/save_file", save_file_request_handler)
    plugin['register_http_handler']("/load_file", load_file_request_handler)
    plugin['register_http_handler']("/jquery_file_tree", jquery_file_tree)
    plugin['register_http_handler']("/save_and_run%s"%plugin['session_random_id'],
                                        save_and_run_request_handler)
    plugin['register_http_handler']("/run_external%s"%plugin['session_random_id'],
                                        run_external_request_handler)
    plugin['register_http_handler']("/save_file_python_interpreter", save_file_python_interpreter_request_handler)
    plugin['register_http_handler']("/save_and_run_python_interpreter%s"%plugin['session_random_id'],
                                        save_and_run_python_interpreter_request_handler)
    plugin['register_http_handler']("/run_external_python_interpreter%s"%plugin['session_random_id'],
                                        run_external_python_interpreter_request_handler)

def filter_default(filename, basepath=None):
    '''filters out all files and directory with filename starting with "."
       except for ".crunchy".'''
    if filename.startswith('.') and filename != ".crunchy":
        return True
    else:
        return False

def filter_html(filename, basepath):
    '''filters out all files and directory with filename so as to include
       only files whose extensions start with ".htm" with the possible
       exception of ".crunchy" - the usual crunchy default directory.
    '''
    if filename.startswith('.') and filename != ".crunchy":
        return True
    else:
        fullpath = os.path.join(basepath, filename)
        if os.path.isdir(fullpath):
            return False   # do not filter out directories
        ext = os.path.splitext(filename)[1][1:] # get .ext and remove dot
        if ext.startswith("htm"):
            return False
        else:
            return True

def filtered_dir(request, filter=filter_default):
    '''returns the file listing from a directory,
       satisfying a given filter function,
       in a form suitable for the jquery FileTree plugin.'''
    ul = ['<ul class="jqueryFileTree" style="display: none;">']
    # request.data is of the form "dir=SomeDirectory"
    try:
        d = urllib.unquote(request.data)[4:]
        d = urllib.unquote(d)  # apparently need to call it twice on windows
        for f in os.listdir(d):
            if filter(f, d):
                continue
            ff = os.path.join(d, f)
            if os.path.isdir(ff):
                ul.append('<li class="directory collapsed"><a href="#" rel="%s/">%s</a></li>' % (ff,f))
            else:
                ext = os.path.splitext(f)[1][1:] # get .ext and remove dot
                ul.append('<li class="file ext_%s"><a href="#" rel="%s">%s</a></li>' % (ext,ff,f))
        ul.append('</ul>')
    except Exception,e:
        ul.append('Could not load directory: %s' % str(e))
    ul.append('</ul>')
    request.wfile.write(''.join(ul))
    return

def jquery_file_tree(request):
    '''extract the file information and formats it in the form expected
       by the jquery FileTree plugin, but excludes some normally hidden
       files or directories.'''
    filtered_dir(request, filter_html)
    return

def insert_file_tree(page, elem, uid):
    '''inserts a file tree object in a page.'''
    if 'display' not in config[page.username]['page_security_level'](page.url):
        if not page.includes("jquery_file_tree"):
            page.add_include("jquery_file_tree")
            page.insert_js_file("/javascript/jquery.filetree.js")
            page.insert_css_file("/css/jquery.filetree.css")
    else:
        return
    tree_id = "tree_" + uid
    form_id = "form_" + uid
    root = os.path.splitdrive(__file__)[0] + "/"  # use base directory for now
    js_code =  """$(document).ready( function() {
        $('#%s').fileTree({
          root: '%s',
          script: '/jquery_file_tree',
          expandSpeed: -1,
          collapseSpeed: -1,
          multiFolder: false
        }, function(file) {
            document.getElementById('%s').value=file;
        });
    });
    """ % (tree_id, root, form_id)
    page.add_js_code(js_code)
    elem.text = 'File Tree Browser'
    elem.attrib['class'] = "filetree_wrapper"

    form = SubElement(elem, 'form', name='url', size='80', method='get',
                       action='/local')
    SubElement(form, 'input', name='url', size='80', id=form_id)
    input_ = SubElement(form, 'input', type='submit',
                           value='Load local tutorial')
    input_.attrib['class'] = 'crunchy'

    file_div = SubElement(elem, 'div')
    file_div.attrib['id'] = tree_id
    file_div.attrib['class'] = "filetree_window"
    return


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
    info = data.split("_::EOF::_")
    if DEBUG:
        print("info = ")
        print(info)
    path = info[0].decode("utf-8")
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
    exec_external(path=path, username=request.crunchy_username)

def run_external_request_handler(request):
    '''saves the code in a default location and runs it from there'''
    if DEBUG:
        print("Entering run_external_request_handler.")
    code = request.data
    request.send_response(200)
    request.end_headers()
    exec_external(code=code, username=request.crunchy_username)

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

def save_file(full_path, content):  # tested
    """saves a file
    """
    if DEBUG:
        print("Entering save_file.")
    #full_path = full_path.encode(sys.getfilesystemencoding)
    try:
        f = open(full_path, 'w')
        f.write(content)
        f.close()
    except:
        print("  Could not save file; full_path =")
        print(full_path)
    if DEBUG:
        print("Leaving save_file")

def read_file(full_path):  # tested
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

def exec_external(code=None,  path=None, username=None):
    """execute code in an external process with default interpreter
    """
    if DEBUG:
        print("Entering exec_external.")
    exec_external_python_version(code, path, alternate_version=False,
                                 username=username)

def save_file_python_interpreter_request_handler(request):
    '''extracts the path & the file content from the request and
       saves the content in the path as indicated.'''
    if DEBUG:
        print("Entering save_file_python_interpreter_request_handler.")
    data = request.data
    request.send_response(200)
    request.end_headers()
    info = data.split("_::EOF::_")
    path = info[1]
    try:
        path = path.encode(sys.getfilesystemencoding())
    except:
        print("  Could not encode path.")

    content = '_::EOF::_'.join(info[2:])
    save_file(path, content)
    if DEBUG:
        print "info =", info
    if info[0]:
        username = request.crunchy_username
        config[username]['alternate_python_version'] = info[0]
        # the following updates the value stored in configuration.defaults
        config[username]['_set_alternate_python_version'](info[0])
    return path

def save_and_run_python_interpreter_request_handler(request):
    '''saves the code in a file in user specified directory and runs it
       from there'''
    if DEBUG:
        print("Entering save_and_run_python_interpreter_request_handler.")
    path = save_file_python_interpreter_request_handler(request)
    if DEBUG:
        print("  path = " + str(path))
    exec_external_python_version(path=path, username=request.crunchy_username)

def run_external_python_interpreter_request_handler(request):
    '''saves the code in a default location and runs it from there'''
    if DEBUG:
        print("Entering run_external_python_interpreter_request_handler.")
    code = request.data
    request.send_response(200)
    request.end_headers()
    exec_external_python_version(code=code, username=request.crunchy_username)

def exec_external_python_version(code=None,  path=None, alternate_version=True,
                                 write_over=True, username=None):
    """execute code in an external process with the choosed python intepreter
    currently works under:
        * Windows NT
        * GNOME/KDE/XFCE/xterm (Tested)
        * OS X
    """
    if DEBUG:
        print("Entering exec_external_python_interpreter.")
        print("path =" + str(path))
        print("alternate version = " + str(alternate_version))
    if alternate_version:
        python_interpreter = config[username]['alternate_python_version']
    else:
        python_interpreter = 'python'  # default interpreter
    if path is None:
        path = os.path.join(config[username]['temp_dir'], "temp.py")
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
            Popen(["command", ('/c start %s %s' % (python_interpreter, fname))])
        except:
            Popen(["cmd.exe", ('/c start %s %s' % (python_interpreter, fname))])
            print("  Launching program did not work with command; used cmd.exe")
        os.chdir(current_dir)
    elif sys.platform == 'darwin': # a much more general method can be found
                                   # in SPE, Stani's Python Editor - Child.py
        activate = 'tell application "Terminal" to activate'
        script = r"cd '\''%s'\'';%s '\''%s'\'';exit" % (target_dir,
                                                    python_interpreter, fname)
        do_script = r'tell application "Terminal" to do script "%s"' % script
        command =  "osascript -e '%s';osascript -e '%s'" % (activate, do_script)
        os.popen(command)
    elif os.name == 'posix':
        terminals_to_try = list(linux_terminals)
        while terminals_to_try:
            (terminal, start_parameter) = terminals_to_try[0]
            try:
                if DEBUG:
                    print 'Try to lauch "%s %s %s %s"' % (terminal, start_parameter,
                                       python_interpreter, path)
                Popen([terminal, start_parameter,
                                       python_interpreter, path])
                # If it works, remove all terminals in the to_try list
                terminals_to_try = []
            except:
                if DEBUG:
                    print 'Failed'
                if len(terminals_to_try) == 1:
                    # Impossible to find a terminal
                    raise NotImplementedError
                else:
                    terminals_to_try = terminals_to_try[1:]
    else:
        raise NotImplementedError
