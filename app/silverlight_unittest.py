# encoding: utf-8
"""
silverlight_unittest.py

Created by Johannes Woolard on 2008-04-06.

Here is a way of running unittests in silverlight apps.

"""

import unittest

def run(suite):
    """
    You can set up your test cases just as you always would.
    """
    container = Document.CreateElement("div")
    container.SetStyleAttribute("border", "1px solid black")
    
    result = unittest.TestResult()
    startTime = time.time()
    suite.run(result)
    stopTime = time.time()
    timeTaken = stopTime - startTime
    
    if result.wasSuccesful():
        container.innerHTML = """
        <h2 style="background-color: green;">Test Succesful</h2>
        <p>All %s tests passed in %s!</p>
        """ % (result.testsRun, timeTaken)
    else:
        container.innerHTML = """
        <h2 style="background-color: red;">Test Failed</h2>
        """
        if len(result.errors) > 0:
            container.innerHTML += "<p>%s errors occurred.</p>" % len(result.errors)
        if len(result.failures) > 0:
            container.innerHTML += "<p>%s tests failed.</p>" % len(result.failures)
        container.innerHTML += """
        <h3 style="background-color:red">Errors:</h3>
        """


