'''This file contains functional tests for Crunchy; using Selenium.
'''
from optparse import OptionParser
import sys
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

SHORT_WAIT = 0.1

def go_home():
    '''Loads the Crunchy home page
       (and waits until it has loaded before returning).'''
    selenium_server.open("/")

def click_link_and_wait(clickable):
    '''clicks on a series of link, waiting for an appropriate time for a
       page to load before continuing.'''
    for elem in clickable:
        selenium_server.click(elem)
        selenium_server.wait_for_page_to_load(5000)

def common_tear_down(self):
    '''All tests end with resuming at the start page and determine if any
    test has failed.'''
    selenium_server.open('/')
    selenium_server.wait_for_page_to_load(5000)
    self.assertEqual([], self.verificationErrors)

class DoctestTest(unittest.TestCase):
    '''Ensures that various code samples run to satisfy (or not) a given
    doctest are executed and the result is compared with the
    expected output.
    '''
    def test_doctest(self):
        '''Compares the output of the doctest, after execution, with
        what is expected'''
        self.verificationErrors = []
        # go to relevant page and store some initial values
        go_home()
        click_link_and_wait(["link=Miscellaneous",  # the main tests page
                             "link=Doctest" # the doctests page
                             ])

        # first run; execute the doctest with no user code
        selenium_server.click("xpath=//div[2]/button") # execute button
        time.sleep(SHORT_WAIT)
        all_text = selenium_server.get_body_text()
        self.assertTrue(all_text.count("NameError") == 4)

        # second run; a different failing test
        selenium_server.type("xpath=//div[2]/textarea",
                             "class Animal(object):\n    pass")
        selenium_server.click("xpath=//div[2]/button") # execute button
        time.sleep(SHORT_WAIT)
        all_text = selenium_server.get_body_text()
        self.assertTrue(all_text.count("NameError") == 3)
        self.assertTrue(all_text.count("TypeError") == 1)

        # Third run: success; make sure we set language to English to compare
        selenium_server.type("xpath=//div[2]/textarea",
                             "crunchy.language='en'\n" +
                             "class Animal(object):\n" +
                             "   def __init__(self, name):\n" +
                             "       self.name = name\n" +
                             "       self.friends = []\n" +
                             "   def addFriend(self, friend):\n" +
                             "       self.friends.append(friend)\n")
        selenium_server.click("xpath=//div[2]/button") # execute button
        time.sleep(SHORT_WAIT)
        all_text = selenium_server.get_body_text()
        self.assertTrue(all_text.count("Congratulations") == 1)

    def tearDown(self):
        '''final verification'''
        common_tear_down(self)


class InterpreterTest(unittest.TestCase):
    '''Ensures that code is run through various interpreter and verifies the
    output meet some expectations.
    '''
    def test_interpreters(self):
        '''Compares the output of the interpreters, after execution, with
        what is expected'''
        self.verificationErrors = []
        # go to relevant page and store some initial values
        go_home()
        click_link_and_wait(["link=Miscellaneous",
                             "link=Interpreter test"])

        # Store some information about text initially on the page.
        all_text = selenium_server.get_body_text()
        forty_twos = all_text.count("42")
        fifty_six = all_text.count("56")
        range_5 = all_text.count("[0, 1, 2, 3, 4]")
        name_errors = all_text.count("NameError")
        system_exits = all_text.count("SystemExit")
        # first interpreter; execute the code and give time for Crunchy
        # to process it
        selenium_server.click("xpath=//div[2]/div[2]/span[2]/a") # editor link
        selenium_server.click("xpath=//div[2]/div[2]/button") # execute button
        time.sleep(SHORT_WAIT)
        all_text = selenium_server.get_body_text()
        # update to expected values and compare
        forty_twos += 3
        range_5 += 1
        self.assertTrue(all_text.count("[0, 1, 2, 3, 4]") == range_5)
        self.assertTrue(all_text.count("42") == forty_twos)

        # second interpreter
        selenium_server.click("xpath=//div[3]/div[2]/span[2]/a") # editor link
        selenium_server.click("xpath=//div[3]/div[2]/button") # execute button
        time.sleep(SHORT_WAIT)
        all_text = selenium_server.get_body_text()
        # update to expected values and compare
        forty_twos += 1
        name_errors += 1
        system_exits += 1
        self.assertTrue(all_text.count("42") == forty_twos)
        self.assertTrue(all_text.count("NameError") == name_errors)
        self.assertTrue(all_text.count("SystemExit") == system_exits)

        # third interpreter
        selenium_server.click("xpath=//div[4]/div[2]/span[2]/a") # editor link
        selenium_server.click("xpath=//div[4]/div[2]/button") # execute button
        time.sleep(SHORT_WAIT)
        all_text = selenium_server.get_body_text()
        forty_twos += 1
        self.assertTrue(all_text.count("42") == forty_twos)

        # fourth interpreter
        selenium_server.click("xpath=//div[5]/div[2]/span[2]/a") # editor link
        selenium_server.click("xpath=//div[5]/div[2]/button") # execute button
        time.sleep(SHORT_WAIT)
        all_text = selenium_server.get_body_text()
        name_errors += 1
        self.assertTrue(all_text.count("NameError") == name_errors)

        # fifth interpreter
        selenium_server.click("xpath=//div[6]/div[2]/span[2]/a") # editor link
        selenium_server.click("xpath=//div[6]/div[2]/button") # execute button
        time.sleep(SHORT_WAIT)
        all_text = selenium_server.get_body_text()
        name_errors += 1
        self.assertTrue(all_text.count("NameError") == name_errors)

        # sixth interpreter
        selenium_server.click("xpath=//div[7]/div[2]/span[2]/a") # editor link
        selenium_server.click("xpath=//div[7]/div[2]/button") # execute button
        time.sleep(SHORT_WAIT)
        all_text = selenium_server.get_body_text()
        fifty_six += 1
        self.assertTrue(all_text.count("56") == fifty_six)

        # seventh interpreter
        selenium_server.click("xpath=//div[8]/div[2]/span[2]/a") # editor link
        selenium_server.click("xpath=//div[8]/div[2]/button") # execute button
        time.sleep(SHORT_WAIT)
        all_text = selenium_server.get_body_text()
        forty_twos += 1
        fifty_six += 1
        self.assertTrue(all_text.count("42") == forty_twos)
        self.assertTrue(all_text.count("56") == fifty_six)

    def tearDown(self):
        '''final verification'''
        common_tear_down(self)


class LeftMenuLinkTest(unittest.TestCase):
    '''
    This tests all the links (excluding the tests menu) on the left
    hand side of the index page, coming back to the index page each time.

    It is just there to make sure that all the pages in the Crunchy tutorial
    are found.
    '''
    def test_links(self):
        '''tests all the links on the left hand side of the index page,
        coming back to that page each time.'''
        self.verificationErrors = []
        go_home()
        click_link_and_wait(["link=Begin Tutorial"])
        go_home()
        click_link_and_wait(["link=Interpreter"])
        go_home()
        click_link_and_wait(["link=Editor"])
        go_home()
        click_link_and_wait(["link=DocTest"])
        go_home()
        click_link_and_wait(["link=Graphics"])
        go_home()
        click_link_and_wait(["link=Images and dhtml"])
        go_home()
        click_link_and_wait(["link=External applications"])
        go_home()
        click_link_and_wait(["link=Browsing"])
        go_home()
        click_link_and_wait(["link=Configuring Crunchy"])
        go_home()
        click_link_and_wait(["link=FAQ, bugs, etc."])
        go_home()
        click_link_and_wait(["link=Writing tutorials"])

    def tearDown(self):
        '''final verification'''
        common_tear_down(self)



def parse_options():
    '''parse command line options'''
    parser = OptionParser(usage)
    parser.add_option("--port", action="store", type="int", dest="port",
            help="Specifies the port number served by Crunchy (default is 8001) ")
    parser.add_option("--browser", action="store", type="string", dest="browser",
            help="Not implemented: will be->Firefox=chrome (default); Safari=safari")

    (options, dummy) = parser.parse_args()

    port = 8001
    if options.port:
        port = options.port
        # see comment about unittest.main() below
        sys.argv.remove('--port=%s'%port)
    browser = "chrome"
    if options.browser:  # safari raises an error currently on my Mac...
        browser = options.browser
        # see comment about unittest.main() below
        sys.argv.remove('--browser=%s'%browser)
    return browser, port

usage = '''python functional_test.py [--port=XXXX]
Functional testing using Selenium.
Make sure Selenium server is running via:
    java -jar selenium-server.jar
and that Crunchy has been started via
    python crunchy.py --automated.
By default, it is assumed that Crunchy is serving at port 8001.
'''

if __name__ == "__main__":
    dummy_browser, port = parse_options()
    base_url = "http://127.0.0.1:%s/" % port
    selenium_server = selenium("localhost", 4444, "*firefox", base_url)
    selenium_server.start()
    selenium_server.open('/index.html')
    selenium_server.wait_for_page_to_load(5000)
    # unittest.main extract arguments from the command line; it would not
    # recognize the arguments passed to functional_test.py. This is why
    # we remove them above.
    unittest.main()
    selenium_server.stop()
