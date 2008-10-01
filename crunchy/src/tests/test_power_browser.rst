power_browser.py tests
================================

power_browser.py has has the following functions that require testing:

1. `register()`_
#. `insert_browser()`_


0. Setting things up
--------------------



    >>> from src.interface import plugin, config, Element, tostring
    >>> import src.utilities
    >>> src.utilities.COUNT = 0
    >>> plugin.clear()
    >>> def dummy(*args):
    ...    print args
    >>> plugin['local_html'] = dummy
    >>> plugin['remote_html'] = dummy
    >>> plugin['local_python'] = dummy
    >>> config.clear()
    >>> config['Crunchy'] = {}
    >>> config['Crunchy']['editarea_language'] = 'en'
    >>> import src.plugins.power_browser as pb
    >>> import src.tests.mocks as mocks
    >>> mocks.init()


.. _`register()`:

Testing register()
----------------------

    >>> pb.register()
    >>> print mocks.registered_end_pagehandlers #doctest: +ELLIPSIS
    {'<function insert_browser at ...>': <function insert_browser at ...>}


.. _`insert_browser()`:

Testing insert_browser()
--------------------------

First, reStructuredText files.

    >>> page = mocks.Page()
    >>> page.body = Element("body")
    >>> config['Crunchy']['power_browser'] = 'rst'
    >>> pb.insert_browser(page)
    >>> print tostring(page.body).replace('>', '>\n')
    <body>
    <div>
     <form name="browser_rst1">
    <input name="filename" onblur="document.submit_rst2.url.value=document.browser_rst1.filename.value" size="80" type="file" />
    <br />
    </form>
    <form action="/rst" method="get" name="submit_rst2">
    <input name="url" type="hidden" />
    <input class="crunchy" type="submit" value="Load local ReST file" />
    </form>
    </div>
    </body>
    <BLANKLINE>

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
    >>> print tostring(page.body).replace('>', '>\n')
    <body />
    <BLANKLINE>

None should yield the same result.

    >>> page = mocks.Page()
    >>> page.body = Element("body")
    >>> config['Crunchy']['power_browser'] = None
    >>> pb.insert_browser(page)
    >>> print tostring(page.body).replace('>', '>\n')
    <body />
    <BLANKLINE>

