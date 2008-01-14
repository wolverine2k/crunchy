io_widget.py tests
================================

Not yet Tested successfully with Python 2.4, 2.5, 3.0a1 and 3.0a2

io_widget.py is a plugin which handles text and graphical IO
It has the following functions that require testing:

1. register(): registers a service available to other plugins.
2. insert_io_subwidget(): insert an output widget into elem, usable for editors
    interpreters and  includes a canvas


0. Setting things up
--------------------

We need to import various modules before starting, and make sure that
they do not contain values initialized by other tests.  Note that
io_widget imports editarea.py which requires config['editarea_language'];
it also requires itself a value for plugin['session_random_id].

    >>> from src.interface import plugin, config, Element
    >>> plugin.clear()
    >>> plugin['session_random_id'] = 42
    >>> config.clear()
    >>> config['editarea_language'] = 'en'
    >>> import src.plugins.io_widget as io_widget
    >>> import src.tests.mocks as mocks
    >>> dummy = reload(mocks)

We also need to define some mock functions and values.

    >>> site_security = {'trusted_url': 'trusted',
    ...                  'display_only_url': 'display normal'}
    >>> def get_security_level(url):
    ...     return site_security[url]
    >>> config['page_security_level'] = get_security_level


1. Testing register()
----------------------

    >>> io_widget.register()
    >>> mocks.registered_services['insert_io_subwidget'] == io_widget.insert_io_subwidget
    True


2. Testing insert_io_subwidget()
--------------------------------

There are various options that we need to tests, depending on the page content.
We first consider the simplest possible case (in terms of information 
included by io_widget.py), that of a page that does not include an
interpreter and whose security level is such that we "display" only the
page, and no interactive element is included.

    >>> page = mocks.Page()
    >>> page.url = 'display_only_url'
    >>> elem = Element('enclosing')
    >>> uid = '42'
    >>> io_widget.insert_io_subwidget(page, elem, uid)


