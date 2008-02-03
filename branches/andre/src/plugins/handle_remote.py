"""handle remote loading of tutorials.
Uses the /remote http request path.
"""

from urllib import urlopen, unquote_plus

# All plugins should import the crunchy plugin API via interface.py
from src.interface import plugin, preprocessor

provides = set(["/remote"])

def register():
    plugin['register_http_handler']("/remote", remote_loader)

def remote_loader(request):
    url = unquote_plus(request.args["url"])
    extension = url.split('.')[-1]
    if extension in ['htm', 'html']:
        page = plugin['create_vlam_page'](urlopen(url), url, remote=True)
    elif extension in preprocessor:
        page = plugin['create_vlam_page'](
                         preprocessor[extension](url, local=False), url)
    request.send_response(200)
    request.end_headers()
    # write() in python 3.0 returns an int instead of None;
    # this interferes with unit tests
    dummy = request.wfile.write(page.read())