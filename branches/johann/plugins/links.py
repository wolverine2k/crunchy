"""
Rewrites links so that crunchy can access remote pages.
"""

import urllib

import CrunchyPlugin as cp

def register():
    cp.register_vlam_handler("a", None, LinkHandler)
    
def LinkHandler(page, elem, uid, vlam):
    """convert remote links if necessary"""
    if "href" in elem.attrib:
        href = elem.attrib["href"]
        if href.startswith("http://"):
            elem.attrib["href"] = "/remote?url=%s" % urllib.unquote_plus(href)
        