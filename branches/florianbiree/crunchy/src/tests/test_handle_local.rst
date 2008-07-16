handle_local.py tests
================================

handle_local.py is a plugin whose main purpose is to load local tutorials.  
It has the following functions that require testing:

#. `register()`_
#. `local_loader()`_
#. `add_to_path()`_

Setting things up
--------------------

See how_to.rst_ for details.

.. _how_to.rst: how_to.rst

    >>> from src.interface import plugin, config, Element
    >>> plugin.clear()
    >>> config.clear()
    >>> import src.plugins.handle_local as handle_local
    >>> import src.tests.mocks as mocks
    >>> mocks.init()
    >>> import os
    >>> current_dir = os.getcwd()

.. _`register()`:

Testing register()
----------------------

    >>> handle_local.register()
    >>> 
    >>> mocks.registered_tag_handler['meta']['title']['python_import'] == handle_local.add_to_path
    True
    >>> mocks.registered_http_handler['/local'] == handle_local.local_loader
    True

.. _`local_loader()`:

Testing local_loader()
-------------------------

We need to test loading of both html and other types of files.  To make the test
totally self-contained, we will create the required files as we run the test, and
delete them afterwards.


    >>> file_content = "This is just a test."
    >>> filename = "test_file0.txt"
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
    >>> handle_local.local_loader(request)
    200
    Cache-Controlno-cache, must-revalidate, no-store
    End headers
    This is just a test.
    >>> os.remove(filepath)

Now, let's repeat, but this time with an html file - as determined by
the file extension - not the actual content.  Note that we need to
determine if the path gets added properly.  
First, we define a dummy vlam page creator.

    >>> def open_html(file_handle, url, local):
    ...    print(file_handle.read())
    ...    file_handle.seek(0)  # "rewind"
    ...    print(url[-4:]) # just the extension
    ...    print(local)
    ...    return file_handle
    >>> plugin['create_vlam_page'] = open_html

Next, we need to make sure the path we wish to add is not there,
so we can be sure it's been added correctly.
    
    >>> import sys
    >>> cwd = os.getcwd()
    >>> while cwd in sys.path:
    ...    sys.path.remove(cwd)

We are now ready for the test as such.

    >>> file_content = "This is just a test."
    >>> filename = "test_file0.htm"
    >>> filepath = os.path.join(os.getcwd(), filename)
    >>> index = 0
    >>> # create non-existing file
    >>> while os.path.exists(filepath):
    ...    orig = "%d.txt"%index
    ...    index += 1
    ...    repl = "%d.txt"%index
    ...    filepath.replace(orig, repl)
    >>> handle = open(filepath, 'w')
    >>> __irrelevant = handle.write(file_content)
    >>> handle.close()
    >>> request = mocks.Request(args={'url':filepath})
    >>> handle_local.local_loader(request)
    This is just a test.
    .htm
    True
    200
    Cache-Controlno-cache, must-revalidate, no-store
    End headers
    This is just a test.
    >>> os.remove(filepath)
    >>> cwd in sys.path
    True
    >>> sys.path.remove(cwd)  # cleaning up

.. _`add_to_path()`:

Testing add_to_path()
------------------------

Make sure that test path not in sys.path; remove if needed
add path and see if it is in there.

    >>> fake_path = "fake_path_which_does_not_exist"
    >>> # just in case we are wrong...
    >>> while fake_path in sys.path:
    ...    sys.path.remove(fake_path)
    >>> elem = Element("dummy")
    >>> elem.attrib['name'] = fake_path
    >>> page = mocks.Page()
    >>> handle_local.add_to_path(page, elem, 'dummy')
    >>> fake_path in sys.path
    True
    >>> sys.path.remove(fake_path)  # cleaning up


