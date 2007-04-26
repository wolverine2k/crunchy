"""links.py
Fancy handling of links in HTML: essentially a request is sent to the server to
load a particular page, only once that page has been loaded will the link be
followed.

This allows us to report errors in processing very easily and to handle remote
links much better.
"""

from CrunchyPlugin import *

def register():
    register_vlam_handler("a", None, html_link_handler)
    register_http_handler("/link", http_link_handler)

def html_link_handler(page, elem, uid, vlam):
    """replace links with a request to consider the link"""
    if not page.includes("handle_link_included"):
        page.add_js_code(handle_link_jscode)
        page.add_include("handle_link_included")
    # temporary "fix"...  without this, we sometimes get KeyErrors; needs further investigation
    if "href" in elem.attrib: # "fix"
        href = elem.attrib["href"]
        elem.attrib["href"] = "#"
        elem.attrib["onclick"] = "handle_link('%s', '%s');return false;" % (href, uid.split(":")[0])


def http_link_handler(request):
    """handle an http request"""
    pageid = request.args["pageid"]
    print "redirecting to: " + request.data
    request.send_response(200)
    request.end_headers()
    exec_js(pageid, """setTimeout('window.location="%s";', 100)""" % request.data)



handle_link_jscode = r"""
function handle_link(url, pageid){
    var rq = new XMLHttpRequest();
    rq.open("POST", "/link?pageid="+pageid, false);
    rq.send(url);
};
"""
