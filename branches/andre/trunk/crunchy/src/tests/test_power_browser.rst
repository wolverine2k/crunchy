power_browser.py tests
================================

power_browser.py has has the following functions that require testing:

1. `register()`_
#. `insert_browser()`_


0. Setting things up
--------------------



    >>> from src.interface import (
    ...     plugin, config, Element, tostring,
    ...     additional_menu_items)
    >>> config.clear()
    >>> plugin.clear()
    >>> from src.interface import ElementTree as et
    >>> from os import getcwd
    >>> config['crunchy_base_dir'] = getcwd()
    >>> import src.utilities
    >>> src.utilities.COUNT = 0

    >>> def dummy(*args):
    ...    print(args)
    >>> plugin['local_html'] = dummy
    >>> plugin['remote_html'] = dummy
    >>> plugin['local_python'] = dummy
    >>> plugin['local_rst'] = dummy

    >>> config['Crunchy'] = {}
    >>> config['Crunchy']['editarea_language'] = 'en'
    >>> import src.plugins.power_browser as pb
    >>> import src.tests.mocks as mocks
    >>> mocks.init()


.. _`register()`:

Testing register()
----------------------

    >>> pb.register()
    >>> print(mocks.registered_end_pagehandlers) #doctest: +ELLIPSIS
    {'<function insert_browser at ...>': <function insert_browser at ...>}


.. _`insert_browser()`:

Testing insert_browser()
--------------------------

First, reStructuredText files.

    >>> page = mocks.Page()
    >>> page.body = Element("body")
    >>> config['Crunchy']['power_browser'] = 'local_rst'
    >>> pb.insert_browser(page) #doctest: +ELLIPSIS
    (...Page...div...dummy...)

Next, local html tutorials.

    >>> page = mocks.Page()
    >>> page.body = Element("body")
    >>> config['Crunchy']['power_browser'] = 'local_html'
    >>> pb.insert_browser(page) #doctest: +ELLIPSIS
    (...Page...div...dummy...)


Next, remote html tutorials.

    >>> page = mocks.Page()
    >>> page.body = Element("body")
    >>> config['Crunchy']['power_browser'] = 'remote_html'
    >>> pb.insert_browser(page) #doctest: +ELLIPSIS
    (...Page...div...dummy...)

Python files.

    >>> page = mocks.Page()
    >>> page.body = Element("body")
    >>> config['Crunchy']['power_browser'] = 'local_python'
    >>> pb.insert_browser(page) #doctest: +ELLIPSIS
    (...Page...div...dummy...)

An unrecognized value.

    >>> page = mocks.Page()
    >>> page.body = Element("body")
    >>> config['Crunchy']['power_browser'] = 'unknown'
    >>> pb.insert_browser(page)
    >>> print(tostring(page.body))
    <body />

None should yield the same result.

    >>> page = mocks.Page()
    >>> page.body = Element("body")
    >>> config['Crunchy']['power_browser'] = None
    >>> pb.insert_browser(page)
    >>> print(tostring(page.body))
    <body />

Testing add_browsing_to_menu
============================

    >>> pb.add_browsing_to_menu(dummy=None)
    >>> assert 'browsing' in additional_menu_items
    >>> print(et.tostring(additional_menu_items['browsing']))
    <li><a href="/docs/basic_tutorial/browsing.html">Browsing</a></li>
