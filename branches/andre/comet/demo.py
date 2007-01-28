"""demo the new server"""

import socket
import webbrowser

import http_serve
import cometIO
from http_path import handle_default

interpreter = """
import code
t = code.InteractiveConsole()
t.interact()
"""

def find_port(start):
    """finds the first free port on 127.0.0.1 starting at start"""
    finalport = None
    testsock = socket.socket()
    testn = start
    while not finalport and (testn < 65536):
        try:
            testsock.bind(('127.0.0.1', testn))
            finalport = testn
        except socket.error:
            testn += 1
    testsock.close()
    return finalport

cometIO.do_exec(interpreter, "0")

port = find_port(8002)

s = http_serve.MyHTTPServer(('127.0.0.1', port), http_serve.HTTPRequestHandler)

s.register_default_handler(handle_default)
s.register_handler(cometIO.push_input, "/input")
s.register_handler(cometIO.comet, "/comet")
s.register_handler(cometIO.exec_callback, "/exec")
webbrowser.open('http://127.0.0.1:' + str(port) + '/')
s.serve_forever()
