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
# Python standard library modules
import os
import random
import urllib
from cStringIO import StringIO
# crunchy modules
import configuration
import server
request = server.CrunchyRequestHandler
# Third party modules - included in crunchy distribution
from element_tree import ElementTree

# Better safe than sorry: we do not allow the following html tags for the
# following reasons:
# script: because we want to prevent unauthorised code execution
# button, form, input: we only want Crunchy itself to create those
# *frame*: we don't want hidden frames that could be playing tricks with the
#          user (very remote possibility, but still.)
# embed: as the name indicates, can be used to embed some unwanted objects.
#
#  It may be worthwhile to check http://ha.ckers.org/xss.html from time to
# time to find out about possible other security issues.
#
tag_black_list = ["script", 'button', 'form', 'frame', 'frameset', 'input',
                    'iframe', 'embed']

# The following is not used currently
#attribute_black_list = ["text/javascript"]

# Almost all html tags can make use of these in a sensible way:
common_allowed = ['class', 'dir', 'id', 'lang', 'style', 'title']

# Rather than trying to find which attributes might be problematic (black list),
# we create a database of allowed (safe) attributes which we know will not cause
# any trouble.  This list can always be expanded if required.
# Note that a black list would have included onblur, onload, oninit, etc.,
# with possibly some new attributes introduced by a given browser which we
# would not have foreseen.
specific_allowed = {
    'a': ['charset', 'type', 'name', 'href', 'hreflang', 'rel'],
    'abbr': [],
    'acronym': [],
    'address': [],
    # applet deprecated
    'area': ['name', 'shape', 'coords', 'href', 'alt', 'nohref'],
    'b': [],
    'base': [],
    'bdo': [],
    'big': [],
    'blockquote': ['cite'],
    'body': ['bgcolor'],
    'br' : ['clear'],
    # button not allowed
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
    # dir is deprecated
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
    # menu deprecated
    'meta': ['name', 'content'], #  'http-equiv' can be a potential problem
    # noframes should not be needed
    'noscript' : [],   # should not be needed
    # object not allowed - preventing unwanted interactions
    'ol': ['start'],  # start is deprecated ... but replaced by ??
    #'optgroup': ['name', 'size', 'multiple'],  # Keep???
    #'option': ['name', 'size', 'multiple'],    # Keep???
    'p': [],
    # param not needed: only for object
    'pre': [],
    'q': ['cite'],
    # s deprecated
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
    'u': [], # deprecated ... but still used
    'ul': [],
    'var': []
    }
for key in specific_allowed:
    for item in common_allowed:
        specific_allowed[key].append(item)

commands = {}
js_memory_file = ''

class SecureSession(object):

    def __init__(self, root_dir, port):
        global js_memory_file
        self.root_dir = root_dir
        # For security reason, we create a unique session ID and use this
        # to create unique names to javascript function that interact
        # with the Python server.  This way, if ever some outside javascript
        # code were to be able to affect the execution of a crunchy page,
        # it would have to guess the unique functions name.
        # This may be an excessive precaution.
        self.session_id = str(port)+str(int(random.random()*1000000000))
        js_infile = open(os.path.join(root_dir, 'src', 'javascript',
                                  'code_exec.js'), 'r')
        js_memory_file = StringIO()
        js_memory_file.write("var session_id = " + self.session_id + '\n')
        js_memory_file.write(js_infile.read())
        # We do a similar mapping to unique names within a session
        self.map_commands()
        return

    def map_commands(self):
        commands['/'] = '/'  # safe; no need to add session_id
        request.pagemap[commands['/']] = server.get_index
        #
        commands['/exit'] = '/exit' # safe; no need to add session_id
        request.pagemap[commands['/exit']] = server.get_exit
        #
        commands['/dir'] = '/dir' + self.session_id
        request.pagemap[commands['/dir']] = server.get_dir
        #
        commands['/doc'] = '/doc' + self.session_id
        request.pagemap[commands['/doc']] = server.get_doc
        #
        commands['/load_local'] = '/load_local' + self.session_id
        request.pagemap[commands['/load_local']] = server.get_local_page
        #
        commands['/push'] = '/push' + self.session_id
        request.pagemap[commands['/push']] = server.get_push
        #
        commands['/load_external'] = '/load_external' + self.session_id
        request.pagemap[commands['/load_external']] = server.get_external_page
        #
        commands['/load_python'] = '/load_python' + self.session_id
        request.pagemap[commands['/load_python']] = server.get_python_file
        #
        commands['/save_python'] = '/save_python' + self.session_id
        #
        commands['/get_user_js'] = '/get_user_js' + self.session_id
        request.pagemap[commands['/get_user_js']] = server.get_user_js
        #
        commands['/select_language'] = '/select_language' + self.session_id
        request.pagemap[commands['/select_language']] = server.get_language
        #
        commands['/doctest'] = '/doctest' + self.session_id
        commands['/execute'] = '/execute' + self.session_id
        commands['/rawio'] = '/rawio' + self.session_id
        commands['/canvas_exec'] = '/canvas_exec' + self.session_id
        commands['/spawn'] = '/spawn' + self.session_id
        commands['/spawn_console'] = '/spawn_console' + self.session_id
        commands['/save_and_run'] = '/save_and_run' + self.session_id
        return

    def close(self):
        #remove the javascript file created for that session
        #
        # Note: this is not the correct path anymore...
        #
        #
        os.remove(os.path.join(self.root_dir, js_name))

def remove_unwanted(tree):
    '''Removes unwanted tags and or attributes from a "tree" created by
    ElementTree from an html page.'''

    for tag in tag_black_list:
        for element in tree.getiterator(tag):
            element.clear() # removes the text
            element.tag = None  # set up so that cleanup will remove it.
    for tag in specific_allowed:
        for element in tree.getiterator(tag):
            for attr in element.attrib.items():
                if attr[0].lower() not in specific_allowed[tag]:
                    del element.attrib[attr[0]]
                elif attr[0].lower() == 'href':
                    if urllib.unquote_plus(attr[1]).startswith("javascript:"):
                        del element.attrib[attr[0]]
# Trying to prevent a XSS vulnerability through
# <STYLE>BODY{-moz-binding:url(" http://ha.ckers.org/xssmoz.xml#xss")}</STYLE>
            if tag == 'style':
                text = element.text.lower().replace(' ', '')
                if ':url(' in text:
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
