# encoding: utf-8
"""
__init__.py

Created by Johannes Woolard on 2008-04-06.

imports all the tests, please add your test modules here as you write them
"""

import unittest

__all__ = ['suite']

suite = unittest.TestSuite()

import Widget_test
suite.addTest(Widget_test.get_suite())
