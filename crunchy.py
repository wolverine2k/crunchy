#!/usr/bin/env python
'''Serves up ready formatted interactive tutorials over http'''

def _(arg):
    return arg

import os
import sys
import BaseHTTPServer
import webbrowser
import socket

root_dir = os.getcwd()

import src.preferences as preferences
prefs = preferences.UserPreferences(root_dir)

import src.security as security
import src.crunchyrequest as crunchyrequest
import src.crunchypages as crunchypages
import src.httprepl as httprepl
import src.thread_stream as thread_stream

try:
    import psyco
    psyco.full()
    print "Succesfully imported psyco"
except ImportError:
    pass

sys.stdout = thread_stream.ThreadStream(sys.stdout)
sys.stderr = thread_stream.ThreadStream(sys.stderr)

serverclass = BaseHTTPServer.HTTPServer
handlerclass = crunchyrequest.CrunchyRequestHandler

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
    session = security.SecureSession(root_dir, port)
    serveraddress = (host, port)
    server = serverclass(serveraddress, handlerclass)
    crunchypages.repl = httprepl.HTTPrepl()
    crunchypages.server = server
    server.still_serving = True
    if openbrowser:
        webbrowser.open('http://' + host + ':' + str(port) + filename)
    print _('Crunchy Frog Server: serving up ready formatted interactive tutorials on port %s') % port
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
