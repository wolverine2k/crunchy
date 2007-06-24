"""
Rewrites links so that crunchy can access remote pages.
"""

import urllib

import CrunchyPlugin as cp
from urlparse import urljoin
import os

def register():
    cp.register_vlam_handler("a", None, link_handler)
    cp.register_vlam_handler("img", None, src_handler)
    cp.register_vlam_handler("link", None, href_handler)

def link_handler(page, elem, uid, vlam):
    """convert remote links if necessary, need to deal with all links in remote pages"""
    if is_remote_url(page.url) and "href" in elem.attrib:
        if "://" not in elem.attrib["href"]:
            elem.attrib["href"] = urljoin(page.url, elem.attrib["href"])
    if "href" in elem.attrib:
        href = elem.attrib["href"]
        if "://" in href:
            elem.attrib["href"] = "/remote?url=%s" % urllib.quote_plus(href)

def src_handler(page, elem, uid, vlam):
    """used in remote pages for elements that have an src attribute"""
    if is_remote_url(page.url) and "src" in elem.attrib:
        if "://" not in elem.attrib["src"]:
            elem.attrib["src"] = urljoin(page.url, elem.attrib["src"])
    elif page.is_remote: # this is how locally loaded tutorials are identified at the moment
        local_dir = os.path.split(page.url)[0]
        elem.attrib["src"] = "/CrunchyLocalFile" + os.path.join(
                                            local_dir, elem.attrib["src"])
def href_handler(page, elem, uid, vlam):
    """used in remote pages for elements that have an href attribute"""
    if is_remote_url(page.url) and "href" in elem.attrib:
        if "://" not in elem.attrib["href"]:
            elem.attrib["href"] = urljoin(page.url, elem.attrib["href"])

def is_remote_url(url):
    """test if a url is remote or not"""
    return not url.startswith("/")

