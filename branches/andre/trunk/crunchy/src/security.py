'''
security.py: unit tests in test_security.rst

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
import os
import imghdr
import urllib
import urlparse
import sys

from src.interface import config, ElementTree

DEBUG = False
DEBUG2 = False
# the root of the server is in a separate directory:

root_path = os.path.join(config['crunchy_base_dir'], "server_root")

# Better safe than sorry: we do not allow the following html tags for the
# following reasons:
# script: because we want to prevent unauthorised code execution
# button, form, input, textarea: we only want Crunchy itself to create those
# *frame*: we don't want hidden frames that could be playing tricks with the
#          user (very remote possibility, but still.)
# embed: as the name indicates, can be used to embed some unwanted objects.
# object, applet: same reason
#
#
#  It may be worthwhile to check http://ha.ckers.org/xss.html from time to
# time to find out about possible other security issues.
#

# Rather than trying to find which attributes might be problematic (black list),
# we create a database of allowed (safe) attributes which we are reasonably
# sure that they will not caus# any trouble.
# This list can always be expanded if required.
# Note that a black list would have included onblur, onload, oninit, etc.,
# with possibly some new attributes introduced by a given browser which we
# would not have foreseen.

#==========================
# The following information is taken from
# http://www.w3schools.com/html/html_standardattributes.asp

# the following core attributes are valid in all elements/tags except
# base, head, html, meta, param, script, style, and title:
# 'class', 'id', 'style', 'title'
# However, we will allow 'title' in the meta element

# The following language attributes are valid in all elements/tags except
# base, br, frame, frameset, hr, iframe, param, and script:
# 'dir', 'lang'
# we only need to include br and hr in the excluded list since the other
# tags are removed by Crunchy.

# NOTE: all of these will be included after we define a basic dict
# containing the (other) allowed attributes
#=============================

# for the other elements, we use the following
# reference: http://www.w3.org/TR/html4/index/attributes.html

# also {1} below: see also http://feedparser.org/docs/html-sanitization.html

specific_allowed = {
# the following tags are excluded mostly for security reasons
    # 'applet'
    #'basefont': [], # not allowed in {1}
    #'base': [],  # not allowed in {1}
    # button not allowed  - should be no reason
    # 'canvas': [] ; needs javascript to work; will be include by Crunchy
    # form not allowed; if required, will be inserted by Crunchy itself
    # frame not allowed (don't want stuff possibly hidden)
    # frameset not allowed
    # iframe not allowed
    # input not allowed
    # object not allowed - preventing unwanted interactions
    # param not needed: only for object
    # script not allowed!
    # textarea not needed; only included by Crunchy
# the following are meant to give choice to user; not required for Crunchy?
    #'optgroup': ['name', 'size', 'multiple'],  # Keep???
    #'option': ['name', 'size', 'multiple'],    # Keep???
    # 'select': ['name', 'size', 'multiple'], # Keep???

# Basic document structure & information
    'a': ['accesskey', 'charset', 'coords', 'href', 'hreflang', 'name',
        'rel', 'rev', 'shape', 'tabindex'],
    'address': [],
    'body': ['alink', 'bgcolor', 'link', 'text', 'vlink', 'marginheight', 'topmargin'],
    # 'background' for body not allowed - link to other file
    'head': [],
    'html': ['xmlns', 'xml:lang'],
    'link': ['charset', 'href', 'hreflang', 'media', 'rel', 'rev', 'type'],
    'meta': ['http-equiv', 'content', 'name'], #  'http-equiv' can be a potential problem
    'title': [],

# text structure
    'br' : ['clear'],
    'div': ['align', 'width', 'name'],
    'h1': ['align'],
    'h2': ['align'],
    'h3': ['align'],
    'h4': ['align'],
    'h5': ['align'],
    'h6': ['align'],
    'hr': ['align', 'noshade', 'size', 'width'], # these attributes are deprecated!
    'p': ['align'],

# lists, quotes, etc.
    'acronym': [],
    'abbr': [],
    'bdo': [],  # keep, even if not allowed in {1}
    'code': [],
    'dd': [],
    'dfn': [],
    'dir': ['compact'],  #  dir deprecated but allowed
    'dl': ['compact'],
    'dt': [],
    'blockquote': [],
    'cite': [],
    'li': ['type', 'value'], # value is deprecated... but replaced by what?
    'menu': ['compact'], # deprecated
    'ol': ['compact', 'start', 'type'],
    # start for ol is deprecated ... but replaced by ??
    'pre': ['width'],
    'q': [],
    'samp': [],
    'ul': ['compact', 'type'],

# text styles, etc.
    'b': [],
    'big': [],
    'center': [],
    'del': [],
    'em': [],
    'font': ['color', 'face', 'size'], # deprecated... but still often used!
    'i': [],
    'ins': [],
    'kbd': [],
    'quote': [],
    's': [],  # deprecated but harmless
    'small': [],
    'span': [],
    'strike': [], # deprecated
    'strong': [],
    'style': ['media', 'type'],
    'sub': [],
    'sup': [],
    'tt': [],
    'u': [], # underlined deprecated ... but still used

# tables, etc.
    'caption': ['align'],
    'col': ['align', 'char', 'charoff', 'span', 'valign', 'width'],
    'colgroup': ['align', 'char', 'charoff', 'span', 'valign', 'width'],
    'table': ['align', 'border', 'cellpadding', 'cellspacing', 'frame',
        'rules', 'summary', 'width'],
    'tbody': ['align', 'char', 'charoff', 'valign'],
    'td': ['abbr', 'align', 'axis', 'bgcolor', 'char', 'charoff', 'colspan',
        'headers', 'height', 'nowrap', 'rowspan', 'scope', 'valign', 'width'],
    'tfoot': ['align', 'char', 'charoff', 'valign'],
    'th': ['abbr', 'align', 'axis', 'bgcolor', 'char', 'charoff', 'colspan',
        'headers', 'height', 'nowrap', 'rowspan', 'scope', 'valign', 'width'],
    'thead': ['align', 'char', 'charoff', 'valign'],
    'tr': ['align', 'bgcolor', 'char', 'charoff', 'valign'],

# images, etc.
    # need to make sure 'area' is safe...
    #'area': ['accesskey', 'alt', 'coords', 'href', 'nohref', 'shape',
    # 'tabindex'],
    'img': ['align', 'alt', 'border', 'height', 'hspace', 'longdesc',
        'name', 'src', 'vspace', 'width'],
    'map': [],

# misc. - should not be needed...
    'fieldset': [],
    # isindex deprecated
    'label': ['accesskey', 'for'],
    'legend': ['accesskey'],
    'nobr': [],  # not part of any standard but used by Python.org tutorial
    'noframes': [],   # should not be needed
    'noscript' : [],   # should not be needed
    'var': []
    }

# We now build lists of allowed combinations tag/attributes based
# on the security level; we build separate dict since it needs
# to be done only once and is easier to modify individually while
# making sure we avoid accidental shared references.

allowed_attributes = {}

# Currently, the difference between normal and trusted is that
# we validate styles, links and images for normal whereas we don't
# for trusted; otherwise, they allow the same tags and attributes
# However, we do keep initialize them separately in case we
# ever distinguish further between them (like we used to)

# - normal
normal = {}
for key in specific_allowed:
    normal[key] = ['title']  # always allow title
    for item in specific_allowed[key]:
        normal[key].append(item)
    if key not in ['base', 'head', 'html', 'meta', 'param', 'script',
            'style', 'title']:
        for item in ['class', 'id', 'style', 'xml:id']:
            # harmless xml:id added for Python tutorial
            normal[key].append(item)
    if key not in ['br', 'hr']:
        for item in ['dir', 'lang']:
            normal[key].append(item)

allowed_attributes['normal'] = normal
allowed_attributes['display normal'] = normal

# - trusted only differs from normal by the validation of some
# links, images, etc.  The allowed content is the same.
allowed_attributes['trusted'] = normal
allowed_attributes['display trusted'] = normal

# - strict -
strict = {}
for key in specific_allowed:
    if key != 'style' and key != 'link' and key != 'img':
        strict[key] = ['title']  # only harmless vlam-specific attribute

strict['a'] = ['href', 'id', 'title'] # only items required for navigation
strict['meta'] = ['title', 'name']  # name needed for appending path to sys.path

allowed_attributes['strict'] = strict
allowed_attributes['display strict'] = strict


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
# in style attributes or in style sheets in "normal" security level;
# styles are not permitted in "severe" or "strict".

# we need to be less specific here: this breaks styles that use background-image among other things
dangerous_strings = ['url(', '&#']
#dangerous_strings=[]

__dangerous_text = ''

good_images = set()
bad_images = set()

def remove_unwanted(tree, page):  # partially tested
    '''Removes unwanted tags and or attributes from a "tree" created by
    ElementTree from an html page.'''
    global __dangerous_text

    # determine if site security level has been set to override
    # the default
    security_level = config[page.username]['page_security_level'](page.url)
    _allowed = allowed_attributes[security_level]
    #The following will be updated so as to add result from page.
    page.security_info = { 'level': security_level,
                          'number removed': 0,
                          'tags removed' : [],
                          'attributes removed': [],
                          'styles removed': []
                        }

# first, removing unwanted tags
    unwanted = set()
    tag_count = {}
    page.security_info['number removed'] = 0
    for element in tree.getiterator():
        if element.tag not in _allowed:
            unwanted.add(element.tag)
            if element.tag in tag_count:
                tag_count[element.tag] += 1
            else:
                tag_count[element.tag] = 1
            page.security_info['number removed'] += 1
    for tag in unwanted:
        for element in tree.getiterator(tag):
            element.clear() # removes the text
            element.tag = None  # set up so that cleanup will remove it.
        page.security_info['tags removed'].append([tag, tag_count[tag]])
    if DEBUG:
        print("These unwanted tags have been removed:")
        print(unwanted)

# next, removing unwanted attributes of allowed tags
    unwanted = set()
    count = 0
    for tag in _allowed:
        for element in tree.getiterator(tag):
            # Filtering for possible dangerous content in "styles..."
            if tag == "link":
                if not 'trusted' in security_level:
                    if not is_link_safe(element, page):
                        page.security_info['styles removed'].append(
                                                [tag, '', __dangerous_text])
                        __dangerous_text = ''
                        element.clear()
                        element.tag = None
                        page.security_info['number removed'] += 1
                        continue
            if tag == "meta":
                for attr in list(element.attrib.items()):
                    if (attr[0].lower() == 'http-equiv' and
                        attr[1].lower() != 'content-type'):
                        page.security_info['attributes removed'].append(
                                                [tag, attr[0], attr[1]])
                        del element.attrib[attr[0]]
                        page.security_info['number removed'] += 1
            for attr in list(element.attrib.items()):
                if attr[0].lower() not in _allowed[tag]:
                    if DEBUG:
                        unwanted.add(attr[0])
                    page.security_info['attributes removed'].append(
                                                [tag, attr[0], ''])
                    del element.attrib[attr[0]]
                    page.security_info['number removed'] += 1
                elif attr[0].lower() == 'href':
                    testHREF = urllib.unquote_plus(attr[1]).replace("\r","").replace("\n","")
                    testHREF = testHREF.replace("\t","").lstrip().lower()
                    if testHREF.startswith("javascript:"):
                        if DEBUG:
                            print("removing href = "+ testHREF)
                        page.security_info['attributes removed'].append(
                                                [tag, attr[0], attr[1]])
                        del element.attrib[attr[0]]
                        page.security_info['number removed'] += 1
                # Filtering for possible dangerous content in "styles..."
                elif attr[0].lower() == 'style':
                    if not 'trusted' in security_level:
                        value = attr[1].lower().replace(' ', '').replace('\t', '')
                        for x in dangerous_strings:
                            if x in value:
                                if DEBUG:
                                    unwanted.add(value)
                                page.security_info['styles removed'].append(
                                                [tag, attr[0], attr[1]])
                                del element.attrib[attr[0]]
                                page.security_info['number removed'] += 1
            # Filtering for possible dangerous content in "styles...", but
            # skipping over empty <style/> element.
            if tag == 'style' and element.text is not None:
                if not 'trusted' in security_level:
                    text = element.text.lower().replace(' ', '').replace('\t', '')
                    for x in dangerous_strings:
                        if x in text:
                            if DEBUG:
                                unwanted.add(text)
                            page.security_info['styles removed'].append(
                                                [tag, '', element.text])
                            element.clear()
                            element.tag = None
                            page.security_info['number removed'] += 1
            # making sure that this is an image
            if tag == "img" and \
                      not 'trusted' in security_level:
                _rem = False
                if 'src' in element.attrib:
                    src = element.attrib["src"]
                    if src in good_images:
                        pass
                    elif src in bad_images:
                        element.clear()
                        element.tag = None
                        # do not repeat the information; same image
                        #_rem = True
                    else:
                        if validate_image(src, page):
                            good_images.add(src)
                        else:
                            bad_images.add(src)
                            element.clear()
                            element.tag = None
                            _rem = True
                else:
                    element.clear()
                    element.tag = None
                    _rem = True
                    src = 'No src attribute included.'
                if _rem:
                    page.security_info['number removed'] += 1
                    page.security_info['attributes removed'].append(
                        ['img', 'src',
                        "could not validate or accept image:" + src])
    __cleanup(tree.getroot(), lambda e: e.tag)
    if DEBUG:
        print("These unwanted attributes have been removed:")
        print(unwanted)
    return

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

def validate_image(src, page):
    '''verifies that the file contents appears to be that of an image'''
    global root_path

    if DEBUG:
        print("entering validate_image")
        print("page.is_local "+ str(page.is_local))
        print("page.is_remote "+ str(page.is_remote))
        print("page.url "+ page.url)
        print("src "+ src)
        print("root_path "+ root_path)

    if src.startswith("http://"):
        # the image may be residing on a different site than the one
        # currently viewed.
        fn = src
    elif page.is_local:
        local_dir = os.path.split(page.url)[0]
        fn = os.path.join(local_dir, src)
    elif page.is_remote:
        fn = urlparse.urljoin(page.url, src)
    else:
        src = urlparse.urljoin(page.url, src)[1:]
        fn = os.path.join(root_path, src.decode('utf-8'))

    try:
        if DEBUG:
            print("opening fn="+ fn)
        try:
            if page.is_remote or src.startswith("http://"):
                h = urllib.urlopen(fn).read(32) #32 is all that's needed for
                                                # imghrd.what
            else:
                h = open(fn.encode(sys.getfilesystemencoding()), 'rb').read(32)
            if DEBUG:
                print("opened the file")
        except:
            if DEBUG:
                print("could not open")
            return False
        try:
            type = imghdr.what('ignore', h)
            if DEBUG:
                print("opened with imghdr.what")
                print("image type = "+ type)
                print("image src = "+ src)
            if type is not None:
                print("validated image:"+ fn)
                return True
        except:
            if DEBUG:
                print("could not open with imghdr.what")
            return False
    except:
        return False

def is_link_safe(elem, page):
    '''only keep <link> referring to style sheets that are deemed to
       be safe'''
    global __dangerous_text
    url = page.url
    if DEBUG:
        print("found link element; page url = "+ url)
    #--  Only allow style files
    if "type" in elem.attrib:
        type = elem.attrib["type"]
        if DEBUG2:
            print("type = "+ type)
        if type.lower() != "text/css":  # not a style sheet - eliminate
            __dangerous_text = 'type != "text/css"'
            return False
    else:
        if DEBUG2:
            print("type not found.")
        __dangerous_text = 'type not found'
        return False
    #--
    if "rel" in elem.attrib:
        rel = elem.attrib["rel"]
        if DEBUG2:
            print("rel = "+ rel)
        if rel.lower() != "stylesheet":  # not a style sheet - eliminate
            __dangerous_text = 'rel != "stylesheet"'
            return False
    else:
        if DEBUG2:
            print("rel not found.")
        __dangerous_text = 'rel not found'
        return False
    #--
    if "href" in elem.attrib:
        href = elem.attrib["href"]
        if DEBUG2:
            print("href = "+ href)
    else:         # no link to a style sheet: not a style sheet!
        if DEBUG2:
            print("href not found.")
        __dangerous_text = 'href not found'
        return False
    #--If we reach this point we have in principle a valid style sheet.

    try:
        link_url = find_url(url, href, page)
    except:
        print "problem encountered in security.py (trying link_url = find_url)"
        return False
    if DEBUG2:
        print("link url = "+ link_url)
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
            print("No suspicious content found in css file.")
        return True
    elif DEBUG:
        print("Suspicious content found in css file.")
        return False

    if DEBUG:
        print("should not be reached")
    return False  # don't take any chances

def find_url(url, href, page):
    '''given the url of a "parent" html page and the href of a "child"
       (specified in a link element), returns
       the complete url of the child.'''

    if "://" in url:
        if DEBUG2:
            print(":// found in url")
        return urlparse.urljoin(url, href)
    elif "://" in href:
        if DEBUG2:
            print(":// found in href")
        return href

    if page.is_local:
        base, fname = os.path.split(url)
        href = os.path.normpath(os.path.join(base, os.path.normpath(href)))
        return href

    elif href.startswith("/"):   # local css file from the root server
        try:
            href = os.path.normpath(os.path.join(root_path, os.path.normpath(href[1:])))
        except:
            try:
                href = os.path.normpath(os.path.join(
                root_path.encode(sys.getfilesystemencoding()), os.path.normpath(href[1:])))
            except:
                try:
                    href = os.path.normpath(os.path.join(
                          root_path.decode(sys.getfilesystemencoding()), os.path.normpath(href[1:])))
                except:
                    print "major problem encountered"
        return href
    else:
        base, fname = os.path.split(url)
        if DEBUG2:
            print("base path = "+ base)
            print("root_path = "+ root_path)
        href = os.path.normpath(os.path.join(base, os.path.normpath(href)))
        if href.startswith(root_path):
            if DEBUG2:
                print("href starts with rootpath")
                print("href = " + href)
            return href
        if DEBUG2:
            print("href does not start with rootpath")
            print("href = " + href)
        return os.path.normpath(os.path.join(root_path, href[1:]))

def open_local_file(url):
    if DEBUG:
        print("attempting to open file: " + url)
    if url.startswith("http://"):
        try:
            return urllib.urlopen(url)
        except:
            if DEBUG:
                print("Cannot open remote file with url= " + url)
            return False
    try:
        return open(url, mode="r")
    except IOError:
        if DEBUG2:
            print("Opening the file without encoding did not work.")
        try:
            return open(url.encode(sys.getfilesystemencoding()),
                        mode="r")
        except IOError:
            if DEBUG:
                print("Cannot open local file with url= " + url)
            return False

def scan_for_unwanted(css_file):
    '''Looks for any suspicious code in a css file

    For now, any file with "url(", "&#" and other "dangerous substrings
    in it is deemed suspicious  and will be rejected.

    returns True if suspicious code is found.'''
    global __dangerous_text

    for line in css_file.readlines():
        squished = line.replace(' ', '').replace('\t', '')
        for x in dangerous_strings:
            if x in squished:
                if DEBUG:
                    print("Found suspicious content in the following line:")
                    print(squished)
                __dangerous_text = squished
                return True
    return False
