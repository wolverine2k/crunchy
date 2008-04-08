# encoding: utf-8
"""
widgets.py

Created by Johannes Woolard on 2008-04-03.
Copyright (c) 2008 Johannes Woolard. All rights reserved.

These classes implement the various Crunchy widgets for Silverlight. 
This file is written in IronPython.
"""

import code
import sys
import traceback

from System.Windows.Browser.HtmlPage import Document
from System import EventHandler

from debug_client import send_debug

class Widget(object):
    """
    Base class for all widgets, also defines some useful helper functions 
    This class defines the Crunchy API (not that this is much simpler under Silverlight because
    there is no longer any need for the hideous COMET hack :-)
    
    The self.Document instance variable gives access to the DOM - which is an instance of 
    System.Windows.Browser.HtmlDocument
    
    Important note: widgets are expected to leave the container element passed to them completely
    alone. They should only append themselves to the children of this element.
    
    Other important note: Please don't write any Javascript: it slows things down, and you can do
    it in Silverlight anyway.
    """
    def __init__(self, elem):
        """
        Initialises the widget, should be overridden (maintaining the same signature) in every
        derived widget class, and must be called on initialising every class (this initialisation
        sets up some of the API - such as the Document variable)
        """
        self.__elem = elem
        self.Document = Document
    
class Interpreter(Widget):
    """
    Implements the Crunchy Interpreter.
    """
    def __init__(self, elem):
        Widget.__init__(self, elem)
        
        # create the input elements:
        self.input = self.Document.CreateElement("input")
        self.input.SetAttribute("type", "text")
        self.input.SetStyleAttribute("width", "60%")
        
        def handle_keys(obj, args):
            print(args.keyCode)
        self.input.AttachEvent("onkeypress", EventHandler(handle_keys))
        exec_btn = self.Document.CreateElement("button")
        exec_btn.innerHTML = "Execute"
        exec_btn.AttachEvent("onclick", EventHandler(self._exec_handler))
        
        # insert the elements:
        OutputWidget(elem)
        elem.AppendChild(self.input)
        elem.AppendChild(exec_btn)
        # create the actual interpreter:
        self.interp = code.InteractiveConsole(filename="<Crunchy Interpreter>")
        # And print the first prompt:
        print ">>> ",
        
    def _exec_handler(self, obj, args):
        """Handler for the execution button"""
        code = self.input.value
        self.input.value = ""
        print code
        try:
            t = self.interp.push(code)
        except:
            print traceback.format_exc()
        if t == 1:
            print "... ",
        else:
            print">>> ",
        self.input.Focus()
        
class OutputWidget(Widget):
    """
    An output widget, at present there cannot be more than 1 in a page.
    
    This represents the old style Crunchy output widget, which cannot handle input
    """
    def __init__(self, elem):
        Widget.__init__(self, elem)
        self.output = self.Document.CreateElement("pre")
        self.output.SetStyleAttribute("display", "inline")
        self.output.SetStyleAttribute("width", "80%")
        elem.AppendChild(self.output)
        sys.stdout = self
        sys.stderr = self
        
    def write(self, data):
        t = self.Document.CreateElement("span")
        t.innerHTML = data
        self.output.AppendChild(t)
