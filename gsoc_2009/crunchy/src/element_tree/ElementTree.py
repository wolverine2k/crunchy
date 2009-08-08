#
# ElementTree
# $Id: ElementTree.py 2326 2005-03-17 07:45:21Z fredrik $
#
# light-weight XML support for Python 2.0 and later.
#
# history:
# 2001-10-20 fl   created (from various sources)
# 2001-11-01 fl   return root from parse method
# 2002-02-16 fl   sort attributes in lexical order
# 2002-04-06 fl   TreeBuilder refactoring, added PythonDoc markup
# 2002-05-01 fl   finished TreeBuilder refactoring
# 2002-07-14 fl   added basic namespace support to ElementTree.write
# 2002-07-25 fl   added QName attribute support
# 2002-10-20 fl   fixed encoding in write
# 2002-11-24 fl   changed default encoding to ascii; fixed attribute encoding
# 2002-11-27 fl   accept file objects or file names for parse/write
# 2002-12-04 fl   moved XMLTreeBuilder back to this module
# 2003-01-11 fl   fixed entity encoding glitch for us-ascii
# 2003-02-13 fl   added XML literal factory
# 2003-02-21 fl   added ProcessingInstruction/PI factory
# 2003-05-11 fl   added tostring/fromstring helpers
# 2003-05-26 fl   added ElementPath support
# 2003-07-05 fl   added makeelement factory method
# 2003-07-28 fl   added more well-known namespace prefixes
# 2003-08-15 fl   fixed typo in ElementTree.findtext (Thomas Dartsch)
# 2003-09-04 fl   fall back on emulator if ElementPath is not installed
# 2003-10-31 fl   markup updates
# 2003-11-15 fl   fixed nested namespace bug
# 2004-03-28 fl   added XMLID helper
# 2004-06-02 fl   added default support to findtext
# 2004-06-08 fl   fixed encoding of non-ascii element/attribute names
# 2004-08-23 fl   take advantage of post-2.1 expat features
# 2005-02-01 fl   added iterparse implementation
# 2005-03-02 fl   fixed iterparse support for pre-2.2 versions
# 2009-06-10      Updated for porting Crunchy to Python 3 by Hao Lian
#
# Copyright (c) 1999-2005 by Fredrik Lundh.  All rights reserved.
#
# fredrik@pythonware.com
# http://www.pythonware.com
#
# --------------------------------------------------------------------
# The ElementTree toolkit is
#
# Copyright (c) 1999-2005 by Fredrik Lundh
#
# By obtaining, using, and/or copying this software and/or its
# associated documentation, you agree that you have read, understood,
# and will comply with the following terms and conditions:
#
# Permission to use, copy, modify, and distribute this software and
# its associated documentation for any purpose and without fee is
# hereby granted, provided that the above copyright notice appears in
# all copies, and that both that copyright notice and this permission
# notice appear in supporting documentation, and that the name of
# Secret Labs AB or the author not be used in advertising or publicity
# pertaining to distribution of the software without specific, written
# prior permission.
#
# SECRET LABS AB AND THE AUTHOR DISCLAIMS ALL WARRANTIES WITH REGARD
# TO THIS SOFTWARE, INCLUDING ALL IMPLIED WARRANTIES OF MERCHANT-
# ABILITY AND FITNESS.  IN NO EVENT SHALL SECRET LABS AB OR THE AUTHOR
# BE LIABLE FOR ANY SPECIAL, INDIRECT OR CONSEQUENTIAL DAMAGES OR ANY
# DAMAGES WHATSOEVER RESULTING FROM LOSS OF USE, DATA OR PROFITS,
# WHETHER IN AN ACTION OF CONTRACT, NEGLIGENCE OR OTHER TORTIOUS
# ACTION, ARISING OUT OF OR IN CONNECTION WITH THE USE OR PERFORMANCE
# OF THIS SOFTWARE.
# --------------------------------------------------------------------

__all__ = [
    # public symbols
    "Comment",
    "dump",
    "Element", "ElementTree",
    "fromstring",
    "iselement", "iterparse",
    "parse",
    "PI", "ProcessingInstruction",
    "QName",
    "SubElement",
    "tostring",
    "TreeBuilder",
    "VERSION", "XML",
    "XMLTreeBuilder",
    ]

ATTRIB_REPLACEMENTS = [u"& &amp;",
                       u"' &apos;",
                       u'" &quot;',
                       u"< &lt;",
                       u"> &gt;"];

CDATA_REPLACEMENTS = [u"& &amp;",
                      u"< &lt;",
                      u"> &gt;"];

##
# The <b>Element</b> type is a flexible container object, designed to
# store hierarchical data structures in memory. The type can be
# described as a cross between a list and a dictionary.
# <p>
# Each element has a number of properties associated with it:
# <ul>
# <li>a <i>tag</i>. This is a string identifying what kind of data
# this element represents (the element type, in other words).</li>
# <li>a number of <i>attributes</i>, stored in a Python dictionary.</li>
# <li>a <i>text</i> string.</li>
# <li>an optional <i>tail</i> string.</li>
# <li>a number of <i>child elements</i>, stored in a Python sequence</li>
# </ul>
#
# To create an element instance, use the {@link #Element} or {@link
# #SubElement} factory functions.
# <p>
# The {@link #ElementTree} class can be used to wrap an element
# structure, and convert it from and to XML.
##

import codecs
import sys
import re

# These functions are here to help with porting Crunchy and should be
# removed later.
import traceback
import logging

# Unfortunately, doctests creates its own standard out.
# http://bytes.com/groups/python/592788-logging-module-doctest
class WrapStdOut(object):
    def __getattr__(self, name):
        return getattr(sys.stdout, name)

def log():
    log = logging.getLogger(__name__)
    h   = logging.StreamHandler(WrapStdOut())
    f   = logging.Formatter("%(levelname)s:%(name)s:line %(lineno)d: %(message)s")
    h.setFormatter(f)
    log.addHandler(h)
    return log

log = log()
DEBUG = False

def format_stack():
    return ''.join(traceback.format_stack())

class _SimpleElementPath(object):
    # emulate pre-1.2 find/findtext/findall behaviour
    def find(self, element, tag):
        for elem in element:
            if elem.tag == tag:
                return elem
        return None
    def findtext(self, element, tag, default=None):
        for elem in element:
            if elem.tag == tag:
                return elem.text or u""
        return default
    def findall(self, element, tag):
        if tag[:3] == u".//":
            return element.getiterator(tag[3:])
        result = []
        for elem in element:
            if elem.tag == tag:
                result.append(elem)
        return result

try:
    import ElementPath
except ImportError:
    # FIXME: issue warning in this case?
    ElementPath = _SimpleElementPath()

# TODO: add support for custom namespace resolvers/default namespaces
# TODO: add improved support for incremental parsing

VERSION = "1.2.6"

##
# Internal element class.  This class defines the Element interface,
# and provides a reference implementation of this interface.
# <p>
# You should not create instances of this class directly.  Use the
# appropriate factory functions instead, such as {@link #Element}
# and {@link #SubElement}.
#
# @see Element
# @see SubElement
# @see Comment
# @see ProcessingInstruction

class _ElementInterface(object):
    # <tag attrib>text<child/>...</tag>tail

    ##
    # (Attribute) Element tag.

    tag = None

    ##
    # (Attribute) Element attribute dictionary.  Where possible, use
    # {@link #_ElementInterface.get},
    # {@link #_ElementInterface.set},
    # {@link #_ElementInterface.keys}, and
    # {@link #_ElementInterface.items} to access
    # element attributes.

    attrib = None

    ##
    # (Attribute) Text before first subelement.  This is either a
    # string or the value None, if there was no text.

    text = None

    ##
    # (Attribute) Text after this element's end tag, but before the
    # next sibling element's start tag.  This is either a string or
    # the value None, if there was no text.

    tail = None # text after end tag, if any

    def __init__(self, tag, attrib):
        self.tag = tag
        self.attrib = {}

        for key in attrib:
            value = attrib[key]
            if DEBUG and not isinstance(attrib[key], unicode):
                log.error('Not Unicode: %s' % [key, attrib[key]])
                log.error(format_stack())
                value = value.decode('utf8')
            self.attrib[key] = value

        self._children = []

    def __repr__(self):
        return "<Element %s at %x>" % (self.tag, id(self))

    ##
    # Creates a new element object of the same type as this element.
    #
    # @param tag Element tag.
    # @param attrib Element attributes, given as a dictionary.
    # @return A new element instance.

    def makeelement(self, tag, attrib):
        return Element(tag, attrib)

    ##
    # Returns the number of subelements.
    #
    # @return The number of subelements.

    def __len__(self):
        return len(self._children)

    ##
    # Returns the given subelement(s).
    #
    # @param index What subelement to return.
    # @return The given subelement.
    # @exception IndexError If the given element does not exist.

    def __getitem__(self, index):
        return self._children[index]

    ##
    # Replaces the given subelement(s).
    #
    # @param index What subelement to replace.
    # @param element The new element value.
    # @exception IndexError If the given element does not exist.
    # @exception AssertionError If element is not a valid object.

    def __setitem__(self, index, value):
        if isinstance(index, slice):
            assert iselements(value)
        else:
            assert iselement(value)

        self._children[index] = value

    ##
    # Deletes the given subelement(s).
    #
    # @param index What subelement to delete.
    # @exception IndexError If the given element does not exist.

    def __delitem__(self, index):
        del self._children[index]

    ##
    # Adds a subelement to the end of this element.
    #
    # @param element The element to add.
    # @exception AssertionError If a sequence member is not a valid object.

    def append(self, element):
        assert iselement(element)
        self._children.append(element)

    ##
    # Inserts a subelement at the given position in this element.
    #
    # @param index Where to insert the new subelement.
    # @exception AssertionError If the element is not a valid object.

    def insert(self, index, element):
        assert iselement(element)
        self._children.insert(index, element)

    ##
    # Removes a matching subelement.  Unlike the <b>find</b> methods,
    # this method compares elements based on identity, not on tag
    # value or contents.
    #
    # @param element What element to remove.
    # @exception ValueError If a matching element could not be found.
    # @exception AssertionError If the element is not a valid object.

    def remove(self, element):
        assert iselement(element)
        self._children.remove(element)

    ##
    # Returns all subelements.  The elements are returned in document
    # order.
    #
    # @return A list of subelements.
    # @defreturn list of Element instances

    def getchildren(self):
        return self._children

    ##
    # Finds the first matching subelement, by tag name or path.
    #
    # @param path What element to look for.
    # @return The first matching element, or None if no element was found.
    # @defreturn Element or None

    def find(self, path):
        return ElementPath.find(self, path)

    ##
    # Finds text for the first matching subelement, by tag name or path.
    #
    # @param path What element to look for.
    # @param default What to return if the element was not found.
    # @return The text content of the first matching element, or the
    #     default value no element was found.  Note that if the element
    #     has is found, but has no text content, this method returns an
    #     empty string.
    # @defreturn string

    def findtext(self, path, default=None):
        return ElementPath.findtext(self, path, default)

    ##
    # Finds all matching subelements, by tag name or path.
    #
    # @param path What element to look for.
    # @return A list or iterator containing all matching elements,
    #    in document order.
    # @defreturn list of Element instances

    def findall(self, path):
        return ElementPath.findall(self, path)

    ##
    # Resets an element.  This function removes all subelements, clears
    # all attributes, and sets the text and tail attributes to None.

    def clear(self):
        self.attrib.clear()
        self._children = []
        self.text = self.tail = None

    ##
    # Gets an element attribute.
    #
    # @param key What attribute to look for.
    # @param default What to return if the attribute was not found.
    # @return The attribute value, or the default value, if the
    #     attribute was not found.
    # @defreturn string or None

    def get(self, key, default=None):
        return self.attrib.get(key, default)

    ##
    # Sets an element attribute.
    #
    # @param key What attribute to set.
    # @param value The attribute value.

    def set(self, key, value):
        if DEBUG and not isinstance(value, unicode):
            log.error('Not Unicode: %s' % [key, value])
            log.error(format_stack())
            value = value.decode('utf8')

        self.attrib[key] = value

    ##
    # Gets a list of attribute names.  The names are returned in an
    # arbitrary order (just like for an ordinary Python dictionary).
    #
    # @return A list of element attribute names.
    # @defreturn list of strings

    def keys(self):
        return self.attrib.keys()

    ##
    # Gets element attributes, as a sequence.  The attributes are
    # returned in an arbitrary order.
    #
    # @return A list of (name, value) tuples for all attributes.
    # @defreturn list of (string, string) tuples

    def items(self):
        return self.attrib.items()

    ##
    # Creates a tree iterator.  The iterator loops over this element
    # and all subelements, in document order, and returns all elements
    # with a matching tag.
    # <p>
    # If the tree structure is modified during iteration, the result
    # is undefined.
    #
    # @param tag What tags to look for (default is to return all elements).
    # @return A list or iterator containing all the matching elements.
    # @defreturn list or iterator

    def getiterator(self, tag=None):
        nodes = []
        if tag == u"*":
            tag = None
        if tag is None or self.tag == tag:
            nodes.append(self)
        for node in self._children:
            nodes.extend(node.getiterator(tag))
        return nodes

# compatibility
_Element = _ElementInterface

class UnicodeDict(dict):
    """Enforces Unicode with an assertion where possible. This
    definitely affects performance and should be removed after Unicode
    porting is finished."""

    def __init__(self, adict={}):
        x = {}
        for key in adict:
            value = adict[key]
            if DEBUG and not isinstance(value, unicode):
                log.error('Not Unicode: %s' % [key, value])
                log.error(format_stack())
                value = value.decode('utf8')
            x[key] = value

        dict.__init__(self, x)

    def update(self, adict):
        x = {}
        for key in adict:
            value = adict[key]
            if DEBUG and not isinstance(value, unicode):
                log.error('Not Unicode: %s' % [key, value])
                log.error(format_stack())
                value = value.decode('utf8')
            x[key] = value

        return dict.update(self, x)

    def __setitem__(self, index, value):
        if DEBUG and not isinstance(value, unicode):
            log.error('Not Unicode: %s' % [index, value])
            log.error(format_stack())
            value = value.decode('utf8')

        return dict.__setitem__(self, index, value)

##
# Element factory.  This function returns an object implementing the
# standard Element interface.  The exact class or type of that object
# is implementation dependent, but it will always be compatible with
# the {@link #_ElementInterface} class in this module.
# <p>
# The element name, attribute names, and attribute values can be
# either 8-bit ASCII strings or Unicode strings.
#
# @param tag The element name.
# @param attrib An optional dictionary, containing element attributes.
# @param **extra Additional attributes, given as keyword arguments.
# @return An element instance.
# @defreturn Element

def Element(tag, attrib={}, **extra):
    if DEBUG:
        attrib = UnicodeDict(attrib)
    else:
        attrib = attrib.copy()
    attrib.update(extra)
    return _ElementInterface(tag, attrib)

##
# Subelement factory.  This function creates an element instance, and
# appends it to an existing element.
# <p>
# The element name, attribute names, and attribute values can be
# either 8-bit ASCII strings or Unicode strings.
#
# @param parent The parent element.
# @param tag The subelement name.
# @param attrib An optional dictionary, containing element attributes.
# @param **extra Additional attributes, given as keyword arguments.
# @return An element instance.
# @defreturn Element

def SubElement(parent, tag, attrib={}, **extra):
    attrib = attrib.copy()
    attrib.update(extra)
    element = parent.makeelement(tag, attrib)
    parent.append(element)
    return element

##
# Comment element factory.  This factory function creates a special
# element that will be serialized as an XML comment.
# <p>
# The comment string can be either an 8-bit ASCII string or a Unicode
# string.
#
# @param text A string containing the comment string.
# @return An element instance, representing a comment.
# @defreturn Element

def Comment(text=None):
    element = Element(Comment)
    element.text = text
    return element

##
# PI element factory.  This factory function creates a special element
# that will be serialized as an XML processing instruction.
#
# @param target A string containing the PI target.
# @param text A string containing the PI contents, if any.
# @return An element instance, representing a PI.
# @defreturn Element

def ProcessingInstruction(target, text=None):
    element = Element(ProcessingInstruction)
    element.text = target
    if text:
        element.text = element.text + u" " + text
    return element

PI = ProcessingInstruction

##
# QName wrapper.  This can be used to wrap a QName attribute value, in
# order to get proper namespace handling on output.
#
# @param text A string containing the QName value, in the form {uri}local,
#     or, if the tag argument is given, the URI part of a QName.
# @param tag Optional tag.  If given, the first argument is interpreted as
#     an URI, and this argument is interpreted as a local name.
# @return An opaque object, representing the QName.

class QName(object):
    def __init__(self, text_or_uri, tag=None):
        if tag:
            text_or_uri = u"{%s}%s" % (text_or_uri, tag)
        self.text = text_or_uri
    def __str__(self):
        return self.text
    def __hash__(self):
        return hash(self.text)
    def __cmp__(self, other):
        if isinstance(other, QName):
            return cmp(self.text, other.text)
        return cmp(self.text, other)

##
# ElementTree wrapper class.  This class represents an entire element
# hierarchy, and adds some extra support for serialization to and from
# standard XML.
#
# @param element Optional root element.
# @keyparam file Optional file handle or name.  If given, the
#     tree is initialized with the contents of this XML file.

class ElementTree(object):

    def __init__(self, element=None, file=None):
        assert element is None or iselement(element)
        self._root = element # first node
        if file:
            self.parse(file)

    ##
    # Gets the root element for this tree.
    #
    # @return An element instance.
    # @defreturn Element

    def getroot(self):
        return self._root

    ##
    # Replaces the root element for this tree.  This discards the
    # current contents of the tree, and replaces it with the given
    # element.  Use with care.
    #
    # @param element An element instance.

    def _setroot(self, element):
        assert iselement(element)
        self._root = element

    ##
    # Loads an external XML document into this element tree.
    #
    # @param source A file name or file object.
    # @param encoding Encoding for the file.
    # @param parser An optional parser instance.  If not given, the
    #     standard {@link XMLTreeBuilder} parser is used.
    # @return The document root element.
    # @defreturn Element

    def parse(self, source, encoding='utf-8', parser=None):
        if not hasattr(source, "read"):
            source = codecs.open(source, "r", encoding)
        if not parser:
            parser = XMLTreeBuilder()
        while 1:
            data = source.read(32768)
            assert isinstance(data, unicode)
            if not data:
                break
            parser.feed(data)
        self._root = parser.close()
        return self._root

    ##
    # Creates a tree iterator for the root element.  The iterator loops
    # over all elements in this tree, in document order.
    #
    # @param tag What tags to look for (default is to return all elements)
    # @return An iterator.
    # @defreturn iterator

    def getiterator(self, tag=None):
        assert self._root is not None
        return self._root.getiterator(tag)

    ##
    # Finds the first toplevel element with given tag.
    # Same as getroot().find(path).
    #
    # @param path What element to look for.
    # @return The first matching element, or None if no element was found.
    # @defreturn Element or None

    def find(self, path):
        assert self._root is not None
        if path[:1] == u"/":
            path = u"." + path
        return self._root.find(path)

    ##
    # Finds the element text for the first toplevel element with given
    # tag.  Same as getroot().findtext(path).
    #
    # @param path What toplevel element to look for.
    # @param default What to return if the element was not found.
    # @return The text content of the first matching element, or the
    #     default value no element was found.  Note that if the element
    #     has is found, but has no text content, this method returns an
    #     empty string.
    # @defreturn string

    def findtext(self, path, default=None):
        assert self._root is not None
        if path[:1] == u"/":
            path = u"." + path
        return self._root.findtext(path, default)

    ##
    # Finds all toplevel elements with the given tag.
    # Same as getroot().findall(path).
    #
    # @param path What element to look for.
    # @return A list or iterator containing all matching elements,
    #    in document order.
    # @defreturn list of Element instances

    def findall(self, path):
        assert self._root is not None
        if path[:1] == u"/":
            path = u"." + path
        return self._root.findall(path)

    ##
    # Writes the element tree to a file, as XML.
    #
    # @param file A file name, or a file object opened for writing.
    # @param encoding Optional output encoding (default is US-ASCII).

    def write(self, file, encoding="utf-8"):
        assert self._root is not None

        if not hasattr(file, "write"):
            file = codecs.open(file, "w", encoding)

        if encoding not in 'utf8 utf-8 us-ascii'.split():
            file.write(u"<?xml version='1.0' encoding='%s'?>\n" % encoding)
        self._write(file, self._root, encoding, {})

    def _write(self, file, node, encoding, namespaces):
        # write XML to file
        tag = node.tag
        if tag is Comment:
            file.write(u"<!-- %s -->" % _escape_cdata(node.text))
        elif tag is ProcessingInstruction:
            file.write(u"<?%s?>" % _escape_cdata(node.text))
        else:
            items = node.items()
            xmlns_items = [] # new namespaces in this scope
            try:
                if isinstance(tag, QName) or tag[:1] == u"{":
                    tag, xmlns = fixtag(tag, namespaces)
                    if xmlns: xmlns_items.append(xmlns)
            except TypeError:
                _raise_serialization_error(tag)
            file.write(u"<" + tag)
            if items or xmlns_items:
                items.sort() # lexical order
                for k, v in items:
                    try:
                        if isinstance(k, QName) or k[:1] == u"{":
                            k, xmlns = fixtag(k, namespaces)
                            if xmlns: xmlns_items.append(xmlns)
                    except TypeError:
                        _raise_serialization_error(k)
                    try:
                        if isinstance(v, QName):
                            v, xmlns = fixtag(v, namespaces)
                            if xmlns: xmlns_items.append(xmlns)
                    except TypeError:
                        _raise_serialization_error(v)
                    file.write(u" %s=\"%s\"" % (k,
                                               _escape_attrib(v)))
                for k, v in xmlns_items:
                    file.write(u" %s=\"%s\"" % (k,
                                               _escape_attrib(v)))
            ### following line modified from original for Crunchy
            # by preventing divs from self-closing, we can display
            # sites such as www.python.org properly.
            if node.text != None or len(node) or tag==u'div':
                file.write(u">")
                if node.text:
                    file.write(_escape_cdata(node.text))
                for n in node:
                    self._write(file, n, encoding, namespaces)
                file.write(u"</" + tag + u">")
            else:
                file.write(u" />")
            for k, v in xmlns_items:
                del namespaces[v]
        if node.tail:
            file.write(_escape_cdata(node.tail))

# --------------------------------------------------------------------
# helpers

##
# Checks if an object appears to be a valid element object.
#
# @param An element instance.
# @return A true value if this is an element object.
# @defreturn flag

def iselement(element):
    # FIXME: not sure about this; might be a better idea to look
    # for tag/attrib/text attributes
    return isinstance(element, _ElementInterface) or hasattr(element, "tag")

##
# Checks if an object appears to be a valid list of element objects.
#
# @param An list (of elements) instance.
# @return A true value if this is a list of element objects, which
# includes the empty list.
# @defreturn flag

def iselements(elements):
    try:
        return all(iselement(e) for e in elements)
    except TypeError:
        return False

##
# Writes an element tree or element structure to sys.stdout.  This
# function should be used for debugging only.
# <p>
# The exact output format is implementation dependent.  In this
# version, it's written as an ordinary XML file.
#
# @param elem An element tree or an individual element.

def dump(elem):
    # debugging
    if not isinstance(elem, ElementTree):
        elem = ElementTree(elem)
    elem.write(sys.stdout)
    tail = elem.getroot().tail
    if not tail or tail[-1] != u"\n":
        sys.stdout.write(u"\n")

_escape = re.compile(ur'[&<>"\u0080-\uffff]+', re.U)

_escape_map = {
    u"&": u"&amp;",
    u"<": u"&lt;",
    u">": u"&gt;",
    u'"': u"&quot;",
}

_namespace_map = {
    # "well-known" namespace prefixes
    u"http://www.w3.org/XML/1998/namespace": u"xml",
    u"http://www.w3.org/1999/xhtml": u"html",
    u"http://www.w3.org/1999/02/22-rdf-syntax-ns#": u"rdf",
    u"http://schemas.xmlsoap.org/wsdl/": u"wsdl",
}

def _raise_serialization_error(text):
    raise TypeError(
        "cannot serialize %r (type %s)" % (text, type(text).__name__)
        )

def _escape(text, replacements):
    # escape attribute value

    if DEBUG and not isinstance(text, unicode):
        log.error('Not Unicode: %s' % text)
        # No point in a traceback, it's too late.
        text = text.decode('utf8')

    try:
        for replacement in replacements:
            oldstr, newstr = replacement.split()
            text = text.replace(oldstr, newstr)

        return text
    except (TypeError, AttributeError):
        _raise_serialization_error(text)

def _escape_cdata(text):
    return _escape(text, CDATA_REPLACEMENTS)

def _escape_attrib(text):
    return _escape(text, ATTRIB_REPLACEMENTS)

def fixtag(tag, namespaces):
    # given a decorated tag (of the form {uri}tag), return prefixed
    # tag and namespace declaration, if any
    if isinstance(tag, QName):
        tag = tag.text
    namespace_uri, tag = tag[1:].split(u"}", 1)
    prefix = namespaces.get(namespace_uri)
    if prefix is None:
        prefix = _namespace_map.get(namespace_uri)
        if prefix is None:
            prefix = u"ns%d" % len(namespaces)
        namespaces[namespace_uri] = prefix
        if prefix == u"xml":
            xmlns = None
        else:
            xmlns = (u"xmlns:%s" % prefix, namespace_uri)
    else:
        xmlns = None
    return u"%s:%s" % (prefix, tag), xmlns

##
# Parses an XML document into an element tree.
#
# @param source A filename or file object containing XML data.
# @param parser An optional parser instance.  If not given, the
#     standard {@link XMLTreeBuilder} parser is used.
# @return An ElementTree instance

def parse(source, parser=None):
    tree = ElementTree()
    tree.parse(source, parser)
    return tree

##
# Parses an XML document into an element tree incrementally, and reports
# what's going on to the user.
#
# @param source A filename or file object containing XML data.
# @param events A list of events to report back.  If omitted, only "end"
#     events are reported.
# @return A (event, elem) iterator.

class iterparse(object):

    def __init__(self, source, events=None):
        if not hasattr(source, "read"):
            source = codecs.open(source, "r", "utf-8")
        self._file = source
        self._events = []
        self._index = 0
        self.root = self._root = None
        self._parser = XMLTreeBuilder()
        # wire up the parser for event reporting
        parser = self._parser._parser
        append = self._events.append
        if events is None:
            events = ["end"]
        for event in events:
            if event == "start":
                try:
                    parser.ordered_attributes = 1
                    parser.specified_attributes = 1
                    def handler(tag, attrib_in, event=event, append=append,
                                start=self._parser._start_list):
                        append((event, start(tag, attrib_in)))
                    parser.StartElementHandler = handler
                except AttributeError:
                    def handler(tag, attrib_in, event=event, append=append,
                                start=self._parser._start):
                        append((event, start(tag, attrib_in)))
                    parser.StartElementHandler = handler
            elif event == "end":
                def handler(tag, event=event, append=append,
                            end=self._parser._end):
                    append((event, end(tag)))
                parser.EndElementHandler = handler
            elif event == "start-ns":
                def handler(prefix, uri, event=event, append=append):
                    try:
                        uri = uri.encode("utf-8")
                    except UnicodeError:
                        pass
                    append((event, (prefix or u"", uri)))
                parser.StartNamespaceDeclHandler = handler
            elif event == "end-ns":
                def handler(prefix, event=event, append=append):
                    append((event, None))
                parser.EndNamespaceDeclHandler = handler

    def next(self):
        while 1:
            try:
                item = self._events[self._index]
            except IndexError:
                if self._parser is None:
                    self.root = self._root
                    try:
                        raise StopIteration
                    except NameError:
                        raise IndexError
                # load event buffer
                del self._events[:]
                self._index = 0
                data = self._file.read(16384)
                if data:
                    self._parser.feed(data)
                else:
                    self._root = self._parser.close()
                    self._parser = None
            else:
                self._index = self._index + 1
                return item

    try:
        iter
        def __iter__(self):
            return self
    except NameError:
        def __getitem__(self, index):
            return self.next()

##
# Parses an XML document from a string constant.  This function can
# be used to embed "XML literals" in Python code.
#
# @param source A Unicode string containing XML data.
# @return An Element instance.
# @defreturn Element

def XML(text):
    assert isinstance(text, unicode)

    parser = XMLTreeBuilder()
    parser.feed(text)
    return parser.close()

##
# Parses an XML document from a string constant, and also returns
# a dictionary which maps from element id:s to elements.
#
# @param source A string containing XML data.
# @return A tuple containing an Element instance and a dictionary.
# @defreturn (Element, dictionary)

def XMLID(text):
    assert isinstance(text, unicode)

    parser = XMLTreeBuilder()
    parser.feed(text)
    tree = parser.close()
    ids = {}
    for elem in tree.getiterator():
        id = elem.get("id")
        if id:
            ids[id] = elem
    return tree, ids

##
# Parses an XML document from a string constant.  Same as {@link #XML}.
#
# @def fromstring(text)
# @param source A string containing XML data.
# @return An Element instance.
# @defreturn Element

fromstring = XML

##
# Generates a string representation of an XML element, including all
# subelements.
#
# @param element An Element instance.
# @return An encoded string containing the XML data.
# @defreturn Unicode string

def tostring(element, encoding='utf-8'):
    data = []

    class dummy(object):
        def write(self, text):
            data.append(text)

    ElementTree(element).write(dummy(), encoding)
    return u"".join(data)

##
# Generic element structure builder.  This builder converts a sequence
# of {@link #TreeBuilder.start}, {@link #TreeBuilder.data}, and {@link
# #TreeBuilder.end} method calls to a well-formed element structure.
# <p>
# You can use this class to build an element structure using a custom XML
# parser, or a parser for some other XML-like format.
#
# @param element_factory Optional element factory.  This factory
#    is called to create new Element instances, as necessary.

class TreeBuilder(object):

    def __init__(self, element_factory=None):
        self._data = [] # data collector
        self._elem = [] # element stack
        self._last = None # last element
        self._tail = None # true if we're after an end tag
        if element_factory is None:
            element_factory = _ElementInterface
        self._factory = element_factory

    ##
    # Flushes the parser buffers, and returns the toplevel documen
    # element.
    #
    # @return An Element instance.
    # @defreturn Element

    def close(self):
        assert len(self._elem) == 0, u"missing end tags"
        assert self._last != None, u"missing toplevel element"
        return self._last

    def _flush(self):
        ### following line modified from original for Crunchy so that it
        ## can display some non-compliant sites better
        if self._data != None:
        # original:
        #if self._data:
            if self._last is not None:
                text = u"".join(self._data)
                if self._tail:
                    assert self._last.tail is None, u"internal error (tail)"
                    self._last.tail = text
                else:
                    assert self._last.text is None, u"internal error (text)"
                    self._last.text = text
            self._data = []

    ##
    # Adds text to the current element.
    #
    # @param data A string.  This should be either an 8-bit string
    #    containing ASCII text, or a Unicode string.

    def data(self, data):
        self._data.append(data)

    ##
    # Opens a new element.
    #
    # @param tag The element name.
    # @param attrib A dictionary containing element attributes.
    # @return The opened element.
    # @defreturn Element

    def start(self, tag, attrs):
        self._flush()
        self._last = elem = self._factory(tag, attrs)
        if self._elem:
            self._elem[-1].append(elem)
        self._elem.append(elem)
        self._tail = 0
        return elem

    ##
    # Closes the current element.
    #
    # @param tag The element name.
    # @return The closed element.
    # @defreturn Element

    def end(self, tag):
        self._flush()
        self._last = self._elem.pop()
        assert self._last.tag == tag,\
               u"end tag mismatch (expected %s, got %s)" % (
                   self._last.tag, tag)
        self._tail = 1
        return self._last

##
# Element structure builder for XML source data, based on the
# <b>expat</b> parser.
#
# @keyparam target Target object.  If omitted, the builder uses an
#     instance of the standard {@link #TreeBuilder} class.
# @keyparam html Predefine HTML entities.  This flag is not supported
#     by the current implementation.
# @see #ElementTree
# @see #TreeBuilder

class XMLTreeBuilder(object):

    def __init__(self, html=0, target=None):
        try:
            from xml.parsers import expat
        except ImportError:
            raise ImportError(
                u"No module named expat; use SimpleXMLTreeBuilder instead"
                )
        self._parser = parser = expat.ParserCreate(None, u"}")
        if target is None:
            target = TreeBuilder()
        self._target = target
        self._names = {} # name memo cache
        # callbacks
        parser.DefaultHandlerExpand = self._default
        parser.StartElementHandler = self._start
        parser.EndElementHandler = self._end
        parser.CharacterDataHandler = self._data
        # let expat do the buffering, if supported
        try:
            self._parser.buffer_text = 1
        except AttributeError:
            pass
        # use new-style attribute handling, if supported
        try:
            self._parser.ordered_attributes = 1
            self._parser.specified_attributes = 1
            parser.StartElementHandler = self._start_list
        except AttributeError:
            pass
        encoding = None

        # xmlparser.returns_unicode is an attribute that disappeared
        # in Python 3. This is because pyexpat now always returns
        # Unicode in Python 3.
        #
        # http://hg.concordance-xmpp.org/genshi-py3/rev/bceb8d369dbe
        if sys.version_info[0] < 3 and not parser.returns_unicode:
            encoding = u"utf-8"
        # target.xml(encoding, None)
        self._doctype = None
        self.entity = {}

    def _fixname(self, key):
        # expand qname, and convert name string to ascii, if possible
        try:
            name = self._names[key]
        except KeyError:
            name = key
            if u"}" in name:
                name = u"{" + name
            self._names[key] = name = name
        return name

    def _start(self, tag, attrib_in):
        fixname = self._fixname
        tag = fixname(tag)
        attrib = {}
        for key, value in attrib_in.items():
            attrib[fixname(key)] = value
        return self._target.start(tag, attrib)

    def _start_list(self, tag, attrib_in):
        fixname = self._fixname
        tag = fixname(tag)
        attrib = {}
        if attrib_in:
            for i in range(0, len(attrib_in), 2):
                attrib[fixname(attrib_in[i])] = attrib_in[i+1]
        return self._target.start(tag, attrib)

    def _data(self, text):
        return self._target.data(text)

    def _end(self, tag):
        return self._target.end(self._fixname(tag))

    def _default(self, text):
        prefix = text[:1]
        if prefix == u"&":
            # deal with undefined entities
            try:
                self._target.data(self.entity[text[1:-1]])
            except KeyError:
                from xml.parsers import expat
                raise expat.error(
                    u"undefined entity %s: line %d, column %d" %
                    (text, self._parser.ErrorLineNumber,
                    self._parser.ErrorColumnNumber)
                    )
        elif prefix == u"<" and text[:9] == u"<!DOCTYPE":
            self._doctype = [] # inside a doctype declaration
        elif self._doctype is not None:
            # parse doctype contents
            if prefix == u">":
                self._doctype = None
                return
            text = text.strip()
            if not text:
                return
            self._doctype.append(text)
            n = len(self._doctype)
            if n > 2:
                type = self._doctype[1]
                if type == u"PUBLIC" and n == 4:
                    name, type, pubid, system = self._doctype
                elif type == u"SYSTEM" and n == 3:
                    name, type, system = self._doctype
                    pubid = None
                else:
                    return
                if pubid:
                    pubid = pubid[1:-1]
                self.doctype(name, pubid, system[1:-1])
                self._doctype = None

    ##
    # Handles a doctype declaration.
    #
    # @param name Doctype name.
    # @param pubid Public identifier.
    # @param system System identifier.

    def doctype(self, name, pubid, system):
        pass

    ##
    # Feeds data to the parser.
    #
    # @param data Encoded data.

    def feed(self, data):
        if sys.version_info[0] < 3:
            # xml.parsers.expat only takes bytestrings in Python 2.
            data = data.encode('utf8')
        self._parser.Parse(data, 0)

    ##
    # Finishes feeding data to the parser.
    #
    # @return An element structure.
    # @defreturn Element

    def close(self):
        self._parser.Parse("", 1) # end of data
        tree = self._target.close()
        del self._target, self._parser # get rid of circular references
        return tree