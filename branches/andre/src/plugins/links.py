"""
Rewrites links so that crunchy can access remote pages.
"""

import urllib
import re
from urlparse import urljoin, urlsplit, urlunsplit
import os

# All plugins should import the crunchy plugin API via interface.py
from src.interface import plugin, SubElement

def register():
    plugin['register_tag_handler']("a", None, None, link_handler)
    plugin['register_tag_handler']("img", None, None, src_handler)
    plugin['register_tag_handler']("link", None, None, href_handler)
    plugin['register_tag_handler']("style", None, None, style_handler)
    plugin['register_tag_handler']("a","title", "external_link", external_link)

def external_link(dummy_page, elem, *dummies):
    '''handler which totally ignores the link being passed to it, other than
    inserting an image to indicate it leads outside of Crunchy'''
    if elem.tail:
        elem.tail += " "
    else:
        elem.text += " "
    img = SubElement(elem, "img")
    img.attrib['src'] = "/external_link.png"
    img.attrib['style'] = "border:0;"
    img.attrib['alt'] = "external_link.png"
    return

def link_handler(page, elem):
    """convert remote links if necessary, need to deal with all links in
       remote pages"""
    if "href" not in elem.attrib:
        return
    ### To do: deal better with .rst, .txt and .py files
    if elem.attrib["href"].startswith("/"):
        return
    elem.attrib["href"] = secure_url(elem.attrib["href"])
    if is_remote_url(page.url):
        if "#" in elem.attrib["href"]:
            if elem.attrib["href"].startswith("#"):
                return
            else:
                # Python.org tutorial has internal links of the form
                #   node#some_reference i.e. there is an extra prefix
                splitted = elem.attrib["href"].split("#")
                if page.url.endswith(splitted[0]): # remove extra prefix
                    elem.attrib["href"] = "#" + splitted[1]
                    return
                else:  # remove trailing #... which Crunchy can't handle
                    elem.attrib["href"] = splitted[0]

        if "://" not in elem.attrib["href"]:
            elem.attrib["href"] = urljoin(page.url, elem.attrib["href"])
        return

    href = elem.attrib["href"]
    if "://" in href:
        elem.attrib["href"] = "/remote?url=%s" % urllib.quote_plus(href)
        return

    if page.is_local: # loaded via local browser
        if "#" in elem.attrib["href"]:
            if elem.attrib["href"].startswith("#"):
                return
            else:
                # Python.org tutorial has internal links of the form
                #   node#some_reference i.e. there is an extra prefix
                splitted = elem.attrib["href"].split("#")
                if page.url.endswith(splitted[0]): # remove extra prefix
                    elem.attrib["href"] = "#" + splitted[1]
                    return
                else:  # remove trailing #... which Crunchy can't handle
                    elem.attrib["href"] = splitted[0]
        extension = elem.attrib["href"].split(".")[-1]
        if extension in ["rst", "txt"]:
            elem.attrib["href"] = "/rst?url=%s" % \
                os.path.dirname(page.url) + "/" + \
                urllib.quote_plus(elem.attrib["href"])
            return
        if "://" not in elem.attrib["href"]:
            href = urljoin(page.url, elem.attrib["href"])
            elem.attrib["href"] = "/local?url=%s" % urllib.quote_plus(href)
            return
    #extension = elem.attrib["href"].split('.')[-1]


def src_handler(page, elem):
    """used for elements that have an src attribute not loaded from the
       server root"""
    if "src" not in elem.attrib:
        return
    # not needed as we validate images in security.py
    ##elem.attrib["src"] = secure_url(elem.attrib["src"])
    if is_remote_url(page.url):
        if "://" not in elem.attrib["src"]:
            elem.attrib["src"] = urljoin(page.url, elem.attrib["src"])
    elif page.is_local:
        local_dir = os.path.split(page.url)[0]
        elem.attrib["src"] = "/local?url=%s"%urllib.quote_plus(
                                os.path.join(local_dir, elem.attrib["src"]))

def href_handler(page, elem):
    """used for elements that have an href attribute not loaded from the
       server root"""
    if "href" not in elem.attrib:
        return
    elem.attrib["href"] = secure_url(elem.attrib["href"])
    if is_remote_url(page.url):
        if "://" not in elem.attrib["href"]:
            elem.attrib["href"] = urljoin(page.url, elem.attrib["href"])
    if page.is_local:
        local_dir = os.path.split(page.url)[0]
        elem.attrib["href"] = "/local?url=%s"%urllib.quote_plus(
                                os.path.join(local_dir, elem.attrib["href"]))

def secure_url(url):
    '''For security reasons, restricts a link to its simplest form if it
    contains a query ("?") so that it can't be used to pass arguments
    to the Python server'''
    if "?" not in url:
        return url
    info = urlsplit(url)
    return urlunsplit((info[0], info[1], info[2], '', ''))

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
