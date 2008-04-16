'''This file contains functional tests for Crunchy.

See note at the bottom of the file for successful execution.
'''

import unittest
import time

# Third party modules
from selenium import selenium

# Suggestion on writing tests

# 1. Avoid using id's to locate elements; most of these are automatically
#    assigned by Crunchy and their value may change as more tests are added.
#    Use fully qualified xpath instead.

# 2. Ensure that enough processing time is given for the browser/Crunchy
#    to produce the appropriate output - otherwise a test may fail.

# 3. Note that it has been observed that some unexpected failing tests occur
#    when the server has been running for too long.

def click_link_and_wait(clickable):
    '''clicks on a series of link, waiting for an appropriate time for a
       page to load before continuing.'''
    for elem in clickable:
        selenium_server.click(elem)
        selenium_server.wait_for_page_to_load(5000)


class InterpreterTest(unittest.TestCase):
    '''Ensures that code is run through various interpreter and verifies the
    output meet some expectations.
    '''
    def test_interpreters(self):
        '''Compares the output of the interpreters, after execution, with
        what is expected'''
        self.verificationErrors = []
        # go to relevant page and store some initial values
        click_link_and_wait(["//img[@alt='Home']", "link=Tests",
                             "link=Interpreter"])

        # Store some information about text initially on the page.
        all_text = selenium_server.get_body_text()
        forty_twos = all_text.count("42")
        fifty_six = all_text.count("56")
        range_5 = all_text.count("[0, 1, 2, 3, 4]")
        name_errors = all_text.count("NameError")
        system_exits = all_text.count("SystemExit")

        # first interpreter; execute the code and give time for Crunchy
        # to process it
        editor_link = "xpath=//div[3]/span[2]/a"
        execute_button = "xpath=//div[3]/button"
        selenium_server.click(editor_link)
        selenium_server.click(execute_button)
        time.sleep(0.1)
        all_text = selenium_server.get_body_text()
        # update to expected values and compare
        forty_twos += 3
        range_5 += 1
        self.assertTrue(all_text.count("[0, 1, 2, 3, 4]") == range_5)
        self.assertTrue(all_text.count("42") == forty_twos)

        # second interpreter
        editor_link = "xpath=//div[4]/span[2]/a"
        execute_button = "xpath=//div[4]/button"
        selenium_server.click(editor_link)
        selenium_server.click(execute_button)
        time.sleep(0.1)
        all_text = selenium_server.get_body_text()
        # update to expected values and compare
        forty_twos += 1
        name_errors += 1
        system_exits += 1
        self.assertTrue(all_text.count("42") == forty_twos)
        self.assertTrue(all_text.count("NameError") == name_errors)
        self.assertTrue(all_text.count("SystemExit") == system_exits)

        # third interpreter
        editor_link = "xpath=//div[5]/span[2]/a"
        execute_button = "xpath=//div[5]/button"
        selenium_server.click(editor_link)
        selenium_server.click(execute_button)
        time.sleep(0.1)
        all_text = selenium_server.get_body_text()
        forty_twos += 1
        self.assertTrue(all_text.count("42") == forty_twos)

        # fourth interpreter
        editor_link = "xpath=//div[6]/span[2]/a"
        execute_button = "xpath=//div[6]/button"
        selenium_server.click(editor_link)
        selenium_server.click(execute_button)
        time.sleep(0.1)
        all_text = selenium_server.get_body_text()
        name_errors += 1
        self.assertTrue(all_text.count("NameError") == name_errors)

        # fifth interpreter
        editor_link = "xpath=//div[7]/span[2]/a"
        execute_button = "xpath=//div[7]/button"
        selenium_server.click(editor_link)
        selenium_server.click(execute_button)
        time.sleep(0.1)
        all_text = selenium_server.get_body_text()
        name_errors += 1
        self.assertTrue(all_text.count("NameError") == name_errors)

        # sixth interpreter
        editor_link = "xpath=//div[8]/span[2]/a"
        execute_button = "xpath=//div[8]/button"
        selenium_server.click(editor_link)
        selenium_server.click(execute_button)
        time.sleep(0.1)
        all_text = selenium_server.get_body_text()
        fifty_six += 1
        self.assertTrue(all_text.count("56") == fifty_six)

        # seventh interpreter
        editor_link = "xpath=//div[9]/span[2]/a"
        execute_button = "xpath=//div[9]/button"
        selenium_server.click(editor_link)
        selenium_server.click(execute_button)
        time.sleep(0.1)
        all_text = selenium_server.get_body_text()
        forty_twos += 1
        fifty_six += 1
        self.assertTrue(all_text.count("42") == forty_twos)
        self.assertTrue(all_text.count("56") == fifty_six)

        self.assertEqual([], self.verificationErrors)


class LeftMenuLinkTest(unittest.TestCase):
    '''
    This tests all the links (excluding the tests menu) on the left
    hand side of the index page, coming back to the index page each time.

    It is just there to make sure that all the pages in the Crunchy tutorial
    are found.
    '''
    def test_links(self):
        self.verificationErrors = []
        click_link_and_wait([
            "//img[@alt='Home']", "link=Begin tutorial",
            "//img[@alt='Home']", "link=Interpreter",
            "//img[@alt='Home']", "link=Editor",
            "//img[@alt='Home']", "link=DocTest",
            "//img[@alt='Home']", "link=Graphics",
            "//img[@alt='Home']", "link=Image files",
            "//img[@alt='Home']", "link=External applications",
            "//img[@alt='Home']", "link=Browsing",
            "//img[@alt='Home']", "link=Configuring Crunchy",
            "//img[@alt='Home']", "link=FAQ, bugs, etc.",
            "//img[@alt='Home']", "link=Writing tutorials",
            "//img[@alt='Home']"])
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
