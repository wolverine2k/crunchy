vlam_load_remote.py tests
================================

Tested successfully with Python 2.4, 2.5, 3.0a1 and 3.0a2

vlam_load_remote.py is a plugin whose purpose is to create a form
allowing a user to browse for a remote tutorial to be loaded by Crunchy.

It contains two methods that need to be tested:
1. register()
2. insert_load_remote()

0. Setting things up
--------------------

See how_to.rst_ for details.

.. _how_to.rst: how_to.rst

   >>> import src.plugins.vlam_load_remote as vlam_load_remote
   >>> from src.interface import Element, plugin
   >>> plugin.clear()
   >>> import src.tests.mocks as mocks
   >>> mocks.init()

1. Testing register()
---------------------

# Test - check that tag handler, and service have been registered
    >>> vlam_load_remote.register()
    >>> print(mocks.registered_tag_handler['span']['title']['load_remote'] == vlam_load_remote.insert_load_remote)
    True
    
2. Testing insert_load_local()
------------------------------

This method inserts one form inside a <span> element.
    
    >>> fake_page = ''  # unused
    >>> fake_uid = '2'  # unused
    >>> span = Element("span")
    >>> span.text = "Cool url"
    >>> vlam_load_remote.insert_load_remote(fake_page, span, fake_uid)
    >>> form = span.find("form")

    >>> form.attrib["name"]
    'url'
    >>> form.attrib["size"]
    '80'
    >>> form.attrib["method"]
    'get'
    >>> form.attrib["action"]
    '/remote'
    >>> inputs = form.findall("input")
    >>> len(inputs)
    2
    >>> inputs[0].attrib["name"]
    'url'
    >>> inputs[0].attrib["size"]
    '80'
    >>> inputs[0].attrib["value"]
    'Cool url'
    >>> inputs[1].attrib["type"]
    'submit'
