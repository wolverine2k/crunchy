handle_local.py tests
================================

handle_remote.py is a plugin whose main purpose is to load remote tutorials,
i.e. those from some external website.  
It has the following functions that require testing:

1. `register()`_
2. `remote_loader()`_


Setting things up
--------------------

See how_to.rst_ for details.

.. _how_to.rst: how_to.rst

    >>> from src.interface import plugin, config
    >>> plugin.clear()
    >>> config.clear()
    >>> import src.plugins.handle_remote as handle_remote
    >>> import src.tests.mocks as mocks
    >>> mocks.init()
    >>> import os

.. _`register()`:

Testing register()
----------------------

    >>> handle_remote.register()
    >>> mocks.registered_http_handler['/remote'] == handle_remote.remote_loader
    True

.. _`remote_loader()`:

Testing remote_loader()
-------------------------

We need to test loading of html files only; note that remote_loader uses
FancyURLopener which can not deal with local files; we will need to use a trick
so as to help us run tests that do not depend on the availability 
of an Internet connection.

To make the test totally self-contained, we will create the required file
as we run the test, and delete it afterwards.


First we create a the test file.

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

Next, we define a dummy vlam page creator.

    >>> def open_html(dummy, url, remote):
    ...    global handle
    ...    return handle
    >>> plugin['create_vlam_page'] = open_html

Note that write() in python 3.0 returns an int instead of None with Python 2.x;
this interferes with unit tests unless we catch the return value.

    >>> __irrelevant = handle.write(file_content)
    >>> handle.close()
    >>> request = mocks.Request(args={'url':filepath})

First, we do a test without the language-request on.

    >>> handle = open(filepath)
    >>> config["forward_accept_language"] = False
    >>> handle_remote.remote_loader(request)
    200
    End headers
    This is just a test.
    >>> handle.close()

Second, with the language-request on but "Accept-Language" 
not in request.headers.

    >>> handle = open(filepath)
    >>> config["forward_accept_language"] = True
    >>> handle_remote.remote_loader(request)
    200
    End headers
    This is just a test.
    >>> handle.close()

Third, with "Accept-Language" in the headers.

    >>> request.headers["Accept-Language"] = 'junk'
    >>> handle = open(filepath)
    >>> config["forward_accept_language"] = True
    >>> handle_remote.remote_loader(request)
    200
    End headers
    This is just a test.
    >>> handle.close()

Finally, we remove the file to clean up.

    >>> os.remove(filepath)

