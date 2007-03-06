"""Crunchy: serving up interactive Python tutorials
At present Crunchy can only be started from here, as a script.
"""

import socket
import webbrowser

import http_serve
import cometIO
import pluginloader

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

if __name__=="__main__":
    port = find_port(8002)
    server = http_serve.MyHTTPServer(('127.0.0.1', port), http_serve.HTTPRequestHandler)
    server.register_handler(cometIO.push_input, "/input")
    server.register_handler(cometIO.comet, "/comet")
    pluginloader.init_plugin_system(server, ["vlam_doctest","vlam_editor","testplugins","handle_default","execution","vlam_interpreter"])
    webbrowser.open('http://127.0.0.1:' + str(port) + '/')
    server.serve_forever()
