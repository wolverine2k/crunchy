# encoding: utf-8
"""
widget.py

Created by Johannes Woolard on 2008-04-06.

Unittests for the widget class
"""

import unittest

from System.Windows.Browser.HtmlPage import Document

from widgets import Widget

class widget_tests(unittest.TestCase):
    def setUp(self):
        self.test_elem = Document.CreateElement("div")
        self.test_elem.Id = "___test_elem___"
        Document.Body.AppendChild(self.test_elem)
    def tearDown(self):
        Document.Body.RemoveChild(self.test_elem)

class widget_api(widget_tests):
    """
    Tests for the widget API
    """
    def test_document_attrib_present(self):
        "Test if the Document attribute is present"
        widget = Widget(self.test_elem)
        self.assert_(hasattr(widget, "Document"))
        widget.remove()

class interpreter(widget_tests):
    def test_insertion_and_removal(self):
        """Test that the widget was correctly inserted and removed"""
        self.fail("This test is not yet implemented")
    def test_simple_execution(self):
        """Test that the simple statement print "Hello World" is executed properly"""
        self.fail("This test is not yet implemented")
    def test_complex_execution(self):
        """Test that we can define and then execute a function"""
        self.fail("This test is not yet implemented")

def get_suite():
    suite = unittest.TestSuite()
    suite.addTest(widget_api('test_document_attrib_present'))
    suite.addTest(interpreter('test_insertion_and_removal'))
    suite.addTest(interpreter('test_complex_execution'))
    suite.addTest(interpreter('test_simple_execution'))
    return suite
