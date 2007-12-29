"""handle remote loading of tutorials.
Uses the /remote http request path.
"""

from urllib import urlopen, unquote_plus

# All plugins should import the crunchy plugin API via interface.py
from src.interface import plugin

provides = set(["/remote"])

def register():
    plugin['register_http_handler']("/remote", remote_loader)

def remote_loader(request):
    url = unquote_plus(request.args["url"])
    page = plugin['create_vlam_page'](urlopen(url), url, remote=True)
    request.send_response(200)
    request.end_headers()
    request.wfile.write(page.read())