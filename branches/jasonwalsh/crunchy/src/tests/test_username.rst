username.py tests
================================

username.py, the simplest possible plugin,
has the following functions that require testing:

1. `register()`_
#. `insert_username()`_

0. Setting things up
--------------------

    >>> from src.interface import plugin, Element
    >>> plugin.clear()
    >>> import src.plugins.username as username
    >>> import src.tests.mocks as mocks
    >>> mocks.init()


.. _`register()`:

Testing register()
----------------------

    >>> username.register()
    >>> print mocks.registered_tag_handler #doctest: +ELLIPSIS
    {'span': {'title': {'username': <function insert_username at ...>}}}

Testing insert_username()
-------------------------

    >>> page = mocks.Page()
    >>> page.username = 'Crunchy'
    >>> elem = Element('whatever')
    >>> elem.text = "this will be replaced"
    >>> username.insert_username(page, elem, 42)
    >>> print elem.text
    Crunchy

