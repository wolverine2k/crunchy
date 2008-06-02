io_widget.py tests
================================

Tested successfully with Python 2.4, 2.5, 3.0a1 and 3.0a2

io_widget.py is a plugin which handles text and graphical IO
It has the following functions that require testing:

1. register(): registers a service available to other plugins.
2. insert_io_subwidget(): insert an output widget into elem, usable for editors
    interpreters and  includes a canvas


0. Setting things up
--------------------

See how_to.rst_ for details.
Note that io_widget imports editarea.py which requires 
config['editarea_language'].

.. _how_to.rst: how_to.rst


    >>> from src.interface import plugin, config, Element, python_version
    >>> plugin.clear()
    >>> plugin['session_random_id'] = 42
    >>> config.clear()
    >>> config['editarea_language'] = 'en'
    >>> import src.plugins.io_widget as io_widget
    >>> import src.tests.mocks as mocks
    >>> mocks.init()
    >>> try:
    ...     import ctypes
    ...     config['ctypes_available'] = True
    ... except:
    ...     config['ctypes_available'] = False

We also need to define some mock functions and values.

    >>> site_security = {'trusted_url': 'trusted',
    ...                  'display_only_url': 'display normal'}
    >>> def get_security_level(url):
    ...     return site_security[url]
    >>> config['page_security_level'] = get_security_level


1. Testing register()
----------------------

    >>> io_widget.register()
    >>> mocks.registered_services['insert_io_subwidget'] == io_widget.insert_io_subwidget
    True


2. Testing insert_io_subwidget()
--------------------------------

There are various options that we need to tests, depending on the page content.

2a. Testing the display only option.
------------------------------------

We first consider the simplest possible case (in terms of information 
included by io_widget.py), that of a page that does not include an
interpreter and whose security level is such that we "display" only the
page, and no interactive element is included.

    >>> page = mocks.Page()
    >>> page.url = 'display_only_url'
    >>> elem = Element('parent')
    >>> uid = '42'
    >>> io_widget.insert_io_subwidget(page, elem, uid)

In this simplest case, three elements will have been included.
As a first crude test, we investigate to see if all the required elements 
have been inserted (and none unexpected).

    >>> spans = []
    >>> inputs = []
    >>> buttons = []
    >>> parent = []
    >>> for el in elem.getiterator():
    ...     if el.tag == "span":
    ...         spans.append(el)
    ...     elif el.tag == "input":
    ...         inputs.append(el)
    ...     elif el.tag == "parent":
    ...         parent.append(el)
    ...     else:
    ...         print("Unexpected element found")
    ...
    >>> len(spans)
    2
    >>> len(inputs)
    1
    >>> len(parent)
    1
    >>> page.added_info
    []

Next, we look at each elements in a bit more detail.

    >>> output = spans[0]
    >>> output.attrib['class'] == 'output'
    True
    >>> output.attrib['id'] == 'out_' + uid
    True
    >>> output.text == '\n'
    True
    >>> span_input = spans[1]
    >>> inp = span_input.find('input')
    >>> inp == inputs[0]
    True
    >>> inp.attrib['id'] == 'in_' + uid
    True
    >>> inp.attrib["onkeydown"] == 'return push_keys(event, "%s")' % uid
    True
    >>> inp.attrib['class'] == 'input'
    True
    >>> inp.attrib['type'] == 'text'
    True

2b. Testing a non-Borg interpreter
----------------------------------

We now consider a page that does include an
interpreter and whose security level is such that we do more than
"display" only the page.

    >>> page = mocks.Page()
    >>> page.url = 'trusted_url'
    >>> elem = Element('parent')
    >>> uid = '42'
    >>> io_widget.insert_io_subwidget(page, elem, uid, interp_kind="Human")

In this simplest case, three elements will have been included.
As a first crude test, we investigate to see if all the required elements 
have been inserted (and none unexpected).

    >>> spans = []
    >>> inputs = []
    >>> imgs = []
    >>> textareas = []
    >>> a_s = []
    >>> parent = []
    >>> for el in elem.getiterator():
    ...     if el.tag == "span":
    ...         spans.append(el)
    ...     elif el.tag == "input":
    ...         inputs.append(el)
    ...     elif el.tag == "parent":
    ...         parent.append(el)
    ...     elif el.tag == "a":
    ...         a_s.append(el)
    ...     elif el.tag == "img":
    ...         imgs.append(el)
    ...     elif el.tag == "textarea":
    ...         textareas.append(el)
    ...     else:
    ...         print("Unexpected element found: " + str(el.tag))
    ...
    >>> len(spans)
    2
    >>> len(inputs)
    1
    >>> len(parent)
    1
    >>> len(a_s)
    2
    >>> len(textareas)
    1
    >>> len(imgs)
    2

Note that we also need to check if the proper "includes" have been inserted.

    >>> page.added_info
    ['includes', ('add_include', 'io_included'), 'add_js_code', 'add_css_code', 'includes', ('add_include', 'push_input_included'), 'add_js_code', 'includes', ('add_include', 'editarea_included'), 'add_js_code', ('insert_js_file', '/edit_area/edit_area_crunchy.js')]

todo: we need to conclude this test as we did with the previous one, to check
the content of the new elements.

2c. Testing with a Borg interpreter
------------------------------------

to do
