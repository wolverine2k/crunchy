rst.py tests
================================

rst.py is a plugin whose purpose is to create a form allowing a user to browse 
for a local tutorial written in reStructuredText to be loaded by Crunchy.

It contains two functions that need to be tested:
1. register()
2. insert_load_rst()

A third function, load_rst(), requires to read some file; for this reason,
we will not, for the moment, create a test for it, but rely instead on
some functional testing that we do on a regular basis.

0. Setting things up
--------------------

We need to import the plugin, something to create an Element, and
set up some dummy registering functions.

   >>> from src.interface import Element, plugin
   >>> plugin.clear()
   >>> def dummy_add(*args):
   ...      for arg in args:
   ...          print arg
   >>> plugin['add_vlam_option'] = dummy_add
   >>> import src.tests.mocks as mocks
   >>> mocks.init()
   >>> import src.plugins.rst as rst
   
Note that if docutils is not installed for the Python version we are testing,
some tests would normally fail; we prevent this from happening by setting up
an appropriate flag.

   >>> _docutils_installed = True
   >>> try:
   ...     from docutils.core import publish_string
   ... except:
   ...     _docutils_installed = False

1. Testing register()
---------------------

# Test - check that tag handler, and service have been registered
    >>> if _docutils_installed:
    ...     rst.register()
    ... else:
    ...     print "power_browser"
    ...     print "rst"
    power_browser
    rst
    >>> if _docutils_installed:
    ...     print(mocks.registered_tag_handler['div']['title']['local_rst_file'] == rst.insert_load_rst)
    ...     print(mocks.registered_http_handler['/rst'] == rst.load_rst)
    ... else:
    ...     print(True)
    ...     print(True)
    True
    True

