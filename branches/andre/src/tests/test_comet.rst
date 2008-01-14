comet.py tests
================================

Tested successfully with Python 2.4, 2.5, 3.0a1 and 3.0a2

comet.py is a plugin whose purpose is simply to register links
to two services provided by cometIO.py.

It contains one method that need to be tested:
1. register()

0. Setting things up
--------------------

We begin by importing the required information from other
modules and create a dummy session id

   >>> from src.interface import plugin
   >>> plugin['session_random_id'] = 42
   >>> import src.plugins.comet
   >>> import src.cometIO as cometIO
   >>> import src.tests.mocks as mocks



1. Testing register()
---------------------

# Test - check that the two http_handlers have been registered
    >>> src.plugins.comet.register()
    >>> print(mocks.registered_http_handler['/input42'] == cometIO.push_input)
    True
    >>> print(mocks.registered_http_handler['/comet'] == cometIO.comet)
    True

