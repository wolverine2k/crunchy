# encoding: utf-8
"""
cross_browser.py

Created by Johannes Woolard on 2008-04-12.

The cross browser module exeists to help iron out the differences between the browsers.
It also contains some useful helper methods.

It defines a browser class and subclasses for each of the supported browsers.

In addition the variable current_browser contains an instantiation of the appropriate class for 
the current browser.

All code specific to particular browsers shold be placed in here - and should be called (using
current_browser) from everywhere else.
"""

from System.Windows.Browser.HtmlPage import BrowserInformation, Document

class Browser(object):
    """
    Root class for all browsers, contains sensible defaults that need only be overridden for 
    browsers that vary from the norm.
    
    The following instance attributes are defined (and may be overridden in subclasses):
      * keypress_event -- the event to listen to for keypresses
      * getElementsByTagName
      * head_elem
    """
    def __init__(self):
        self.keypress_event = "onkeypress"
        self.head_elem = self.getElementsByTagName("head")[0]
        self.description = "an unknown browser"

    def getElementsByTagName(self, tag, root = Document.DocumentElement):
        """Get a list of all the element with a given tag name.
        If no root element is given this searches the whole document.
        Implemented as DFS over the document tree.
        
        ***This really needs a test case.***
        """
        elems = []
        try:
            TagName = root.TagName
            Children = root.Children
        except: # if anything happens then we should probably just give up on the element
            return []
        if TagName == tag:
            elems = [root]
        for e in Children:
            # recurse:
            elems.extend(self.getElementsByTagName(tag, e))
        return elems
        
class WebKit(Browser):
    """
    Class describing WebKit browsers (Safari et al)
    """
    def __init__(self):
        super(WebKit, self).__init__()
        # fix because WebKit doesn't raise onkeypress events when arrow keys are pressed:
        self.keypress_event = "onkeyup"
        self.pre_wrap_css = ("word-wrap", "break-word")
        self.description = "a WebKit based browser"
        
class Gecko(Browser):
    """Support for Gecko based browsers"""
    def __init__(self):
        super(Gecko, self).__init__()
        self.description = "a Gecko based browser"
        
class Camino_1_5_4(Gecko):
    """Just for fun, differentiate Camino 1.5.4"""
    def __init__(self):
        super(Camino_1_5_4, self).__init__()
        self.description = "Camino version 1.5.4"
        
# This is a useful string for deciding which browser we are using:
user_agent = BrowserInformation.UserAgent

if "WebKit" in user_agent:
    current_browser = WebKit()
elif "Camino/1.5.4" in user_agent:
    current_browser = Camino_1_5_4()
elif "Gecko" in user_agent:
    current_browser = Gecko()
else:
    current_browser = Browser()
