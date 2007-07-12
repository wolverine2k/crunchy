"""handle local loading of tutorials (not from the server root).
Uses the /local http request path.
"""
import os

from src.CrunchyPlugin import *
from urllib import unquote_plus
from src.configuration import defaults

provides = set(["/local", "/generated_image"])

def register():
    register_http_handler("/local", local_loader)
    register_http_handler("/generated_image", image_loader)

def local_loader(request):
    url = unquote_plus(request.args["url"])
    if ".htm" in url:
        page = create_vlam_page(open(url), url, local=True)
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
