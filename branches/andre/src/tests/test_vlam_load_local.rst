vlam_load_local.py tests
================================

Tested successfully with Python 2.4, 2.5, 3.0a1 and 3.0a2

vlam_load_local.py is a plugin whose purpose is to create a form
allowing a user to browse for a local tutorial to be loaded by Crunchy.

It contains two methods that need to be tested:
1. register()
2. insert_load_local()

0. Setting things up
--------------------

We simply need to import the plugin and something to create an Element

   >>> import src.plugins.vlam_load_local as vlam_load_local
   >>> from src.interface import Element, plugin
   >>> registered = None
   >>> def dummy(a, b, c, fn):
   ...     global registered
   ...     registered = fn
   ...
   >>> plugin['register_tag_handler'] = dummy

1. Testing register()
---------------------

# Test - check that tag handler, and service have been registered
    >>> vlam_load_local.register() 
    >>> print(registered == vlam_load_local.insert_load_local)
    True

2. Testing insert_load_local()
------------------------------

This method inserts two forms inside a <span> element.
    
    >>> fake_page = ''  # unused
    >>> fake_uid = '2'  # unused
    >>> span = Element("span")
    >>> vlam_load_local.insert_load_local(fake_page, span, fake_uid)
    >>> forms = []
    >>> for el in span.getiterator():
    ...     if el.tag == "form": forms.append(el)
    ...
    >>> len(forms)
    2

Testing the first generated form

    >>> forms[0].attrib["name"]
    'browser_'
    >>> input = forms[0].find("input")
    >>> input.attrib["name"]
    'filename'
    >>> input.attrib["size"]
    '80'
    >>> input.attrib["type"]
    'file'
    >>> forms[0].find("br") == None
    False

Now the second one

    >>> forms[1].attrib["name"]
    'submit_'
    >>> forms[1].attrib["method"]
    'get'
    >>> forms[1].attrib["action"]
    '/local'
    >>> inputs2 = forms[1].findall("input")
    >>> len(inputs2)
    2
    >>> inputs2[0].attrib["type"]
    'hidden'
    >>> inputs2[0].attrib["name"]
    'url'
    >>> inputs2[1].attrib["type"]
    'submit'