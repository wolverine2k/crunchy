no_markup.py tests
================================

no_markup.py has has the following functions that require testing:

1. `register()`_
#. `custom_vlam()`_

0. Setting things up
--------------------

    >>> from src.interface import plugin, config, Element, tostring
    >>> plugin.clear()
    >>> config.clear()
    >>> import src.plugins.no_markup as no_markup
    >>> import src.tests.mocks as mocks
    >>> mocks.init()
    >>> def repeat_args(*args):
    ...      for arg in args:
    ...          print arg
    >>>


.. _`register()`:

Testing register()
----------------------

    >>> no_markup.register()
    >>> print mocks.registered_final_tag_handlers #doctest: +ELLIPSIS
    {'pre': <function custom_vlam at ...>}


.. _`custom_vlam()`:

Testing custom_vlam()
--------------------------

First, no markup specified.

    >>> page = mocks.Page(username='Crunchy')
    >>> page.pre = Element("pre")
    >>> config['Crunchy'] = {}
    >>> config['Crunchy']['no_markup'] = None
    >>> no_markup.custom_vlam(page, page.pre, '42')
    >>> print tostring(page.pre).replace('>', '>\n')
    <pre />
    <BLANKLINE>

Next, some silly markup...

    >>> config['Crunchy']['no_markup'] = "silly"
    >>> page.handlers3["pre"] = {}
    >>> page.handlers3["pre"]["title"] = {}
    >>> page.handlers3["pre"]["title"]["silly"] = repeat_args # fake handler
    >>> no_markup.custom_vlam(page, page.pre, '42') #doctest: +ELLIPSIS
    <src.tests.mocks.Page object at ...>
    <Element pre at ...>
    42
    >>> print tostring(page.pre).replace('>', '>\n')
    <pre title="silly" />
    <BLANKLINE>

