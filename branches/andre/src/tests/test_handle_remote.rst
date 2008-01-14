handle_local.py tests
================================

Tested successfully with Python 2.4, 2.5, 3.0a1 and 3.0a2

handle_remote.py is a plugin whose main purpose is to load remote tutorials,
i.e. those from some external website.  
It has the following functions that require testing:

1. register(): registers a handler.
2. remote_loader(): loads a file following a request, and sends it to the browser


0. Setting things up
--------------------

See how_to.rst_ for details.

.. _how_to.rst: how_to.rst

    >>> from src.interface import plugin, python_version
    >>> plugin.clear()
    >>> import src.plugins.handle_remote as handle_remote
    >>> import src.tests.mocks as mocks
    >>> mocks.init()
    >>> import os


1. Testing register()
----------------------

    >>> handle_remote.register()
    >>> mocks.registered_http_handler['/remote'] == handle_remote.remote_loader
    True


2. Testing remote_loader()
-------------------------

We need to test loading of html files only; note that remote_loader uses
urllib.urlopen which can deal with local files - we will use this fact
to help us run tests that do not depend on the availability 
of an Internet connection.
To make the test totally self-contained, we will create the required file
as we run the test, and delete it afterwards.

First, we define a dummy vlam page creator.

    >>> def open_html(file_handle, url, remote):
    ...    return file_handle
    >>> plugin['create_vlam_page'] = open_html

Nexgt we create the test file per se.

    >>> file_content = "This is just a test."
    >>> filename = "test_file0.html"
    >>> filepath = os.path.join(os.getcwd(), filename)
    >>> index = 0
    >>> # create non-existing file
    >>> while os.path.exists(filepath):
    ...    orig = "%d.txt"%index
    ...    index += 1
    ...    repl = "%d.txt"%index
    ...    filepath.replace(orig, repl)
    >>> handle = open(filepath, 'w')

Note that write() in python 3.0 returns an int instead of None with Python 2.x;
this interferes with unit tests unless we catch the return value.

    >>> __irrelevant = handle.write(file_content)
    >>> handle.close()
    >>> request = mocks.Request(args={'url':filepath})
    >>> handle_remote.remote_loader(request)
    200
    End headers
    This is just a test.
    >>> os.remove(filepath)

