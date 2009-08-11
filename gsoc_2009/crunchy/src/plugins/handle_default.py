"""This plugin handles loading all pages not loaded by other plugins.
It's important to close file handles in this module as it seems to
solve the too-many-files-open error that intermittently pops up."""

import codecs
import os
import re
import sys
import traceback
from os.path import normpath, isdir, join, exists

# All plugins should import the crunchy plugin API via interface.py
from src.interface import (
    translate, plugin, server, debug,
    debug_msg, preprocessor)
from src.utilities import meta_content_open

_ = translate['_']

def register():
    '''registers a default http handler'''
    plugin['register_http_handler'](None, handler)

# the root of the server is in a separate directory:
root_path = join(plugin['crunchy_base_dir'](), "server_root/")

def index(npath):
    """ Normalizes npath to an index.htm or index.html file if
    possible. Returns normalized path. """

    if not isdir(npath):
        return npath

    childs = os.listdir(npath)
    for i in ("index.htm", "index.html"):
        if i in childs:
            return join(npath, i)

    return npath

def path_to_filedata(path, root, username=None):
    """ Given a path, finds the matching file and returns a read-only
    reference to it. If the path specifies a directory and does not
    have a trailing slash (ie. /example instead of /example/) this
    function will return none, the browser should then be redirected
    to the same path with a trailing /. Root is the fully qualified
    path to server root. Paths starting with / and containing .. will
    return an error message. POSIX version, should work in Windows.
    Data will be returned in encoded, non-Unicode form because the
    path could point to a binary file and is tailored for the
    request.wfile.write method.
    """
    # Path is guaranteed to be Unicode. See parse_headers in
    # http_serve.py for details.
    assert isinstance(path, unicode)

    if path == server['exit']:
        server['server'].still_serving = False
        exit_file = join(root_path, "exit_en.html")

        f = open(exit_file, mode="rb")
        x = f.read()
        f.close()
        return x
    if path.startswith("/") and (path.find("/../") != -1):
        return error_page(path).encode('utf8')

    if exists(path) and path != "/":
        npath = path
    else:
        npath = normpath(join(root, normpath(path[1:])))

    npath = index(npath)

    if isdir(npath):
        if path[-1] != "/":
            return None
        return get_directory(npath, username).encode('utf8')

    try:
        extension = npath.split('.')[-1]
        creator = plugin['create_vlam_page']
        if extension in ["htm", "html"]:
            f = meta_content_open(npath)
            text = creator(f, path, username)
            f.close()
            text = text.read().encode('utf8')
            return text
        elif extension in preprocessor:
            f = preprocessor[extension](npath)
            text = creator(f, path, username)
            f.close()
            text = text.read().encode('utf8')
            return text
        # we need binary mode because otherwise the file may not get
        # read properly on windows (e.g. for image files)
        f = open(npath, mode="rb")
        x = f.read()
        f.close()
        return x
    except IOError:
        print("In path_to_filedata, can not open path: " + npath)
        traceback.print_exc()
        return error_page(path).encode('utf8')

def handler(request):
    """the actual handler"""
    if debug['handle_default'] or debug['handle_default.handler']:
        debug_msg("--> entering handler() in handle_default.py")
    try:
        username = request.crunchy_username
    except:
        msg = _("You need to create an account before you can use Crunchy. ")
        request.wfile.write(msg.encode('utf8'))
        msg = _("Please use account_manager.py to create an account.")
        request.wfile.write(msg.encode('utf8'))
        exit_file = join(root_path, "exit_en.html")

        f = open(exit_file, 'rb')
        request.wfile.write(f.read())
        f.close()

        request.end_headers()
        server['server'].still_serving = False
        return

    data = path_to_filedata(request.path, root_path, request.crunchy_username)
    assert not isinstance(data, unicode)

    if debug['handle_default'] or debug['handle_default.handler']:
        debug_msg("in handle_default.handler(), beginning of data =")
        try:
            d = data[0:80]
            if "\n" in d:
                d = d.split("\n")[0]
            debug_msg(d)
        except:
            debug_msg(data)
    if data == None:
        request.send_response(301)
        request.send_header("Location", request.path + "/")
        request.end_headers()
    else:
        request.send_response(200)
        # Tell Firefox not to cache; otherwise back button can bring back to
        # a page with a broken interpreter
        request.send_header('Cache-Control', 'no-cache, must-revalidate, no-store')
        # Todo: Send out a proper Content-type here.
        request.end_headers()
        try:
            request.wfile.write(data)
        except:  # was introduced to deal with Python 3.x problems
            print("Error in handle_default; should not have happened!")
            raise

def list_directory(path):
    '''Returns a list of files and annotated directories in a path.'''
    childs = os.listdir(path)
    def annotate(child):
        if isdir(os.path.join(path, child)):
            return child + '/'
        else:
            return child
    return map(annotate, childs)

def get_directory(npath, crunchy_username):
    '''Returns a directory listing from a path. Always returns
    Unicode.'''

    assert isdir(npath)
    childs = list_directory(npath)

    def to_bullet(x):
        return '<li><a href="%s">%s</a></li>' % (x, x)

    tstring = u''.join(to_bullet(child) for child in childs)
    return dir_list_page % (_("Directory Listing"), tstring)

not_found = codecs.open(join(root_path, "404.html"),
                        encoding='utf8').read()

dir_list_page = u"""
<html>
<head>
<title>
%s
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

def error_page(path):
    '''returns a page with an error message; used when a path is not found'''
    return not_found % (path, path)
