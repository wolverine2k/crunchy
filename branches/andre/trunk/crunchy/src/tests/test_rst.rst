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

   >>> import src.plugins.rst as rst
   >>> from src.interface import Element
   >>> import src.tests.mocks as mocks
   >>> mocks.init()
   
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
    >>> rst.register() 
    >>> if _docutils_installed:
    ...     print(mocks.registered_tag_handler['span']['title']['load_rst'] == rst.insert_load_rst)
    ...     print(mocks.registered_http_handler['/rst'] == rst.load_rst)
    ... else:
    ...     print(True)
    ...     print(True)
    True
    True

2. Testing insert_load_rst()
------------------------------

This method inserts two forms inside a <span> element.
    
    >>> fake_page = ''  # unused
    >>> fake_uid = '2'  # unused
    >>> span = Element("span")
    >>> rst.insert_load_rst(fake_page, span, fake_uid)
    >>> forms = []
    >>> for el in span.getiterator():
    ...     if el.tag == "form": forms.append(el)
    ...
    >>> len(forms)
    2

Testing the first generated form

    >>> forms[0].attrib["name"][:11]
    'browser_rst'
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

    >>> forms[1].attrib["name"][:10]
    'submit_rst'
    >>> forms[1].attrib["method"]
    'get'
    >>> forms[1].attrib["action"]
    '/rst'
    >>> inputs2 = forms[1].findall("input")
    >>> len(inputs2)
    2
    >>> inputs2[0].attrib["type"]
    'hidden'
    >>> inputs2[0].attrib["name"]
    'url'
    >>> inputs2[1].attrib["type"]
    'submit'