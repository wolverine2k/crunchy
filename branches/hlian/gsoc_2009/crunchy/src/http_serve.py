"""
serve HTTP in a beautiful threaded way, allowing requests to branch
off into new threads and handling URL's automagically
This was built for Crunchy - and it rocks!
In some ways it is more restrictive than the default python HTTPserver -
for instance, it can only handle GET and POST requests and actually
treats them the same.
"""

import base64
import email
import sys
import time
import urllib
from BaseHTTPServer import BaseHTTPRequestHandler, HTTPServer
from SocketServer import ThreadingMixIn, TCPServer
from traceback import format_exc

# Selective imports only for urllib2 because 2to3 will not replace the
# urllib2.<method> calls below. Also, 2to3 will throw an error if we
# try to do a from _ import _.
if sys.version_info[0] < 3:
    import urllib2
    parse_http_list = urllib2.parse_http_list
    parse_keqv_list = urllib2.parse_keqv_list
else:
    from urllib.request import parse_http_list, parse_keqv_list

import src.CrunchyPlugin as CrunchyPlugin
import src.interface

DEBUG = False

realm = "Crunchy Access"

# This is convoluted because there's no way to tell 2to3 to insert a
# byte literal.
HEADER_NEWLINES = [x.encode('ascii') for x in (u'\r\n', u'\n', u'')]

if src.interface.python_version < 3:
    import md5
    def md5hex(x):
        return md5.md5(x).hexdigest()
else:
    import hashlib
    def md5hex(x):
        return hashlib.md5(x).hexdigest()

def require_digest_access_authenticate(func):
    '''A decorator to add digest authorization checks to HTTP Request Handlers'''
    accounts = src.interface.accounts

    def wrapped(self):
        method = self.command
        if not hasattr(self, 'authenticated'):
            self.authenticated =  None
        auth = self.headers.get('Authorization')
        if not self.authenticated and auth is not None:
            token, fields = auth.split(' ', 1)
            if token == 'Digest':
                cred = parse_http_list(fields)
                cred = parse_keqv_list(cred)
                if 'realm' not in cred or 'username' not in cred \
                    or 'nonce' not in cred or 'uri' not in cred or 'response' not in cred:
                    self.authenticated = False
                elif cred['realm'] != realm or cred['username'] not in accounts:
                    self.authenticated = False
                elif 'qop' in cred and ('nc' not in cred or 'cnonce' not in cred):
                    self.authenticated = False
                else:
                    if 'qop' in cred:
                        expect_response = md5hex('%s:%s'%(
                            accounts.get_password(cred['username']),
                            ':'.join([cred['nonce'],cred['nc'],cred['cnonce'],cred['qop'], md5hex('%s:%s' %(method, self.path))])
                            )
                        )
                    else:
                        expect_response = md5hex('%s:%s' %(
                            accounts.get_password(cred['username']),
                            ':'.join([cred['nonce'], md5hex('%s:%s' %(method, self.path))])
                            )
                        )
                    self.authenticated = (expect_response == cred['response'])
                    if self.authenticated:
                        self.crunchy_username = cred['username']

        if self.authenticated is None:
            msg = "You are not allowed to access this page. Please login first!"
        elif self.authenticated is False:
            msg = "Authenticated Failed"
        if  not self.authenticated :
            self.send_response(401)
            self._nonce = md5hex("%d:%s" % (time.time(), realm))
            self.send_header('WWW-Authenticate','Digest realm="%s", qop="auth", algorithm="MD5", nonce="%s"' %(realm, self._nonce))
            self.end_headers()
            self.wfile.write(msg)
        else:
            return func(self)

    return wrapped

if src.interface.accounts:
    require_authenticate = require_digest_access_authenticate
else:
    require_authenticate = lambda x: x

class MyHTTPServer(ThreadingMixIn, HTTPServer):
    daemon_threads = True
    def __init__(self, addr, rqh):
        self.default_handler = None
        self.handler_table = {}
        HTTPServer.__init__(self, addr, rqh)

    def register_default_handler(self, handler):
        """register a default handler"""
        self.default_handler = handler

    def register_handler(self, path, handler):
        """
        register a handler function
        the function should be of the form: handler(request)
        """
        self.handler_table[path] = handler

    def register_handler_instance(self, handlerinstance):
        """register a handler class instance,
        the instance functions should be of the form: class.handler(self, request)
        and should have as their docstring the path they want to handle
        """
        pass

    def get_handler(self, path):
        """returns none if no handler registered"""
        if DEBUG:
            print("entering get_handler")
        if path in self.handler_table:
            if DEBUG:
                print("path %s in self.handler_table."%path)
                print("self.handler_table[path] = %s" % self.handler_table[path])
            return self.handler_table[path]
        else:
            if DEBUG:
                print("path %s NOT in self.handler_table."%path)
            return self.default_handler

def parse_headers(fp, _class=email.message.Message):
    """Parses only RFC2822 headers from a file pointer.

    email Parser wants to see strings rather than bytes.
    But a TextIOWrapper around self.rfile would buffer too many bytes
    from the stream, bytes which we later need to read as bytes.
    So we read the correct bytes here, as bytes, for email Parser
    to parse. This code is taken directly from the Python 3 stdlib.
    """
    headers = []
    while True:
        line = fp.readline()
        headers.append(line)
        if line in HEADER_NEWLINES:
            break
    hstring = u''.encode('ascii').join(headers).decode('iso-8859-1')
    return email.parser.Parser(_class=_class).parsestr(hstring)

def message_wrapper(self, fp, irrelevant):
    return parse_headers(fp)

class HTTPRequestHandler(BaseHTTPRequestHandler):

    # In Python 3, BaseHTTPRequestHandler went from using the
    # deprecated mimetools.Message class to the new
    # email.message.Message class for self.headers. Unfortunately, the
    # two APIs are not compatible. Fortunately, there's an API in
    # place to fiddle with the class that's chosen. Here we force
    # Python 2 to adopt email.message.Message.
    if sys.version_info[0] < 0:
        MessageClass = message_wrapper

    @require_authenticate
    def do_POST(self):
        """handle an HTTP request"""
        # at first, assume that the given path is the actual path and there are no arguments
        realpath = self.path
        if DEBUG:
            print(realpath)
        argstring = ""
        self.args = {}
        # if there is a ? in the path then there are some arguments, extract them and set the path
        # to what it should be
        if self.path.find("?") > -1:
            realpath, argstring = self.path.split("?")
        self.path = urllib.unquote(realpath)
        # parse any arguments there might be
        if argstring:
            arg = []
            arglist = argstring.split('&')
            for i in arglist:
                arg = i.split('=')
                val = ''
                if len(arg) > 1:
                    self.args[arg[0]] = urllib.unquote_plus(arg[1])
        # extract any POSTDATA
        self.data = ""
        if "Content-Length" in self.headers:
            self.data = self.rfile.read(int(self.headers["Content-Length"]))
        # and run the handler
        if DEBUG:
            print("preparing to call get_handler in do_POST")
        try:
            self.server.get_handler(realpath)(self)
        except:
            self.send_response(500)
            self.end_headers()
            self.wfile.write(format_exc())

##        if CrunchyPlugin.server.still_serving == False:
##            #sometimes the program does not exit; so force it...
##            import sys
##            sys.exit()

    @require_authenticate
    def do_GET(self):
        """the same as POST, we draw no distinction"""
        self.do_POST()

    def send_response(self, code):
        BaseHTTPRequestHandler.send_response(self, code)
        self.send_header("Connection", "close")
