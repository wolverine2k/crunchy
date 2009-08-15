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

    >>> from src.interface import plugin, config, Element
    >>> plugin.clear()
    >>> config.clear()
    >>> def print_args(*args):
    ...     for arg in args:
    ...         print(arg)
    >>> plugin['add_vlam_option'] = print_args
    >>> from os import getcwd
    >>> config['crunchy_base_dir'] = getcwd()
    >>> import src.tests.mocks as mocks
    >>> mocks.init()
    >>> import os
    >>> import src.plugins.handle_remote as handle_remote

.. _`register()`:

Testing register()
----------------------

    >>> handle_remote.register()
    power_browser
    remote_html
    >>> mocks.registered_http_handler['/remote'] == handle_remote.remote_loader
    True
    >>> mocks.registered_tag_handler['span']['title']['load_remote'] == handle_remote.insert_load_remote
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

    >>> def open_html(dummy, url, remote, username):
    ...    global handle
    ...    return handle
    >>> plugin['create_vlam_page'] = open_html

Note that write() in python 3.0 returns an int instead of None with Python 2.x;
this interferes with unit tests unless we catch the return value.

    >>> __irrelevant = handle.write(file_content)
    >>> handle.close()
    >>> request = mocks.Request(args={'url':filepath})
    >>> request.crunchy_username = "Crunchy"

First, we do a test without the language-request on.

    >>> handle = open(filepath)
    >>> config["Crunchy"] = {}
    >>> config["Crunchy"]["forward_accept_language"] = False
    >>> handle_remote.remote_loader(request)
    >>> request.print_lines()
    200
    ('Cache-Control', 'no-cache, must-revalidate, no-store')
    End headers
    This is just a test.
    >>> handle.close()

Second, with the language-request on but "Accept-Language"
not in request.headers.

    >>> handle = open(filepath)
    >>> config["Crunchy"]["forward_accept_language"] = True
    >>> request = mocks.Request(args={'url':filepath})
    >>> handle_remote.remote_loader(request)
    >>> request.print_lines()
    200
    ('Cache-Control', 'no-cache, must-revalidate, no-store')
    End headers
    This is just a test.
    >>> handle.close()

Third, with "Accept-Language" in the headers.

    >>> request.headers["Accept-Language"] = 'junk'
    >>> handle = open(filepath)
    >>> config["Crunchy"]["forward_accept_language"] = True
    >>> request = mocks.Request(args={'url':filepath})
    >>> handle_remote.remote_loader(request)
    >>> request.print_lines()
    200
    ('Cache-Control', 'no-cache, must-revalidate, no-store')
    End headers
    This is just a test.
    >>> handle.close()

Finally, we remove the file to clean up.

    >>> os.remove(filepath)

Testing insert_load_remote()
------------------------------

This method inserts one form inside a <span> element.

    >>> fake_page = ''  # unused
    >>> fake_uid = '2'  # unused
    >>> span = Element("span")
    >>> span.text = "Cool url"
    >>> handle_remote.insert_load_remote(fake_page, span, fake_uid)
    >>> form = span.find(".//form")
    >>> form is not None
    True
    >>> print(form.attrib["name"])
    url
    >>> print(form.attrib["size"])
    80
    >>> print(form.attrib["method"])
    get
    >>> print(form.attrib["action"])
    /remote
    >>> inputs = list(form.findall("input"))
    >>> len(inputs)
    2
    >>> print(inputs[0].attrib["name"])
    url
    >>> print(inputs[0].attrib["size"])
    80
    >>> print(inputs[0].attrib["value"])
    Cool url
    >>> print(inputs[1].attrib["type"])
    submit
