# -*- coding: utf-8 -*-
"""handle local loading of tutorials (not from the server root).
Uses the /local http request path.

Also creates a form allowing to browse for a local tutorial to be loaded
by Crunchy.
"""
import os
import re
import sys
import traceback

# All plugins should import the crunchy plugin API via interface.py
from src.interface import config, plugin, python_version, translate
_ = translate['_']
import src.interface

if python_version < 3:
    from urllib import quote_plus, unquote_plus
    from urlparse import urljoin
else:
    from urllib.parse import quote_plus, unquote_plus, urljoin

provides = set(["/local"])
requires = set(["filtered_dir", "insert_file_tree"])

LOCAL_HTML = "local_html"

def register():  # tested
    '''registers the plugins so that Crunchy can use them'''
    plugin['register_http_handler']("/local", local_loader)
    plugin['register_tag_handler']("meta", "title", "python_import", add_to_path)
    plugin['register_tag_handler']("div", "title", "local_html_file",
                                                 insert_load_local)
    plugin['add_vlam_option']('power_browser', LOCAL_HTML)
    plugin['register_http_handler']("/jquery_file_tree_html", jquery_file_tree_html)
    plugin['register_service'](LOCAL_HTML, insert_load_local)

def local_loader(request):  # tested
    '''loads a local file;
    if it determines that it is an html file (based on the extension), it
    creates a new vlam page from it and, if not already present, adds the
    base path to sys.path - so that any python file located in the same
    directory could be imported.

    If it is not an html file, it simply reads the file.'''
    url = unquote_plus(request.args["url"])
    extension = url.split('.')[-1]
    base_url, dummy = os.path.split(url)
    username = request.crunchy_username
    if "htm" in extension:
        page = plugin['create_vlam_page'](open(url, 'rb'), url, username=username,
                                          local=True)
        # The following will make it possible to include python modules
        # with tutorials so that they can be imported.
        if base_url not in sys.path:
            sys.path.insert(0, base_url)
        content = page.read()
    elif extension == 'css':
        # record this value in case a css file imports another relative
        # one via something like @import "s5-core.css";
        # which slides by docutils do.
        #src.interface.last_local_base_url, dummy =  os.path.split(url)
        base_url, dummy =  os.path.split(url)
        page = open(url, 'rb')
    else:
        print "non css extension: ", extension
        page = open(url, 'rb')
    content = page.read()
    if extension == 'css':
        content = replace_css_import(base_url, content)
    request.send_response(200)
    request.send_header('Cache-Control', 'no-cache, must-revalidate, no-store')
    request.end_headers()
    # write() in python 3.0 returns an int instead of None;
    # this interferes with unit tests
    # also, in Python 3, need to convert between bytes and strings for text...
    try:
        __irrelevant = request.wfile.write(content.encode('utf-8'))
    except:
        __irrelevant = request.wfile.write(content)

css_import_re = re.compile('@import\s+url\((.+?)\);')
def replace_css_import(base_url, text):
    """replace @import statements in style elements"""
    def css_import_replace(imp_match):
        '''replaces the relative path found by its absolute value'''
        path = imp_match.group(1)
        return '@import url(%s/%s);' % (base_url, path)
    return css_import_re.sub(css_import_replace, text)

def add_to_path(page, elem, *dummy):  # tested
    '''adds a path, relative to the html tutorial, to the Python path'''
    base_url, dummy = os.path.split(page.url)
    try:
        import_path = elem.attrib['name']
    except:
        return
    if page.is_from_root:
        added_path = os.path.normpath(os.path.join(
                                        config['crunchy_base_dir'],
                                    "server_root", base_url[1:], import_path))
    else:
        added_path = os.path.normpath(os.path.join(base_url, import_path))
    if added_path not in sys.path:
        sys.path.insert(0, added_path)

def insert_load_local(page, elem, uid):
    "Inserts a javascript browser object to load a local (html) file."
    plugin['services'].insert_file_tree(page, elem, uid, '/jquery_file_tree_html',
                                '/local', _('Load local html tutorial'),
                                _('Load tutorial'))
    return
plugin[LOCAL_HTML] = insert_load_local

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

def jquery_file_tree_html(request):
    '''extract the file information and formats it in the form expected
       by the jquery FileTree plugin, but excludes some normally hidden
       files or directories, to include only html files.'''
    plugin['services'].filtered_dir(request, filter_html)
    return
