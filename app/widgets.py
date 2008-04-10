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
from System.Windows.Browser import HtmlEventArgs
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
        Initialises the widget, should not be overridden an any
        derived widget class.
        Widget initialisation should be done in the insert method
        """
        self.__elem = elem
        self.Document = Document
        # go ahead and insert the element:
        self.insert(elem)
        
    def insert(self, elem):
        """
        This should be overridden in derived classes to add the widget to the page.
        """
        pass
        
    def remove(self):
        """
        This should be overidden in derived classes to remove the widget from the page.
        """
        pass
    
class Interpreter(Widget):
    """
    Implements the Crunchy Interpreter.
    """
    class History(object):
        """
        A class to keep track of interpreter history
        """
        def __init__(self, input):
            self.buffer = []
            self.pos = 0
            self.input = input
        
        def move_up(self):
            """move the history up one"""
            if self.pos > 0:
                self.pos -= 1
                self.update()
        
        def update(self):
            if 0 <= self.pos < len(self.buffer):
                self.input.value = self.buffer[self.pos]
            else:
                self.input.value = ""    # if in doubt, blank it
        
        def move_down(self):
            """docstring for move_down"""
            if self.pos < len(self.buffer):
                self.pos += 1
                self.update()
        
        def push(self, line):
            self.buffer.append(line)
            self.pos = len(self.buffer)
            
    def insert(self, elem):
        # create the input elements:
        self.input = self.Document.CreateElement("input")
        self.input.SetAttribute("type", "text")
        self.input.SetStyleAttribute("width", "60%")
        
        def handle_keys(obj, args):
            #print args.CharacterCode
            if args.CharacterCode == 13:    # return or enter
                self._exec_handler(None, None)
                return
            if args.CharacterCode == 38:    # up arrow
                self.history.move_up()
                return
            if args.CharacterCode == 40:    # down arrow
                self.history.move_down()
                return
                
        self.input.AttachEvent("onkeypress", EventHandler[HtmlEventArgs](handle_keys))
        self.exec_btn = self.Document.CreateElement("button")
        self.exec_btn.innerHTML = "Execute"
        self.exec_btn.AttachEvent("onclick", EventHandler(self._exec_handler))
        
        # insert the elements:
        self.output = OutputWidget(elem)
        elem.AppendChild(self.input)
        elem.AppendChild(self.exec_btn)
        
        # create the history buffer
        self.history = Interpreter.History(self.input)
        
        # create the actual interpreter:
        self.interp = code.InteractiveConsole(filename="<Crunchy Interpreter>")
        # And print the first prompt:
        print ">>> ",
        
    def _exec_handler(self, obj, args):
        """Handler for the execution button"""
        code = self.input.value
        self.input.value = ""
        print code
        self.history.push(code)
        try:
            t = self.interp.push(code)
        except:
            print traceback.format_exc()
        if t == 1:
            print "... ",
        else:
            print">>> ",
        self.input.Focus()
        
    def remove(self):
        self.output.remove()
        self.input.Parent.RemoveChild(self.input)
        self.exec_btn.Parent.RemoveChild(self.exec_btn)
        
class OutputWidget(Widget):
    """
    An output widget, at present there cannot be more than 1 in a page.
    This represents the old style Crunchy output widget, which cannot handle input
    """
    def insert(self, elem):
        self.output = self.Document.CreateElement("pre")
        self.output.SetStyleAttribute("display", "inline")
        self.output.SetStyleAttribute("width", "80%")     
        elem.AppendChild(self.output)
        self.oldout = sys.stdout
        sys.stdout = self
        self.olderr = sys.stderr
        sys.stderr = self
        
    def write(self, data):
        t = self.Document.CreateElement("span")
        t.innerHTML = data
        self.output.AppendChild(t)
        
    def remove(self):
        """Removes the output widget from the page and resets stderr and stdout"""
        sys.stderr = self.olderr
        sys.stdout = self.oldout
        self.output.Parent.RemoveChild(self.output)
        