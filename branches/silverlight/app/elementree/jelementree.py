# encoding: utf-8
"""
jelementree.py

Created by Johannes Woolard on 2008-04-10.

This is a port of Elementree built on top of the Silverlight DOM

I have abandoned this for now until I figure out how text elements behave in the Silverlight DOM
"""

from System.Windows.Browser.HtmlPage import Document

class Element(object):
    """The basic Element"""
    def __init__(self, tag, attrib={}, **args):
        try:
            self._elem = Document.CreateElement(tag)
        except:   # assume for now that any failure is due to tag actually being a DOM elem
            self._elem = tag
            
    def __delitem__(self):
        """docstring for __delitem__"""
        pass
        
    def __delslice__(self):
        """docstring for __delslice__"""
        pass
        
    def __getitem__(self):
        """docstring for __getitem__"""
        pass
        
    def __getslice__(self):
        """docstring for __getslice__"""
        pass
        
    def __len__(self):
        pass
    
    def __setitem__(self):
        """docstring for __setitem__"""
        pass
        
    def __setslice__(self):
        """docstring for __setslice__"""
        pass
        
    def append(self, element):
        """docstring for append"""
        self._elem.AppendChild(element._elem)
        
    def clear(self):
        """Clear all text in an Element
        Note that this does not clear the attributes, as this could have huge side effects in a 
        live DOM.
        """
        # the quickest way to clear the contents of an element:
        self._elem.innerHTML = ""
        
    def find(self, path):
        """docstring for find"""
        pass
        
    def findall(self):
        """docstring for findall"""
        pass
        
    def findtext(self):
        """docstring for findtext"""
        pass
        
    def get(self, key, default=None):
        """Get the value of an attribute"""
        try:
            return self._elem.GetAttribute(key)
        except:
            return default
        
    def getchildren(self):
        """Return a python list containing the children"""
        childs = self._elem.Children
        return [Element(x) for x in childs]
        
    def getiterator(self):
        """Get an iterator over the children"""
        childs = self._elem.Children
        def iter():
            x = 0
            while x < childs.Count():
                yield Element(childs.ElementAt(x))
        return [Element(x) for x in childs].getiterator()
        
    def insert(self, index, element):
        """Insert an element"""
        raise NotImplementedError
        
    def items(self):
        """docstring for items"""
        pass
        
    def keys(self):
        """docstring for keys"""
        pass
        
    def makeelement(self):
        """docstring for makeelement"""
        pass
        
    def remove(self):
        """docstring for remove"""
        pass
        
    def set(self):
        """docstring for set"""
        pass
        
        
class ElementTree(object):
    """docstring for ElementTree"""
    def __init__(self):
        pass
    
    def find(self, path):
        """docstring for find"""
        pass

    def findall(self):
        """docstring for findall"""
        pass

    def findtext(self):
        """docstring for findtext"""
        pass
        
    def getiterator(self):
        """docstring for getiterator"""
        return Element(Document.Root).getiterator()
        
    def getroot(self):
        return Element(Document.Root)


