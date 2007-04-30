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
provides = set(["/save_file", "/load_file", "/save_and_run"])

def exec_handler(request):
    """handle an execution request"""
    CrunchyPlugin.exec_code(request.data, request.args["uid"])
    request.send_response(200)
    request.end_headers()


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
    CrunchyPlugin.register_http_handler("/save_and_run", save_and_run_request_handler)
    #CrunchyPlugin.register_service(save_file, "save_file")
    #CrunchyPlugin.register_service(read_file, "read_file")


def save_file_request_handler(request):
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
    path = save_file_request_handler(request)
    exec_external(path=path)

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
        * GNOME (originally tested - but not since change)
        * OS X
    This also needs to be implemented/texted for KDE
    and some form of linux fallback (xterm?)
    """
    if path is None:
        path = os.path.join(os.path.expanduser("~"), ".crunchy", "temp.py")
    if os.name == 'nt':
        current_dir = os.getcwd()
        target_dir, fname = os.path.split(path)

    if code is not None:  # used in old Crunchy
        filename = open(path, 'w')
        filename.write(code)
        filename.close()

    if os.name == 'nt':
        os.chdir(target_dir) # change dir so as to deal with paths that
                             # include spaces
        if console:
            Popen(["cmd.exe", ('/c start python %s'%fname)])
        else:
            Popen(["cmd.exe", ('/c python %s'%fname)])
        os.chdir(current_dir)
    if sys.platform == 'darwin':  # adapted from spe
        pth, fn = os.path.split(path)
        commandList = [ ['cd', pth], ['python', fn], ['exit'] ]
        startAppleScript(commandList, activateFlag=True)
    elif os.name == 'posix':
        try:
            os.spawnlp(os.P_NOWAIT, 'gnome-terminal', 'gnome-terminal',
                                '-x', 'python', '%s'%path)
        except:
            try: # untested
                os.spawnlp(os.P_NOWAIT, 'Konsole', 'Konsole',
                                '-x', 'python', '%s'%path)
            except:
                raise NotImplementedError
    else:
        raise NotImplementedError

# the following is taken from SPE
def startAppleScript(commandList, activateFlag = True):
	"""Start a list of commands in the terminal window.
	Each command is a list of program name, parameters.
	Handles the quoting properly through shell, applescript and shell again.
	"""
	def adjustParameter(parameter):
		"""Adjust a parameter for the shell.
		Adds single quotes,
		unless the parameter consists of letters only
		(to make shell builtins work)
		or if the parameter is a list
		(to flag that it already is list a parameters).
		"""
		if isinstance(parameter, list): return parameter[0]
		if parameter.isalpha(): return parameter
		#the single quote proper is replaced by '\'' since
		#backslashing a single quote doesn't work inside a string
		return "'%s'"%parameter.replace("'",r"'\''")
	command = ';'.join([
		' '.join([
			adjustParameter(parameter)
			for parameter in command
			])
		for command in commandList
	])
	#make Applescript string from this command line:
	#put backslashes before double quotes and backslashes
	command = command.replace('\\','\\\\').replace('"','\\"')
	#make complete Applescript command containing this string
	command = 'tell application "Terminal" to do script "%s"'%command
	#make a shell parameter (single quote handling as above)
	command = command.replace("'","'\\''")
	#make complete shell command
	command = "osascript -e '%s'"%command
	#prepend activate command if needed
	if activateFlag:
		command = "osascript -e 'tell application \"Terminal\" to activate';"+command
	#go!
	os.popen(command)
