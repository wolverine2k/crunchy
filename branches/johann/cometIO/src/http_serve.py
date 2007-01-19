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
        realpath = self.path
        argstring = ""
        if self.path.find("?") > -1:
            realpath, argstring = self.path.split("?")
        self.path = realpath
        self.args = {}
        if argstring:
            arg = []
            arglist = argstring.split('&')
            for i in arglist:
                arg = i.split('=')
                val = ''
                if len(arg) > 1:
                    self.args[arg[0]] = urllib.unquote_plus(arg[1])
        self.data = ""
        if "Content-Length" in self.headers:
            self.data = self.rfile.read(int(self.headers["Content-Length"]))
        self.server.get_handler(realpath)(self)
        
    def do_GET(self):
        """the same as GET, we draw no distinction"""
        self.do_POST()
        
def send_response(response_code, wfile):
    """start a response"""
    wfile.write(str(response_code) + "\n")

def end_headers(wfile):
    """ends the headers of a request, ready to begin body"""
    wfile.write("\n")
