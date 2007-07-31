"""handle remote loading of tutorials.
Uses the /remote http request path.
"""

from src.CrunchyPlugin import *
from src.security import get_security_level
from urllib import urlopen, unquote_plus

provides = set(["/remote"])

def register():
    register_http_handler("/remote", remote_loader)
    CrunchyPlugin.register_service(display_security, "display_security")

def remote_loader(request):
    url = unquote_plus(request.args["url"])
    page = create_vlam_page(urlopen(url), url, remote=True)
    request.send_response(200)
    request.end_headers()
    request.wfile.write(page.read())

def display_security(page, elem, uid):
    if not page.includes("display_security") and page.body:
        page.add_include("display_security")
        test_security = Element("div")
        test_security.attrib["style"] = "position: absolute; left: 0px; top:0px; z-index:100"
        test_security.text = get_security_level("127.0.0.1") + " - "
        page.body.append(test_security)

        # TODO: reload page on return
        change_link = SubElement(test_security, "a")
        change_link.attrib["href"] = 'javascript:updateSecurity("trusted")'
        change_link.text = " change"