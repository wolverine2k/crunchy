"""
document.py

Exposes a single document object
"""
import src.interface
_plugin = src.interface.plugin

__all__ = ["document"]

next_free = 0
def freevar():
    """returns a variable name guaranteed to be free"""
    global next_free
    next_free += 1
    return 'a' + str(next_free)

class Document(object): 
    def exec_jscript(self, code):
        print code
        _plugin['exec_js'](_plugin['get_pageid'](), code + ";")
    
    def _get_body(self):
        return Element(self, "document.body")
    body = property(_get_body, None)
    "body: returns the BODY node of the document"
    
    def create_element(self, tagName):
        "Creates an element with the specified tag name"
        v = freevar()
        self.exec_jscript('var %s = document.createElement("%s")' % (v, tagName))
        return Element(self, v)
    
    def getElementById(self, id):
        "Returns an object reference to the identifed element"
        v = freevar()
        self.exec_jscript('var %s = document.getElementById("%s")' % (v, id))
        return Element(self, v)
        
class Element(object):
    def __init__(self, document, var):
        self.document = document
        self.var = var
    def _set_innerHTML(self, val):
        self.document.exec_jscript('%s.innerHTML= "%s"' % (self.var, val))
    innerHTML = property(None, _set_innerHTML)