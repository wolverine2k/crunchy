Guide for writing tests
=======================

To test Crunchy, we use two kinds of tests:

  1. doctest-based unit tests
  2. Functional tests

Most functional tests are html pages that contains vlam instructing Crunchy
as to how to modify a page and display it appropriately.  They are tested
by having Crunchy load them and require a user to verify that the display
is as expected.  They are not the subject of this document.

Doctest-based unit tests are rst files (rst = ReStructuredText) which are
meant to be imported and run by Python, independently of Crunchy. 
This document describes the conventions and tools used to create such
test files.  For the rest of this document, when we refer to "tests" or
"test files" we mean "doctest-based unit tests" or files containing these.

1. Convention and running tests
-------------------------------

By convention, all tests files begin with "test", followed by an underscore "_",
followed by the name of the module they are testing, but with "rst" as an extension.
They are located in the directory src/tests/ relative to the main Crunchy directory.
For example, the test file for the module "comet.py" is called "test_comet.rst".

These tests can be run via

- python all_tests.py, if using a Python version less than 3.0
- python all_tests_py3k.py, if using a Python version 3.x


In the above, we assume that "python" 
is the name of the command used to call the appropriate Python version.
Using the above will run all test files found in the tests directory.

2. Standard content of a test file
----------------------------------

Usually, a test file should contain 3 or more parts:

   a. an introduction, briefly describing the purpose of the module that
      is being tested; this can often be extracted from the docstring of
      that module.  This introduction should also contain a list of functions
      or methods that need to be tested.
   b. A section used for setting tests up.  In this section, the required modules
      are imported, and most mock values and functions are defined.  We will give
      a fake example below, with explanation.
   c. Each function/method tested should be in a separate section.


In order to facilitate writing test files, a number of modules have
been written to provide "hooks" into various required functions, rather
than using hard-coded import statements.  When Crunchy is run normally,
these "hooks" are initialized via other Crunchy modules.  When running
tests, a user needs to initialized the "hooks" explicitly, usually with
mock functions or values.

There are two main modules used for "hooks": interface.py and mocks.py.
interface.py contains various "hooks" (Python dicts) which can be initialized
as required.  mocks.py contains simplified version of standard objects used
by Crunchy such as "vlam pages", "http requests", etc.

Setting a test up is usually done with something like the following:

First, we import the required objects from interface.py

    >>> from src.interface import plugin # or other like config, Element, etc.

Next, we make sure that any dict imported does not contain left-over values
from a previous test.

    >>> plugin.clear() # do the same for config if present

Then, we define any required value by the module to be tested.

    >>> plugin['magic_number'] = 42

We then import the module to be tested

    >>> import src.plugins.amazing_module as amazing_module

Next, we import mock.py; note that it
could have been imported by a previous test that was run in a single
doctest session.
In that case, importing it again would only provide a link
to the module; by clearing the above directory, we will have removed some
important definitions.  To correct this, we need to call the init() function
from that module

    >>> import src.tests.mocks as mocks
    >>> mocks.init()

Note that, with Python 2.x, we could have used reload(mocks) instead - but
this is no longer an option with Python 3.x.

Finally, we can define some fake functions that can be used.  This could
have been done when we defined required values above, but it is usually
clearer to do it separately, with some additional explanation.  For example
suppose we need to test some function which depend on the security level
attributed to a given url.  We can do this by creating a number of fake
urls, a function to retrieve the security level of these urls, and a link
to the required "hook".

    >>> site_security = {'trusted_url': 'trusted',
    ...                  'display_only_url': 'display normal'}
    >>> def get_security_level(url):
    ...     return site_security[url]
    >>> config['page_security_level'] = get_security_level

Note that "config" in the example above would have been imported from
interface.py.

After doing all of the above, we are ready to actually start testing
the various functions.  To see how this is done, we refer you to actual
test examples.