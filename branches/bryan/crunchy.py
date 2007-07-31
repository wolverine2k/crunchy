"""Crunchy: serving up interactive Python tutorials
At present Crunchy can only be started from here, as a script.
"""

import socket
import webbrowser
import sys
import imp

"""Attempt to import all_plugins so that py2exe knows to
import specific modules that are required by the plugins
"""
try:
    import all_plugins

    # override the default find_module, which is only used to determine path
    imp._find_module = imp.find_module
    def _find_module(name, path=None):
        if name == "crunchy":
            return ("","","")
        return imp._find_module(name, path)
    imp.find_module = _find_module

except:
    pass

import src.configuration as configuration
import src.http_serve as http_serve
import src.cometIO as cometIO
import src.pluginloader as pluginloader

def find_port(start=8001):
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

def run_crunchy(host='127.0.0.1', port=None, url=None):
    if port is None:
        port = find_port()
    server = http_serve.MyHTTPServer((host, port), http_serve.HTTPRequestHandler)
    pluginloader.init_plugin_system(server)
    if url is None:
        url = 'http://' + host + ':' + str(port) + '/'
    webbrowser.open(url)
    # print this info so that, if the right browser does not open,
    # the user can copy and paste the URL
    print '\nCrunchy Server: serving up interactive tutorials at URL %s\n'%url
    server.still_serving = True
    while server.still_serving:
        server.handle_request()

if __name__ == "__main__":
    run_crunchy()
