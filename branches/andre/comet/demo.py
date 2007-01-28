"""demo the new server"""

import socket
import webbrowser

import http_serve
import cometIO

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


def handle_default(request):
    ''' Returns the default test_page.'''
    request.send_response(200)
    request.end_headers()
    request.wfile.write(test_page)

cometIO.do_exec(interpreter, "0")

test_page = open("comet_index.html").read()

port = find_port(8002)

s = http_serve.MyHTTPServer(('127.0.0.1', port), http_serve.HTTPRequestHandler)

s.register_default_handler(handle_default)
s.register_handler(cometIO.push_input, "/input")
s.register_handler(cometIO.comet, "/comet")
s.register_handler(cometIO.exec_callback, "/exec")
webbrowser.open('http://127.0.0.1:' + str(port) + '/')
s.serve_forever()
