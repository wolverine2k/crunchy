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
modules and create some dummy functions

   >>> import src.plugins.comet
   >>> from src.interface import plugin
   >>> import src.cometIO as cometIO
   >>> registered = {}
   >>> def dummy(name, function):
   ...     registered[name] = function
   ...
   >>> plugin['register_http_handler'] = dummy
   >>> plugin['session_random_id'] = 42

1. Testing register()
---------------------

# Test - check that the two http_handlers have been registered
    >>> src.plugins.comet.register()
    >>> print(registered['/input42'] == cometIO.push_input)
    True
    >>> print(registered['/comet'] == cometIO.comet)
    True

