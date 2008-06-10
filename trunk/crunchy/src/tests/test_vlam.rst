vlam.py tests
================================


vlam.py is, in some sense, the core of Crunchy as it reads an html page,
performs vlam substitution, and outputs back the final result.

It contains two classes and a number of methods that need to be tested:

#. `_BasePage.__init__()`_
#. `create_tree()`_
#. `find_head()`_
#. `find_body()`_
#. `add_include()`_
#. `includes()`_
#. `add_css_code()`_
#. `add_crunchy_style()`_
#. `add_user_style()`_
#. `add_js_code()`_
#. `insert_js_file()`_

Setting things up
--------------------

See how_to.rst_ for details.

.. _how_to.rst: how_to.rst

    >>> import src.vlam as vlam
    >>> from StringIO import StringIO
    >>> from src.interface import Element, plugin, config, from_comet
    >>> from src.utilities import uidgen
    >>> plugin.clear()
    >>> config.clear()
    >>> from_comet.clear()
    >>> def dummy(arg):
    ...    pass
    >>> from_comet['register_new_page'] = dummy
   

Let us define a utility function that will:

1. Take an html string
2. Create a page
3. Create a tree
4. Create a new html string from that tree, for comparison

    >>> def process_html(html):
    ...     fake_file = StringIO()
    ...     fake_file.write(html)
    ...     fake_file.seek(0)
    ...     page = vlam._BasePage()
    ...     page.create_tree(fake_file)  # tested separately below
    ...     output = StringIO()
    ...     page.tree.write(output)
    ...     out_html = output.getvalue()
    ...     return page, out_html
    >>>

Also, let us define the 4th part of that function as a function on its own

    >>> def output(page):
    ...     output = StringIO()
    ...     page.tree.write(output)
    ...     out_html = output.getvalue()
    ...     return out_html
    >>>

.. _`_BasePage.__init__()`:

Creating a page and a tree
---------------------------

Let's start by creating a simple page.

    >>> page = vlam._BasePage()
    >>> page.included
    set([])
    >>> print int(uidgen()) - int(page.pageid)
    1

.. _`create_tree()`:

The next step is to create a page and a tree using our utility function
introduced above, which calls create_tree().

    >>> html = '<html><head>brain</head><body><p>This is a test.</p></body></html>'
    >>> page, out_html = process_html(html)

Let's verify that this tree has been read properly by writing it out again.

    >>> out_html == html
    True

Since we are using BeautifulSoup, we can handle files that have major problems.
Let's verify this for a file that has major problems with missing closing tags.

    >>> bad_html = '<html><head>brain<body><p>This is a test.'
    >>> page2, bad_out_html = process_html(bad_html)
    >>> bad_out_html
    '<html><head>brain<body><p>This is a test.</p></body></head></html>'

The result is not entirely what we might have liked, as the head encloses the body,
but all tags are at least closed. 
Finally, what happens if we pass a straight text file.

    >>> no_tags = 'This is just text'
    >>> page_no_tags, out_no_tags = process_html(no_tags)
    >>> out_no_tags
    '<html>This is just text</html>'

We do get a very basic html page...

Finally, three more examples

    >>> no_html = '<head>brain</head><body><p>This is a test.</p></body>'
    >>> page_no_html, out_no_html = process_html(no_html)
    >>> out_no_html
    '<html><head>brain</head><body><p>This is a test.</p></body></html>'

    >>> no_head = '<html><body><p>This is a test.</p></body></html>'
    >>> page_no_head, out_no_head = process_html(no_head)
    >>> out_no_head
    '<html><body><p>This is a test.</p></body></html>'

    >>> no_body = '<html><head>brain</head></html>'
    >>> page_no_body, out_no_body = process_html(no_body)
    >>> out_no_body
    '<html><head>brain</head></html>'

    >>> just_body = '<body><p>This is a test.</p></body>'
    >>> page_just_body, out_just_body = process_html(just_body)
    >>> out_just_body
    '<html><body><p>This is a test.</p></body></html>'

Finally, a weird example with a DTD, but no html tag.

    >>> dtd_no_html = vlam.DTD + '<head>brain</head><body><p>This is a test.</p></body>'
    >>> page_dtd_no_html, out_dtd_no_html = process_html(dtd_no_html)
    >>> out_dtd_no_html
    '<html>\n<head>brain</head><body><p>This is a test.</p></body></html>'

.. _`find_head()`:

Testing find_head()
--------------------

    >>> page.find_head()
    >>> print(page.head.text)
    brain

Let's try in the case of a missing head.

    >>> page_no_head.find_head()
    >>> page_no_head.head.text == ' '
    True

.. _`find_body()`:

Testing find_body()
--------------------

    >>> page.find_body()
    >>> print(page.body[0].text)
    This is a test.

Let's try in the case of a missing body.

    >>> page_no_body.find_body()
    >>> page_no_body.body[0].text   # enclosed inside an <h1>
    'Missing body from original file'

.. _`add_include()`:

Testing add_include()
---------------------

    >>> page.included
    set([])
    >>> page.add_include('junk')
    >>> page.included
    set(['junk'])
    >>> page.add_include('more junk')
    >>> page.included
    set(['junk', 'more junk'])

.. _`includes()`:

Testing includes()
---------------------

    >>> page.includes('junk')
    True
    >>> page.includes('more junk')
    True
    >>> page.includes('more')
    False
    >>> page.includes('Sally')
    False

.. _`add_css_code()`:

Testing add_css_code()
-----------------------

    >>> sample = "pre{font:1000pt;}"
    >>> no_body = '<html><head>brain</head></html>'    # chosen for simpler output below
    >>> page_no_body, out_no_body = process_html(no_body)
    >>> page_no_body.add_css_code(sample)
    >>> output(page_no_body)
    '<html><head>brain<style type="text/css">pre{font:1000pt;}</style></head></html>'

Just to make sure, an even simpler case, with no head; one will be created for
proper insertion of css code.

    >>> no_body = '<html></html>'
    >>> page_no_body, out_no_body = process_html(no_body)
    >>> page_no_body.add_css_code(sample)
    >>> output(page_no_body)
    '<html><head> <style type="text/css">pre{font:1000pt;}</style></head></html>'

.. _`add_crunchy_style()`:

Testing add_crunchy_style()
---------------------------

    >>> no_body = '<html><head>brain<title>Hi!</title></head></html>'
    >>> page_no_body, out_no_body = process_html(no_body)
    >>> page_no_body.add_crunchy_style()
    >>> output(page_no_body)
    '<html><head>brain<link href="/crunchy.css" rel="stylesheet" type="text/css" /><title>Hi!</title></head></html>'

Just to make sure, an even simpler case, with no head; one will be created for
proper insertion of css code.

    >>> no_body = '<html></html>'    # chosen for simpler output below
    >>> page_no_body, out_no_body = process_html(no_body)
    >>> page_no_body.add_crunchy_style()
    >>> output(page_no_body)
    '<html><head> <link href="/crunchy.css" rel="stylesheet" type="text/css" /></head></html>'

.. _`add_js_code()`:


.. _`add_user_style()`:

Testing add_user_style()
-------------------------

First, we test with an empty config file; while it was empty at the start, 
we do it again in case other tests are added at some later time.

    >>> config.clear()
    >>> no_body = '<html><head>brain<title>Hi!</title></head></html>'
    >>> page_no_body, out_no_body = process_html(no_body)
    >>> page_no_body.add_user_style()
    >>> output(page_no_body)
    '<html><head>brain<title>Hi!</title></head></html>'

Next, we consider the case where an entry exists but no style is needed.

    >>> config['my_style'] = False
    >>> page_no_body.add_user_style()
    >>> output(page_no_body)
    '<html><head>brain<title>Hi!</title></head></html>'

Next, an entry call for some styling, but none is defined.

    >>> config['my_style'] = True
    >>> page_no_body.add_user_style()
    >>> output(page_no_body)
    '<html><head>brain<title>Hi!</title></head></html>'

Next, some null styling is defined.

    >>> config['styles'] = {}
    >>> page_no_body.add_user_style()
    >>> output(page_no_body)
    '<html><head>brain<title>Hi!</title></head></html>'

Finally, some real styling is defined.

    >>> config['styles'] = {'pre': 'font:1000pt;', 'body': 'color: red;'}
    >>> page_no_body.add_user_style()
    >>> output(page_no_body)
    '<html><head>brain<title>Hi!</title><style type="text/css">pre{font:1000pt;}\nbody{color: red;}\n</style></head></html>'

Testing add_js_code()
---------------------

    >>> sample = "alert(Crunchy!);"
    >>> no_body = '<html><head>brain</head></html>'    # chosen for simpler output below
    >>> page_no_body, out_no_body = process_html(no_body)
    >>> page_no_body.add_js_code(sample)
    >>> output(page_no_body)
    '<html><head>brain<script type="text/javascript">alert(Crunchy!);</script></head></html>'

Just to make sure, an even simpler case, with no head; one will be created for
proper insertion of javascript code.

    >>> no_body = '<html></html>'
    >>> page_no_body, out_no_body = process_html(no_body)
    >>> page_no_body.add_js_code(sample)
    >>> output(page_no_body)
    '<html><head> <script type="text/javascript">alert(Crunchy!);</script></head></html>'

.. _`insert_js_file()`:

Testing insert_js_file()
------------------------

    >>> no_body = '<html><head>brain</head></html>'    # chosen for simpler output below
    >>> page_no_body, out_no_body = process_html(no_body)
    >>> page_no_body.insert_js_file('smart.js')
    >>> output(page_no_body)
    '<html><head>brain<script src="smart.js" type="text/javascript"> </script></head></html>'

Just to make sure, an even simpler case, with no head; one will be created for
proper insertion of javascript code.

    >>> no_body = '<html></html>'
    >>> page_no_body, out_no_body = process_html(no_body)
    >>> page_no_body.insert_js_file('smart.js')
    >>> output(page_no_body)
    '<html><head> <script src="smart.js" type="text/javascript"> </script></head></html>'



