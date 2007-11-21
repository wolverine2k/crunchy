"""handle local loading of tutorials (not from the server root).
Uses the /local http request path.
"""
import os
import sys

from src.CrunchyPlugin import *
from urllib import unquote_plus
from src.configuration import defaults

provides = set(["/local", "/generated_image"])

def register():
    register_http_handler("/local", local_loader)
    register_http_handler("/generated_image", image_loader)
    register_tag_handler("meta", "title", "python_import", add_to_path)

def local_loader(request):
    url = unquote_plus(request.args["url"])
    if ".htm" in url:
        page = create_vlam_page(open(url), url, local=True)
        # The following will make it possible to include python modules
        # with tutorials so that they can be imported.
        base_url, fname = os.path.split(url)
        if base_url not in sys.path:
            sys.path.insert(0, base_url)
    else:
        page = open(url, 'rb')
    request.send_response(200)
    request.end_headers()
    request.wfile.write(page.read())

def image_loader(request):
    url = unquote_plus(request.args["url"])
    fname = os.path.join(defaults.temp_dir, url)
    page = open(fname, 'rb')
    request.send_response(200)
    request.end_headers()
    request.wfile.write(page.read())

def add_to_path(page, elem, *dummy):
    '''adds a path, relative to the html tutorial, to the Python path'''
    base_url, fname = os.path.split(page.url)
    try:
        import_path = elem.attrib['name']
    except:
        return
    added_path = os.path.normpath(os.path.join(base_url, import_path))
    if added_path not in sys.path:
        sys.path.insert(0, added_path)




