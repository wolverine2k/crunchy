'''This file contains functional tests for Crunchy.

See note at the bottom of the file for successful execution.
'''

import unittest

# Third party modules
from selenium import selenium

class InterpreterTest(unittest.TestCase):
    def setUp(self):
        self.verificationErrors = []

    def test_new(self):
        sel = selenium_server
        sel.click("//img[@alt='Home']")
        sel.wait_for_page_to_load(5000)
        sel.click("link=Tests")
        sel.wait_for_page_to_load(5000)
        sel.click("link=Interpreter")
        sel.wait_for_page_to_load(5000)
        sel.key_press('xpath=//div[3]/span[2]/input', '42')

    def tearDown(self):
        self.assertEqual([], self.verificationErrors)


class LeftMenuLinkTest(unittest.TestCase):
    '''
    This tests all the links (excluding the tests menu) on the left
    hand side of the index page, coming back to the index page each time.

    It is just there to make sure that all the pages in the Crunchy tutorial
    are found.
    '''
    def setUp(self):
        self.verificationErrors = []

    def test_new(self):
        sel = selenium_server
        sel.click("//img[@alt='Home']")
        sel.wait_for_page_to_load(5000)
        sel.click("link=Begin tutorial")
        sel.wait_for_page_to_load(5000)
        sel.click("//img[@alt='Home']")
        sel.wait_for_page_to_load(5000)
        sel.click("link=Interpreter")
        sel.wait_for_page_to_load(5000)
        sel.click("//img[@alt='Home']")
        sel.wait_for_page_to_load(5000)
        sel.click("link=Editor")
        sel.wait_for_page_to_load(5000)
        sel.click("//img[@alt='Home']")
        sel.wait_for_page_to_load(5000)
        sel.click("link=DocTest")
        sel.wait_for_page_to_load(5000)
        sel.click("//img[@alt='Home']")
        sel.wait_for_page_to_load(5000)
        sel.click("link=Graphics")
        sel.wait_for_page_to_load(5000)
        sel.click("//img[@alt='Home']")
        sel.wait_for_page_to_load(5000)
        sel.click("link=Image files")
        sel.wait_for_page_to_load(5000)
        sel.click("//img[@alt='Home']")
        sel.wait_for_page_to_load(5000)
        sel.click("link=External applications")
        sel.wait_for_page_to_load(5000)
        sel.click("//img[@alt='Home']")
        sel.wait_for_page_to_load(5000)
        sel.click("link=Browsing")
        sel.wait_for_page_to_load(5000)
        sel.click("//img[@alt='Home']")
        sel.wait_for_page_to_load(5000)
        sel.click("link=Configuring Crunchy")
        sel.wait_for_page_to_load(5000)
        sel.click("//img[@alt='Home']")
        sel.wait_for_page_to_load(5000)
        sel.click("link=FAQ, bugs, etc.")
        sel.wait_for_page_to_load(5000)
        sel.click("//img[@alt='Home']")
        sel.wait_for_page_to_load(5000)
        sel.click("link=Writing tutorials")
        sel.wait_for_page_to_load(5000)
        sel.click("//img[@alt='Home']")

    def tearDown(self):
        self.assertEqual([], self.verificationErrors)

if __name__ == "__main__":
    print "functional testing using nose and selenium"
    print "make sure selenium server is running via"
    print "java -jar selenium-server.jar"
    print "start Crunchy via: python crunchy.py --automated=True"
    print "Note: it is assumed that we have one running Crunchy instance at port 8001"
    print "==============================\n"
    base_url = "http://127.0.0.1:8001/"
    selenium_server = selenium("localhost", 4444, "*chrome", base_url)
    selenium_server.start()
    selenium_server.open('/')
    unittest.main()
    selenium_server.stop()
