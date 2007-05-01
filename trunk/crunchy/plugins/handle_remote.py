"""handle remote loading of tutorials.
Uses the /remote http request path.
"""

from CrunchyPlugin import *
from urllib import urlopen
def register():
    register_http_handler("/remote", remote_loader)
    
def remote_loader(request):
    url = request.args["url"]
    print "loading remote URL: %s" % url
    page = create_vlam_page(urlopen(url))
    request.send_response(200)
    request.end_headers()
    request.wfile.write(page.read())