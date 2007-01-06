"""Sublass SimpleHTTPRequestHandler to deal with our specific needs
"""

# Python standard library modules
import os
import sys
import urllib
from SimpleHTTPServer import SimpleHTTPRequestHandler
from urllib2 import urlopen
from urllib import pathname2url
# crunchy modules
import transformer
import errors
import configuration
prefs = configuration.UserPreferences()
# The following variables is initialised in chewy.py
server = None

active_path = None
active_base = None

class ChewyRequestHandler(SimpleHTTPRequestHandler):
    '''handle HTTP requests'''
    pagemap = {}
    def do_GET(self):
        '''handle a GET request, called by methods in SimpleHTTPRequestHandler'''
        if self.pagemap == {}:
            self.pagemap = {
                "/": get_index,
                "/exit": get_exit,
                "/load_local": get_local_page,
                "/select_language": get_language,
                "/update": update_page
                }
        path, argmap = self.process_GET_path(self.path)
        if path in self.pagemap:
            data = self.pagemap[path](argmap)
            if type(data) == type(200):
                self.send_error(data)
            else:
                self.send_response(200)
                self.end_headers()
                self.wfile.write(data)
                self.wfile.flush()
                self.wfile.close()
        else:    #OK, we didn't recognise it, assume its in the local filesystem:
            #NOTE: this is undocumented - risky? works with Python 2.4
            #we can't use SimpleHTTPRequestHandler.send_head because it sends an inaccurate "Content-Length" header
            path = self.translate_path(self.path)
            ext = os.path.splitext(path)[1]
            if ext in ['.htm', '.html', ".lore"]:    #treat it as a VLAM page, even if it contains no VLAM, we can still style it
                try:
                    handle = open(path, 'r')
                except IOError, info:
                    self.send_data(errors.IOError_error_dialog(info))
                    return
                try:
                    page = transformer.VLAMPage(handle, 'file://' + path)
                except errors.HTMLTreeBuilderError, e:
                    self.send_data(errors.HTMLTreeBuilder_error_dialog(e))
                    return
                data = page.get()
                self.send_response(200)
                self.end_headers()
                self.wfile.write(data)
                return
            else:
                #its not VLAM, fall back:
                SimpleHTTPRequestHandler.do_GET(self)

    def process_GET_path(self, path):
        """process a path passed in a GET request:
            dplit of the path from the argument segment
            and return the path and a mapping of argument names to values
            - very pythonic :-)
        """
        parts = self.path.split("?")
        path = str(parts[0])
        #extract the arguments,
        # argmap will map from argument names to values as strings
        # values are decoded with urllib.unquote_plus
        argmap = {}
        arg = []
        if len(parts) > 1:
            argstring = str(parts[1])
            arglist = argstring.split('&')
            for i in arglist:
                arg = i.split('=')
                val = ''
                if len(arg) > 1:
                    argmap[arg[0]] = urllib.unquote_plus(arg[1])
        return path, argmap

    def send_data(self, data):
        '''Sends data back to browser, after successfully handling a request.'''
        # Note: It is also used to send a customized javascript error dialog
        # instead of a standard error code, like 404.
        self.send_response(200)
        self.end_headers()
        self.wfile.write(data)
        return

    def do_POST(self):
        '''Handles a POST request, called by methods in SimpleHTTPRequestHandler'''
        self.send_error(404, self.path) # not implemented yet!

def get_index(dummy):
    '''Default page displayed to user.'''
    if prefs._language == 'fr':
        path = "index_fr.html"
    else: # default is English
        path = "index.html"
    return open(path).read()

def get_exit(dummy):
    server.still_serving = False
    return """
    <html><head><title>Chewy is done!</title></head>
    <body>You may close the browser window (or tab).</body></html>"""

def get_local_page(args):
    """load an arbitrary local page into chewy"""
    # pages are encoded in utf-8; the info received is sometimes in that encoding.
    # If the path contains "weird" characters, such as &eacute; we may
    # need to decode them into the expected local default.
    global active_path, active_base
    try:
        path = args['path'].decode('utf-8').encode(sys.getdefaultencoding())
    except:
        path = args['path']
    if path.startswith('file://'):
        path = path.replace('file://', '')
    try:
        handle = open(path)
    except:
        return 404
    if path.endswith('.html') or path.endswith('.htm'):
        base = 'file://'+ os.path.dirname(path)
        vlam = transformer.VLAMPage(handle, base)
        # we save the path and not the handle as we can't read twice
        # from the same handle
        active_path = path
        active_base = base
        return vlam.get()
    else:
        return handle.read()

def update_page(args):
    '''test function for now '''
    global active_path, active_base
    handle = open(active_path)
    vlam = transformer.VLAMUpdater(handle, active_base, args['changed'])
    return vlam.get()

def get_language(args):
    import configuration
    prefs = configuration.UserPreferences()
    prefs.language = args['language']
    handle = open(prefs.options)
    vlam = transformer.VLAMPage(handle, prefs.options)
    return vlam.get()
