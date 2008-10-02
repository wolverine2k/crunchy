editarea.py tests
==================

editarea.py is a plugin whose purpose is to insert the appropriate code in 
a page to enable the javascript based editor "editarea".  It has the following functions
that require testing:

#. `register()`_: registers a service available to other plugins.
#. `enable_editarea()`_: enables an editarea editor on a given element (textarea) of a page.



Since enable_editarea() calls add_hidden_load_and_save() which, in turns, calls the
remaining two functions, we will test them in reverse, that is, the test order will be
1, 5, 4, 3, 2.

Note that the purpose of most of these functions is simply to append new html tags
with various attributes.  As a result, the tests that need to be performed are
rather simplistic and tedious.  They also have been written "after the fact" since
the real test for developing the code was in looking at the UI that was generated.

Setting things up
--------------------

See how_to.rst_ for details.

.. _how_to.rst: how_to.rst

    >>> from src.interface import config, plugin, Element
    >>> config.clear()
    >>> plugin.clear()
    >>> config['Crunchy'] = {}
    >>> config['Crunchy']['editarea_language'] = 'en'
    >>> plugin['session_random_id'] = '42'
    >>> import src.plugins.editarea as editarea
    >>> import src.tests.mocks as mocks
    >>> mocks.init()

.. _`register()`:

Testing register()
---------------------

   >>> editarea.register()
   >>> print(mocks.registered_services['enable_editarea'] == editarea.enable_editarea)
   True

.. _`addSavePython()`:



