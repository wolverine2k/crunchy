execution.py tests
================================

execution.py is a plugin whose purpose is to register a http_handler
that is called whenever some Python code needs to be executed.

It contains two functions that need to be tested:

1. `register()`_
2. `exec_handler()`_

Setting things up
--------------------

    >>> from src.interface import plugin, config
    >>> config.clear()
    >>> plugin.clear()
    >>> plugin['session_random_id'] = 42
    >>> import src.tests.mocks as mocks
    >>> mocks.init()
    >>> def exec_code(data, arg):
    ...     print(data)
    ...     print(arg)
    >>> plugin['exec_code'] = exec_code
    >>> import src.plugins.execution as execution

.. _`register()`:

Testing register()
---------------------

register() simply registers one http handler

    >>> execution.register()
    >>> print(mocks.registered_http_handler['/exec42'] == execution.exec_handler)
    True

.. _`exec_handler()`:

Testing exec_handler()
-------------------------

    >>> request = mocks.Request(args={'uid':'spam'})
    >>> execution.exec_handler(request)
    data
    spam
    200
    End headers



