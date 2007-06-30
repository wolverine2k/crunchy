"""
serve HTTP in a beautiful threaded way, allowing requests to branch
off into new threads and handling URL's automagically
This was built for Crunchy - and it rocks!
In some ways it is more restrictive than the default python HTTPserver -
for instance, it can only handle GET and POST requests.
"""

from SocketServer import ThreadingMixIn, TCPServer
from BaseHTTPServer import BaseHTTPRequestHandler, HTTPServer
from sys import stderr
import urllib
from traceback import format_exc

class MyHTTPServer(ThreadingMixIn, HTTPServer):
    daemon_threads = True
    def __init__(self, addr, rqh):
        self.default_handler = None
        self.handler_table = {}
        HTTPServer.__init__(self, addr, rqh)

    def register_default_handler(self, handler):
        """register a default handler"""
        self.default_handler = handler

    def register_handler(self, handler, path):
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
        if path in self.handler_table:
            return self.handler_table[path]
        else:
            return self.default_handler

class HTTPRequestHandler(BaseHTTPRequestHandler):
    def do_POST(self):
        """handle an HTTP request"""
        # at first, assume that the given path is the actual path and there are no arguments
        realpath = self.path
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
        try:
            self.server.get_handler(realpath)(self)
        except:
            # if there is an error, say so
            self.send_response(500)
            self.end_headers()
            self.wfile.write(format_exc())

    def do_GET(self):
        """the same as GET, we draw no distinction"""
        self.do_POST()

    def send_response(self, code):
        BaseHTTPRequestHandler.send_response(self, code)
        self.send_header("Connection", "close")

