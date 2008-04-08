#!/usr/bin/env python
# encoding: utf-8
"""
debug_server.py

Created by Johannes Woolard on 2008-03-28.


A server for debugging multithreaded silverlight scripts.

This is to get around the limitation that only the one thread can access the UI.
Using this server, any thread can display output by connecting over TCP to port
54321 on 127.0.0.1
"""

from SocketServer import TCPServer, StreamRequestHandler
import sys

class DebugRequestHandler(StreamRequestHandler):
    def handle(self):
        print "\n************* Request Recieved ****************"
        for data in self.rfile:
            print data
        print "************* Request Ended ****************"
        
def main():
	print "Crunchy Silverlight Debug Server"
	print "Connect on port 4511"
	server = TCPServer(('127.0.0.1', 4511), DebugRequestHandler)
	server.serve_forever()

if __name__ == '__main__':
	main()

