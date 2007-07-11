"""
Rewrites links so that crunchy can access remote pages.
"""

import urllib
import re
from urlparse import urljoin
import os

import src.CrunchyPlugin as cp
def register():
    cp.register_tag_handler("a", None, None, link_handler)
    cp.register_tag_handler("img", None, None, src_handler)
    cp.register_tag_handler("link", None, None, href_handler)
    cp.register_tag_handler("style", None, None, style_handler)

def link_handler(page, elem):
    """convert remote links if necessary, need to deal with all links in remote pages"""
    if is_remote_url(page.url) and "href" in elem.attrib:
        if "://" not in elem.attrib["href"]:
            elem.attrib["href"] = urljoin(page.url, elem.attrib["href"])
    if "href" in elem.attrib:
        href = elem.attrib["href"]
        if "://" in href:
            elem.attrib["href"] = "/remote?url=%s" % urllib.quote_plus(href)
    if page.is_local and "href" in elem.attrib:
        if "#" in elem.attrib["href"]:
            return
        if "://" not in elem.attrib["href"]:
            href = urljoin(page.url, elem.attrib["href"])
            elem.attrib["href"] = "/local?url=%s" % urllib.quote_plus(href)

def src_handler(page, elem):
    """used in remote pages for elements that have an src attribute"""
    if is_remote_url(page.url) and "src" in elem.attrib:
        if "://" not in elem.attrib["src"]:
            elem.attrib["src"] = urljoin(page.url, elem.attrib["src"])
    elif page.is_local:
        local_dir = os.path.split(page.url)[0]
        elem.attrib["src"] = "/CrunchyLocalFile" + os.path.join(
                                            local_dir, elem.attrib["src"])
def href_handler(page, elem):
    """used in remote pages for elements that have an href attribute"""
    if is_remote_url(page.url) and "href" in elem.attrib:
        if "://" not in elem.attrib["href"]:
            elem.attrib["href"] = urljoin(page.url, elem.attrib["href"])
    if page.is_local and "href" in elem.attrib:
        local_dir = os.path.split(page.url)[0]
        elem.attrib["href"] = "/CrunchyLocalFile" + os.path.join(
                                            local_dir, elem.attrib["href"])
def is_remote_url(url):
    """test if a url is remote or not"""
    return not url.startswith("/")

css_import_re = re.compile('@import\s+"(.+?)"')

def style_handler(page, elem):
    """replace @import statements in style elements"""
    def css_import_replace(imp_match):
        path = imp_match.group(1)
        return '@import "%s"' % urljoin(page.url, path)
    elem.text = css_import_re.sub(css_import_replace, elem.text)
