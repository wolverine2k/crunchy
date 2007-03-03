"""Test plugins for the new demo plugin infrastructure
"""
from CrunchyPlugin import CrunchyPlugin

class TestPlugin(CrunchyPlugin):
    def register(self):
        print "TestPlugin registering..."

class SecondTestPlugin(CrunchyPlugin):
    def register(self):
        print "SecondTestPlugin registering..."