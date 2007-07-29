'''
security.py

Javascript code is normally executed in a web-browser "sandbox", preventing
access to the user's computer.  Crunchy creates a link between the browser and
a Python backend, enabling the user to execute code on his computer (with full
access to the resources), thereby bypassing the security sandbox of the browser.

This creates a potential security hole.

The purpose of this module is to prevents the automatic execution of Python code
caused by insertion of malicious javascript code within a web page.
'''

# Note: a 2nd layer of security is implemented through a random session
# id generated in CrunchyPlugin.py
import imp
import os

import urllib
import urlparse
import sys

# Third party modules - included in crunchy distribution
from element_tree import ElementTree

import configuration

DEBUG = True

# Better safe than sorry: we do not allow the following html tags for the
# following reasons:
# script: because we want to prevent unauthorised code execution
# button, form, input, textarea: we only want Crunchy itself to create those
# *frame*: we don't want hidden frames that could be playing tricks with the
#          user (very remote possibility, but still.)
# embed: as the name indicates, can be used to embed some unwanted objects.
#
#
#  It may be worthwhile to check http://ha.ckers.org/xss.html from time to
# time to find out about possible other security issues.
#


# The following is not used currently
#attribute_black_list = ["text/javascript"]

# NOTE: 'style' below could be problematic due to the "url(" problem

# Almost all html tags can make use of these in a sensible way:
common_allowed = ['class', 'dir', 'id', 'lang', 'style', 'title']

# Rather than trying to find which attributes might be problematic (black list),
# we create a database of allowed (safe) attributes which we know will not cause
# any trouble.  This list can always be expanded if required.
# Note that a black list would have included onblur, onload, oninit, etc.,
# with possibly some new attributes introduced by a given browser which we
# would not have foreseen.

# {1} see also http://feedparser.org/docs/html-sanitization.html
specific_allowed = {
    'a': ['charset', 'type', 'name', 'href', 'hreflang', 'rel'],
    'abbr': [],
    'acronym': [],
    'address': [],
    # applet deprecated
    'area': ['name', 'shape', 'coords', 'href', 'alt', 'nohref'],
    'b': [],
    #'basefont': [], # not allowed in {1}
    #'base': [],  # not allowed in {1}
    'bdo': [],  # keep, even if not allowed in {1}
    'big': [],
    'blockquote': ['cite'],
    'body': ['bgcolor'],
    'br' : ['clear'],
    # button not allowed  - should be no reason
    'canvas': [],
    'caption': ['align'],
    'center': [],
    'cite': [],
    'code': [],
    'col': ['span', 'width'],
    'colgroup': ['span', 'width'],
    'dd': [],
    'del': ['cite', 'datetime'],
    'dfn': [],
    'dir': [],  #  deprecated but allowed
    'div': ['align'],
    'dl': [],
    'dt': [],
    'em': [],
    'fieldset': ['align'],
    'font': ['size', 'color', 'face'], # deprecated... but still often used!
    # form not allowed; if required, will be inserted by Crunchy itself
    # frame not allowed (don't want stuff possibly hidden)
    # frameset not allowed
    'h1': ['align'],
    'h2': ['align'],
    'h3': ['align'],
    'h4': ['align'],
    'h5': ['align'],
    'h6': ['align'],
    'head': [],
    'hr': ['align', 'noshade', 'size', 'width'], # these attributes are deprecated!
    'html': [],
    'i': [],
    # iframe not allowed
    'img': ['src', 'alt', 'longdesc', 'name', 'height', 'width', 'usemap', 'ismap'],
    # input not allowed
    'ins': ['cite', 'datetime'],
    # isindex deprecated
    'kbd': [],
    'label': ['for'],
    'legend': ['align'],
    'li': ['value'], # value is deprecated... but replaced by what?
    'link': ['charset', 'href', 'hreflang', 'type', 'rel', 'rev', 'media'],
    'map': ['shape', 'coords', 'href', 'nohref', 'alt'],
    'menu': [], # deprecated
    'meta': ['name', 'content'], #  'http-equiv' can be a potential problem
    'noframes': [],   # should not be needed
    'noscript' : [],   # should not be needed
    # object not allowed - preventing unwanted interactions
    'ol': ['start'],  # start is deprecated ... but replaced by ??
    #'optgroup': ['name', 'size', 'multiple'],  # Keep???
    #'option': ['name', 'size', 'multiple'],    # Keep???
    'p': [],
    # param not needed: only for object
    'pre': [],
    'q': ['cite'],
    's': [],  # deprecated but harmless
    'samp': [],
    # script not allowed!
    # 'select': ['name', 'size', 'multiple'], # Keep???
    'small': [],
    'span': ['align'],
    'strike': [], # deprecated
    'strong': [],
    'style': ['type', 'media'],
    'sub': [],
    'sup': [],
    'table': ['summary', 'align', 'width', 'bgcolor', 'frame', 'rules',
                'border', 'cellspacing', 'cellpadding'],
    'tbody': ['align', 'char', 'charoff', 'valign'],
    'td': ['abbr', 'axis', 'headers', 'scope', 'rowspan', 'colspan', 'bgcolor',
            'align', 'char', 'charoff', 'valign'],
    # textarea not needed; only included by Crunchy
    'tfoot': ['align', 'char', 'charoff', 'valign'],
    'th': ['abbr', 'axis', 'headers', 'scope', 'rowspan', 'colspan', 'bgcolor',
            'align', 'char', 'charoff', 'valign'],
    'thead': ['align', 'char', 'charoff', 'valign'],
    'title': ['abbr', 'axis', 'headers', 'scope', 'rowspan', 'colspan', 'bgcolor',
            'align', 'char', 'charoff', 'valign'],
    'tr': [],
    'tt': [],
    'u': [], # deprecated ... but still used
    'ul': [],
    'var': []
    }

# Just like XSS vulnerability are possible through <style> or 'style' attrib
# -moz-binding:url(" http://ha.ckers.org/xssmoz.xml#xss")
# [see: http://ha.ckers.org/xss.html for reference], the same holes
# could be used to inject javascript code into Crunchy processed pages.
#
# In addition, one common technique is to encode character into html
# entities to bypass normal filters.  In addition to ha.ckers.org,
# see also for example http://feedparser.org/docs/html-sanitization.html
#
# As a result, we will not allowed dangerous "substring" to appear
# in style attributes or in style sheets.

dangerous_strings = ['url(', '&#']

for key in specific_allowed:
    for item in common_allowed:
        specific_allowed[key].append(item)

def remove_unwanted(tree, page):
    '''Removes unwanted tags and or attributes from a "tree" created by
    ElementTree from an html page.'''

    unwanted = set()
    for element in tree.getiterator():
        if element.tag not in specific_allowed:
            unwanted.add(element.tag)
    for tag in unwanted:
        for element in tree.getiterator(tag):
            element.clear() # removes the text
            element.tag = None  # set up so that cleanup will remove it.

    for tag in specific_allowed:
        for element in tree.getiterator(tag):
# Filtering for possible dangerous content in "styles..."
            if tag == "link":
                if configuration.defaults.paranoid: # default is True
                    if not is_link_safe(element, page):
                        element.clear()
                        element.tag = None
                        continue
            for attr in element.attrib.items():
                if attr[0].lower() not in specific_allowed[tag]:
                    del element.attrib[attr[0]]
                elif attr[0].lower() == 'href':
                    testHREF = urllib.unquote_plus(attr[1]).replace("\r","").replace("\n","")
                    testHREF = testHREF.replace("\t","").lstrip().lower()
                    if testHREF.startswith("javascript:"):
                        del element.attrib[attr[0]]
# Filtering for possible dangerous content in "styles..."
                elif attr[0].lower() == 'style':
                    if configuration.defaults.paranoid: # default is True
                        value = attr[1].lower().replace(' ', '').replace('\t', '')
                        for x in dangerous_strings:
                            if x in value:
                                del element.attrib[attr[0]]
# Filtering for possible dangerous content in "styles..."
            if tag == 'style':
                if configuration.defaults.paranoid: # default is True
                    text = element.text.lower().replace(' ', '').replace('\t', '')
                    for x in dangerous_strings:
                        if x in text:
                            element.clear()
                            element.tag = None
    __cleanup(tree.getroot(), lambda e: e.tag)
    return tree

def __cleanup(elem, filter):
    ''' See http://effbot.org/zone/element-bits-and-pieces.htm'''
    out = []
    for e in elem:
        __cleanup(e, filter)
        if not filter(e):
            if e.text:
                if out:
                    out[-1].tail += e.text
                else:
                    elem.text += e.text
            out.extend(e)
            if e.tail:
                if out:
                    out[-1].tail += e.tail
                else:
                    elem.text += e.tail
        else:
            out.append(e)
    elem[:] = out
    return

def is_link_safe(elem, page):
    '''only keep <link> referring to style sheets that are deemed to
       be safe'''
    url = page.url
    if DEBUG:
        print "found link element; page url = ", url
    #--  Only allow style files
    if "type" in elem.attrib:
        type = elem.attrib["type"]
        if DEBUG:
            print "type = ", type
        if type.lower() != "text/css":  # not a style sheet - eliminate
            return False
    else:
        if DEBUG:
            print "type not found."
        return False
    #--
    if "rel" in elem.attrib:
        rel = elem.attrib["rel"]
        if DEBUG:
            print "rel = ", rel
        if rel.lower() != "stylesheet":  # not a style sheet - eliminate
            return False
    else:
        if DEBUG:
            print "rel not found."
        return False
    #--
    if "href" in elem.attrib:
        href = elem.attrib["href"]
        if DEBUG:
            print "href = ", href
    else:         # no link to a style sheet: not a style sheet!
        if DEBUG:
            print "href not found."
        return False
    #--If we reach this point we have in principle a valid style sheet.
    link_url = find_url(url, href)
    if DEBUG:
        print "link url = ", link_url
    #--Scan for suspicious content
    suspicious = False
    if page.is_local:
        css_file = open_local_file(link_url)
        if not css_file:  # could not open the file
            return False
        suspicious = scan_for_unwanted(css_file)
    elif page.is_remote:
        css_file = open_local_file(link_url)
        if not css_file:  # could not open the file
            return False
        suspicious = scan_for_unwanted(css_file)
    else:  # local page loaded via normal link.
        css_file = open_local_file(link_url)
        if not css_file:  # could not open the file
            return False
        suspicious = scan_for_unwanted(css_file)

    if not suspicious:
        if DEBUG:
            print "No suspicious content found in css file"
        return True
    elif DEBUG:
        print "suspicious content found in css file"
        return False

    if DEBUG:
        print "should not be reached"
    return False  # don't take any chances

# the root of the server is in a separate directory:
root_path = os.path.join(os.path.dirname(imp.find_module("crunchy")[1]), "server_root/")

def find_url(url, href):
    '''given the url of a "parent" html page and the href of a "child"
       (specified in a link element), returns
       the complete url of the child.'''
    if "://" in url:
        if DEBUG:
            print ":// found in url"
        return urlparse.urljoin(url, href)
    elif "://" in href:
        if DEBUG:
            print ":// found in href"
        return href
    elif href.startswith("/"):   # local css file from the root server
        return os.path.normpath(os.path.join(root_path, os.path.normpath(href[1:])))
    else:
        base, fname = os.path.split(url)
        if DEBUG:
            print "base path =", base
            print "root_path =", root_path
        href = os.path.normpath(os.path.join(base, os.path.normpath(href)))
        if href.startswith(root_path):
            if DEBUG:
                print "href starts with rootpath"
                print "href =", href
            return href
        if DEBUG:
            print "href does not start with rootpath"
            print "href =", href
        return os.path.normpath(os.path.join(root_path, href[1:]))

def open_local_file(url):
    if DEBUG:
        print "attempting to open file: ", url
    if url.startswith("http://"):
        try:
            return urllib.urlopen(url)
        except:
            if DEBUG:
                print "Cannot open remote file with url=", url
            return False
    try:
        return open(url, mode="r")
    except IOError:
        if DEBUG:
            print "opening the file without encoding did not work."
        try:
            return open(url.encode(sys.getfilesystemencoding()),
                        mode="r")
        except IOError:
            if DEBUG:
                print "Cannot open local file with url=", url
            return False

def scan_for_unwanted(css_file):
    '''Looks for any suspicious code in a css file

    For now, any file with "url(", "&#" and other "dangerous substrings
    in it is deemed suspicious  and will be rejected.

    returns True if suspicious code is found.'''
    for line in css_file.readlines():
        squished = line.replace(' ', '').replace('\t', '')
        for x in dangerous_strings:
            if x in squished:
                if DEBUG:
                    print "found suspicious content in the following line:"
                    print squished
                return True
    return False





