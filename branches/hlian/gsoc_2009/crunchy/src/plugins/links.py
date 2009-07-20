"""
Rewrites links so that crunchy can access remote pages.

unit tests in in test_links.rst
"""

import urllib
import re
from urlparse import urljoin, urlsplit, urlunsplit
import os

# All plugins should import the crunchy plugin API via interface.py
from src.interface import plugin, SubElement

def register():  # tested
    '''registers a series of tag handlers, all related to html links '''
    plugin['register_tag_handler']("a", None, None, a_tag_handler)
    plugin['register_tag_handler']("img", None, None, src_handler)
    plugin['register_tag_handler']("link", None, None, link_tag_handler)
    plugin['register_tag_handler']("style", None, None, style_handler)
    plugin['register_tag_handler']("a", "title", "external_link", external_link)
    plugin['register_tag_handler']("a", "title", "security_link", fixed_link)

def external_link(page, elem, *dummy):  # tested
    '''handler which totally ignores the link being passed to it, other than
    inserting an image to indicate it leads outside of Crunchy'''
    if elem.tail:
        elem.tail += " "
    else:
        elem.text += " "
    dummy = SubElement(elem, "img",
                       src=u"/images/external_link.png",
                       style=u"border:0;",
                       alt=u"external_link.png")
    elem.attrib['target'] = u"_blank" # opens in separate window/tab.
    # If the links is a relative link, make it absolute
    if u"://" not in elem.attrib["href"]:
        elem.attrib["href"] = urljoin(page.url, elem.attrib["href"])
    return

def fixed_link(*dummy):  # tested
    '''handler which totally ignores the link being passed to it.'''
    # This is useful if one Crunchy widget needs to insert a link, usually
    # with respect to the server root, that is not meant to be altered - which
    # otherwise might have occurred because of the other link handlers.
    return

def a_tag_handler(page, elem, *dummy):  # tested
    """convert remote links if necessary, need to deal with all links in
       remote pages"""
    if "href" not in elem.attrib:
        return
    elem.attrib["href"] = secure_url(elem.attrib["href"])
    if page.is_remote: #is_remote_url(page.url):
        if 'title' in elem.attrib:
            if elem.attrib['title'] == u'security_link':
                return
        if "#" in elem.attrib["href"]:
            if elem.attrib["href"].startswith("#"):
                return
            else:
                # Python.org tutorial has internal links of the form
                #   node#some_reference i.e. there is an extra prefix
                splitted = elem.attrib["href"].split("#")
                if page.url.endswith(splitted[0]): # remove extra prefix
                    elem.attrib["href"] = u"#" + splitted[1]
                    return
                else:  # remove trailing #... which Crunchy can't handle
                    elem.attrib["href"] = splitted[0]

        if "://" not in elem.attrib["href"]:
            elem.attrib["href"] = urljoin(page.url, elem.attrib["href"])
            elem.attrib["href"] = u"/remote?url=%s" % urllib.quote_plus(elem.attrib["href"])
        return

    href = elem.attrib["href"]
    if "://" in href:
        elem.attrib["href"] = u"/remote?url=%s" % urllib.quote_plus(href)
        return

    ### To do: deal better with .rst, .txt and .py files
    if elem.attrib["href"].startswith("/"):
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
                    elem.attrib["href"] = u"#" + splitted[1]
                    return
                else:  # remove trailing #... which Crunchy can't handle
                    elem.attrib["href"] = splitted[0]
        extension = elem.attrib["href"].split(".")[-1]
        if extension in ["rst", "txt"]:
            elem.attrib["href"] = u"/rst?url=%s" % \
                os.path.dirname(page.url) + "/" + \
                urllib.quote_plus(elem.attrib["href"])
            return
        if "://" not in elem.attrib["href"]:
            href = urljoin(page.url, elem.attrib["href"])
            elem.attrib["href"] = u"/local?url=%s" % urllib.quote_plus(href)
            return
    #extension = elem.attrib["href"].split('.')[-1]


def src_handler(page, elem, *dummy):  # partially tested
    """used for elements that have an src attribute not loaded from the
       server root"""
    if "src" not in elem.attrib:
        return
    if 'title' in elem.attrib:
        if elem.attrib['title'] == 'security_link':
            return
    # not needed as we validate images in security.py
    ##elem.attrib["src"] = secure_url(elem.attrib["src"])
    if page.is_remote: #is_remote_url(page.url):
        if "://" not in elem.attrib["src"]:
            elem.attrib["src"] = urljoin(page.url, elem.attrib["src"])
    elif page.is_local:
        if elem.attrib["src"].startswith("/"):
            return
        local_dir = os.path.split(page.url)[0]
        elem.attrib["src"] = u"/local?url=%s" % urllib.quote_plus(
                                os.path.join(local_dir, elem.attrib["src"]))

def link_tag_handler(page, elem, *dummy):  # partially tested
    """resolves html <link> URLs"""
    if "href" not in elem.attrib:
        return
    elem.attrib["href"] = secure_url(elem.attrib["href"])
    if page.is_remote: #is_remote_url(page.url):
        if "://" not in elem.attrib["href"]:
            elem.attrib["href"] = urljoin(page.url, elem.attrib["href"])
    if page.is_local:
        if elem.attrib["href"].startswith("/"):
            return
        local_dir = os.path.split(page.url)[0]
        elem.attrib["href"] = u"/local?url=%s" % urllib.quote_plus(
                                os.path.join(local_dir, elem.attrib["href"]))

def secure_url(url):  # tested
    '''For security reasons, restricts a link to its simplest form if it
    contains a query ("?") so that it can't be used to pass arguments
    to the Python server'''
    if "?" not in url:
        return url
    info = urlsplit(url)
    return urlunsplit((info[0], info[1], info[2], '', ''))
#
#def is_remote_url(url):
#    """test if a url is remote or not"""
#    return not url.startswith("/")

css_import_re = re.compile('@import\s+"(.+?)"')

def style_handler(page, elem, *dummy):  # tested
    """replace @import statements in style elements"""
    def css_import_replace(imp_match): # indirectly tested
        '''replaces the relative path found by its absolute value'''
        path = imp_match.group(1)
        return '@import "%s"' % urljoin(page.url, path)
    elem.text = css_import_re.sub(css_import_replace, elem.text)
