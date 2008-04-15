'''
This file tests all the links (excluding the tests menu) on the left
hand side of the index page, coming back to the index page each time.

It is just there to make sure that all the pages in the Crunchy tutorial
are found.
'''
from selenium import selenium
import unittest

class LeftMenuLinkTest(unittest.TestCase):
    def setUp(self):
        self.verificationErrors = []
        self.selenium = selenium("localhost", 4444, "*chrome", "http://127.0.0.1:8888/")
        self.selenium.start()

    def test_new(self):
        sel = self.selenium
        sel.open("http://127.0.0.1:8888/")
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
        #self.selenium.stop()
        self.assertEqual([], self.verificationErrors)

if __name__ == "__main__":
    unittest.main()
