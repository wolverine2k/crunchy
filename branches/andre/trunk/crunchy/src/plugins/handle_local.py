"""handle local loading of tutorials (not from the server root).
Uses the /local http request path.
"""
import os
import sys
from urllib import unquote_plus

# All plugins should import the crunchy plugin API via interface.py
from src.interface import config, plugin

provides = set(["/local", "/generated_image"])

def register():  # tested
    plugin['register_http_handler']("/local", local_loader)
    plugin['register_tag_handler']("meta", "title", "python_import", add_to_path)

def local_loader(request):  # tested
    '''loads a local file;
    if it determines that it is an html file (based on the extension), it
    creates a new vlam page from it and, if not already present, adds the
    base path to sys.path - so that any python file located in the same
    directory could be imported.

    If it is not an html file, it simply reads the file.'''
    url = unquote_plus(request.args["url"])
    extension = url.split('.')[-1]
    if "htm" in extension:
        page = plugin['create_vlam_page'](open(url), url, local=True)
        # The following will make it possible to include python modules
        # with tutorials so that they can be imported.
        base_url, fname = os.path.split(url)
        if base_url not in sys.path:
            sys.path.insert(0, base_url)
    else:
        page = open(url, 'rb')
    request.send_response(200)
    request.end_headers()
    # write() in python 3.0 returns an int instead of None;
    # this interferes with unit tests
    __irrelevant = request.wfile.write(page.read())

def add_to_path(page, elem, *dummy):  # tested
    '''adds a path, relative to the html tutorial, to the Python path'''
    base_url, fname = os.path.split(page.url)
    try:
        import_path = elem.attrib['name']
    except:
        return
    added_path = os.path.normpath(os.path.join(base_url, import_path))
    if added_path not in sys.path:
        sys.path.insert(0, added_path)
