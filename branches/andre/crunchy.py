#!/usr/bin/env python
'''Serves up ready formatted interactive tutorials over http'''

# Python standard library modules
import BaseHTTPServer
import os
import socket
import sys
import webbrowser
# crunchy modules
import src.configuration as configuration
import src.interpreters as interpreters
import src.security as security
import src.server
import src.utilities
# Third party modules
try:
    import psyco
    psyco.full()
    print "Succesfully imported psyco"
except ImportError:
    pass
# globally defined objects
root_dir = os.getcwd()
prefs = configuration.UserPreferences(root_dir)
sys.stdout = src.utilities.ThreadStream(sys.stdout)
sys.stderr = src.utilities.ThreadStream(sys.stderr)
serverclass = BaseHTTPServer.HTTPServer
handlerclass = src.server.CrunchyRequestHandler

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

def run(filename='', host='127.0.0.1', port=find_port(5555), openbrowser=True):
    """
    Run Crunchy Frog
    
    By default it serves on the first free port on above 5555 on 127.0.0.1,
    and opens a browser window to display the URL http://127.0.0.1:port/
    """
    root_dir = os.getcwd()
    session = security.SecureSession(root_dir, port)
    serveraddress = (host, port)
    server = serverclass(serveraddress, handlerclass)
    src.server.repl = interpreters.HTTPrepl()
    src.server.server = server
    server.still_serving = True
    if openbrowser:
        webbrowser.open('http://' + host + ':' + str(port) + filename)
    print 'Crunchy Server: serving up interactive tutorials on port %s' % port
    try:
        while server.still_serving:
            server.handle_request()
    finally:
        session.close()

# Do something useful if we're launching as an applet:
if __name__ == '__main__':
    syshost = '127.0.0.1'
    # usage: python crunchy.py [port [start_webbrowser]]
    if len(sys.argv) > 1:
        sysport = int(sys.argv[1])
        start_webbrowser = False
        if len(sys.argv) > 2:
            if sys.argv[2] == "True":
                start_webbrowser = True 
    else:
        start_webbrowser = True
    run(host=syshost, openbrowser=start_webbrowser)
