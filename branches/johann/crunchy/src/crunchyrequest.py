"""Sublass SimpleHTTPRequestHandler to deal with our specific needs
"""
from SimpleHTTPServer import SimpleHTTPRequestHandler
import urllib
import os
import sys
from elementtree.ElementTree import ElementTree

import crunchypages
import interp_backend
import canvas
import crunchytute
import errorhandler
import exec_external
import security
import widgets

class CrunchyRequestHandler(SimpleHTTPRequestHandler):
    '''handle HTTP requests'''
    pagemap = {}
    
    def do_GET(self):
        '''handle a GET request, called by methods in SimpleHTTPRequestHandler'''       
        path, argmap = self.process_GET_path(self.path)
        if path in self.pagemap:
            data = self.pagemap[path](argmap)
            if type(data) == type(200):
                self.send_error(data)
            else:
                self.send_response(200)
                self.end_headers()
                self.wfile.write(data)
                self.wfile.flush()
                self.wfile.close()
        else:    #OK, we didn't recognise it, assume its in the local filesystem:
            #NOTE: this is undocumented - risky? works with Python 2.4
            #we can't use SimpleHTTPRequestHandler.send_head because it sends an inaccurate "Content-Length" header
            path = self.translate_path(self.path)
            ext = os.path.splitext(path)[1]
            if ext in ['.htm', '.html', ".lore"]:    #treat it as a VLAM page, even if it contains no VLAM, we can still style it
                try:
                    handle = open(path, 'r')
                except IOError, info:
                    self.send_data(errorhandler.IOError_error_dialog(info))
                    return
                try:
                    page = crunchytute.VLAMPage(handle, 'file://' + path)
                except errorhandler.HTMLTreeBuilderError, e:
                    self.send_data(errorhandler.HTMLTreeBuilder_error_dialog(e))
                    return 
                data = page.get()
                self.send_response(200)
                self.end_headers()
                self.wfile.write(data)
                return
            else:
                #its not VLAM, fall back:
                SimpleHTTPRequestHandler.do_GET(self)
    
    def process_GET_path(self, path):
        """process a path passed in a GET request:
            dplit of the path from the argument segment 
            and return the path and a mapping of argument names to values
            - very pythonic :-)
        """
        parts = self.path.split("?")
        path = str(parts[0])
        #extract the arguments, 
        # argmap will map from argument names to values as strings
        # values are decoded with urllib.unquote_plus
        argmap = {}
        arg = []
        if path.startswith("/get_user_js"):  # special Crunchy case
            argmap['path'] = str(parts[1])
        elif len(parts) > 1:
            argstring = str(parts[1])
            arglist = argstring.split('&')
            for i in arglist:
                arg = i.split('=')
                val = ''
                if len(arg) > 1:
                    argmap[arg[0]] = urllib.unquote_plus(arg[1])
        return path, argmap

    def send_data(self, data):
        '''Sends data back to browser, after successfully handling a request.'''
        # Note: It is also used to send a customized javascript error dialog
        # instead of a standard error code, like 404.
        self.send_response(200)
        self.end_headers()
        self.wfile.write(data)
        return
        
    def do_POST(self):
        '''Handles a POST request, called by methods in SimpleHTTPRequestHandler'''
        if self.path.startswith(security.commands["/push"]):  #interactive interpreter
            args = {}
            args["line"] = self.rfile.read(int(self.headers["Content-Length"]))
            args["name"] = self.path.split('?')[1]
            data = self.pagemap[security.commands["/push"]](args)
            if type(data) == type(200):
                self.send_error(data)
            else:
                self.send_data(data)
        elif self.path.startswith(security.commands["/execute"]):           #code editor
            code = self.rfile.read(int(self.headers["Content-Length"]))
            uid = self.path.split('?')[1]
            i = interp_backend.CrunchyInterpreter(code, uid)
            i.start()
            #out_xml = widgets.ExecOutput(uid)
            #t = ElementTree(element=out_xml)
            self.send_response(200)
            self.end_headers()
            #t.write(self.wfile)
            
        elif self.path.startswith(security.commands["/doctest"]):      #doctest
            code = self.rfile.read(int(self.headers["Content-Length"]))
            parts = self.path.split('?')
            self.send_response(200)
            self.end_headers()
            interp_backend.run_doctest(code, parts[1])
        elif self.path.startswith(security.commands['/canvas_exec']):
            canvas_id = self.path.split('?')[1]
            try:
                data = canvas.run (canvas_id, 
                          self.rfile.read(int(self.headers["Content-Length"])))
                self.send_data(data)
            except errorhandler.ColourNameError, info:
                self.send_error(400, errorhandler.colour_name_dialog(info))
            except Exception, info:
                self.send_error(400, errorhandler.canvas_error_dialog(info))

        elif self.path.startswith(security.commands['/rawio']):
            bufname = self.path.split('?')[1]  
            print bufname  
            if bufname in interp_backend.interpreters:  
                i = interp_backend.interpreters[bufname]  
                #print self.headers  
                self.send_response(200)  
                self.end_headers()   
                data = i.get()  
                self.wfile.write(data)  
                if not i.isAlive():  
                    del interp_backend.interpreters[bufname]
            else:
                self.send_error(403)
        elif self.path.startswith(security.commands['/spawn_console']):
            data = self.rfile.read(int(self.headers["Content-Length"]))
            exec_external.exec_external(data, console=True)
        elif self.path.startswith(security.commands['/spawn']):
            data = self.rfile.read(int(self.headers["Content-Length"]))
            exec_external.exec_external(data, console=False)
        else:
            self.send_error(404, self.path)
