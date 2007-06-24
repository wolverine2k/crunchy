"""handle remote loading of tutorials.
Uses the /remote http request path.
"""

from CrunchyPlugin import *
from urllib import urlopen, unquote_plus

provides = set(["/remote"])

def register():
    register_http_handler("/remote", remote_loader)

def remote_loader(request):
    url = unquote_plus(request.args["url"])
    page = create_vlam_page(urlopen(url), url, remote=True)
    request.send_response(200)
    request.end_headers()
    request.wfile.write(page.read())