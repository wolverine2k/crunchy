#!/usr/bin/env python
'''Enables easy vlam markup of python tutorials'''

# Python standard library modules
import BaseHTTPServer
import os
import socket
import sys
import webbrowser
# chewy modules
import src.configuration as configuration
# need to set the root directory for use in other modules
root_dir = os.getcwd()
prefs = configuration.UserPreferences(root_dir)
import src.server
#import src.utilities
# Third party modules
try:
    import psyco
    psyco.full()
    print "Succesfully imported psyco"
except ImportError:
    pass

serverclass = BaseHTTPServer.HTTPServer
handlerclass = src.server.ChewyRequestHandler

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
    Run Chewy

    By default it serves on the first free port on above 5555 on 127.0.0.1,
    and opens a browser window to display the URL http://127.0.0.1:port/
    """
    root_dir = os.getcwd()
    serveraddress = (host, port)
    server = serverclass(serveraddress, handlerclass)
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
