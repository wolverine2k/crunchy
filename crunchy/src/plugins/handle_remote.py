"""handle remote loading of tutorials.
Uses the /remote http request path.
"""

from urllib import FancyURLopener, unquote_plus

# All plugins should import the crunchy plugin API via interface.py
from src.interface import plugin, preprocessor, config

provides = set(["/remote"])

def register():  # tested
    '''registers http handler for dealing with remote files'''
    plugin['register_http_handler']("/remote", remote_loader)

def remote_loader(request):  # tested
    '''
    create a vlam page from a request to get a remote file
    '''
    url = unquote_plus(request.args["url"])
    extension = url.split('.')[-1]
    username = request.crunchy_username
    if extension in preprocessor:
        # TODO: preprocessor don't forward Accept-Language HTTP headers
        page = plugin['create_vlam_page'](
                    preprocessor[extension](url, local=False), url,
                                                username=username, remote=True)
    else:
        opener = FancyURLopener()
        if (config[username]["forward_accept_language"]
            and "Accept-Language" in request.headers):
            opener.addheader("Accept-Language", request.headers["Accept-Language"])
        page = plugin['create_vlam_page'](opener.open(url), url,
                                          username=username, remote=True)
    request.send_response(200)
    request.send_header('Cache-Control', 'no-cache, must-revalidate, no-store')
    request.end_headers()
    # write() in python 3.0 returns an int instead of None;
    # this interferes with unit tests
    dummy = request.wfile.write(page.read())
