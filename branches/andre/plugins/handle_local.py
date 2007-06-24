"""handle local loading of tutorials (not from the server root).
Uses the /local http request path.
"""

from CrunchyPlugin import *
from urllib import unquote_plus

provides = set(["/local"])

def register():
    register_http_handler("/local", local_loader)

def local_loader(request):
    url = unquote_plus(request.args["url"])
    page = create_vlam_page(open(url), url, local=True)
    request.send_response(200)
    request.end_headers()
    request.wfile.write(page.read())