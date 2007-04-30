"""  file_service.py

Provides the means to save and load a file.
"""

from urllib import pathname2url

# All plugins should import the crunchy plugin API
import CrunchyPlugin

# The set of other "widgets/services" provided by this plugin
provides = set(["/save_file", "/load_file"])


def exec_handler(request):
    """handle an execution request"""
    CrunchyPlugin.exec_code(request.data, request.args["uid"])
    request.send_response(200)
    request.end_headers()


def register():
    """The register() function is required for all plugins.
       In this case, we need to register two types of 'actions':
         1. an 'http handler' that deals with requests to save files
         2. an 'http handler' that deals with requuests to load files.
       If needed, we could register two services using internal functions
         1. a custom service to save a file.
         2. a custom service to read content from a file.
       """
    CrunchyPlugin.register_http_handler("/save_file", save_file_request_handler)
    CrunchyPlugin.register_http_handler("/load_file", load_file_request_handler)

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
    print "calling save_file"
    save_file(path, content)

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
