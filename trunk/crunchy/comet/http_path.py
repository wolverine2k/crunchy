"""
helper functions to find files from a given root given an HTTP request
This has to be made platform independent - and tested properly
"""

from imp import find_module
import os.path as o
import urllib
from dircache import listdir, annotate

root_path = o.abspath(o.dirname(__file__))
print "Root path is %s" % root_path

default_pages = ["index.htm", "index.html"]

illegal_paths_page = """
<html>
<head>
<title>
Crunchy: Illegal path, page not found.
</title>
</head>
<body>
<h1>Illegal Path, Page not Found</h1>
<p>Crunchy could not open the page you requested. This could be for one of a
number of reasons, including:</p>
<ul>
<li>The page doesn't exist</li>
<li>The path you requested was illegal, examples of illegal paths include those containg the .. path modifier.
</ul>
<p>The path you requested was: <b>%s</b></p>
</body>
</html>
"""

dir_list_page = """
<html>
<head>
<title>
Crunchy: Directory Listing
</title>
</head>
<body>
<ul>
<li><a href="../">..</a></li>
%s
</ul>
</body>
</html>
"""

def path_to_filedata(path, root):
    """
    Given a path, finds the matching file and returns a read-only reference
    to it. If the path specifies a directory and does not have a trailing slash
    (ie. /example instead of /example/) this function will return none, the
    browser should then be redirected to the same path with a trailing /.
    Root is the fully qualified path to server root.
    Paths containing .. will return an error message.
    POSIX version, may work in Windows (untested).
    """
    if "/../" in path:
        return error_page(path)
    npath = o.normpath(o.join(root, o.normpath(path[1:])))
    npath = urllib.unquote(npath)
    if o.isdir(npath):
        if path[-1] != "/":
            return None
        else:
            return get_directory(npath)
    else:
        try:
            return open(npath).read()
        except IOError:
            return error_page(path)

def error_page(path):
    return illegal_paths_page % path

def get_directory(npath):
    childs = listdir(npath)
    childs = childs[:]
    annotate(npath, childs)
    for i in default_pages:
        if i in childs:
            return path_to_filedata("/"+i, npath)
    tstring = ""
    for child in childs:
        tstring += '<li><a href="%s">%s</a></li>' % (child, child)
    return dir_list_page % tstring

def handle_default(request):
    data = path_to_filedata(request.path, root_path)
    if data == None:
        request.send_response(301)
        request.send_header("Location", request.path + "/")
        request.end_headers()
    else:
        request.send_response(200)
        request.end_headers()
        request.wfile.write(data)
