vlam.py tests
================================


vlam.py is, in some sense, the core of Crunchy as it reads an html page,
performs vlam substitution, and outputs back the final result.

It contains two classes and a number of methods that need to be tested:

#. `BasePage.__init__()`_
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
#. `add_charset()`_
#. `read()`_
#. An introduction to the processing of  `handlers`_.  It covers testing of
   process_handlers1(), process_handlers2(), process_handlers3(), 
   process_final_handlers1(), process_type1().
#. `extract_keyword()`_


Setting things up
--------------------

See how_to.rst_ for details.

.. _how_to.rst: how_to.rst

    >>> from StringIO import StringIO
    >>> from src.interface import Element, plugin, config, from_comet
    >>> from src.utilities import uidgen
    >>> plugin.clear()
    >>> config.clear()
    >>> from os import getcwd
    >>> config['crunchy_base_dir'] = getcwd()
    >>> import src.vlam as vlam
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
    ...     page = vlam.BasePage('dummy_username')
    ...     page.create_tree(fake_file)  # tested separately below
    ...     output = StringIO()
    ...     page.tree.write(output)
    ...     out_html = output.getvalue().encode('utf8')
    ...     return page, out_html
    >>>

Also, let us define the 4th part of that function as a function on its own

    >>> def output(page):
    ...     output = StringIO()
    ...     page.tree.write(output)
    ...     out_html = output.getvalue().encode('utf8')
    ...     return out_html
    >>>

.. _`BasePage.__init__()`:

Creating a page and a tree
---------------------------

Let's start by creating a simple page.

    >>> page = vlam.BasePage('dummy_username')
    >>> page.included
    set([])
    >>> print int(uidgen('dummy')) - int(page.pageid)
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
    '<html><head>brain<link href="/css/crunchy.css" rel="stylesheet" type="text/css" /><title>Hi!</title></head></html>'

Just to make sure, an even simpler case, with no head; one will be created for
proper insertion of css code.

    >>> no_body = '<html></html>'    # chosen for simpler output below
    >>> page_no_body, out_no_body = process_html(no_body)
    >>> page_no_body.add_crunchy_style()
    >>> output(page_no_body)
    '<html><head> <link href="/css/crunchy.css" rel="stylesheet" type="text/css" /></head></html>'

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

.. _`add_charset()`:

Testing add_charset()
---------------------

We test this method with a very simple page.

    >>> html = '<html><head>brain</head><body><p>This is a test.</p></body></html>'
    >>> page, out_html = process_html(html)
    >>> page.add_charset()
    >>> output(page)
    '<html><head>brain<meta content="text/html; charset=UTF-8" http-equiv="Content-Type" /></head><body><p>This is a test.</p></body></html>'

Next, we redo this test with a page that has no head (nor body).
A head should be added automatically.

    >>> html = '<html></html>'
    >>> page, out_html = process_html(html)
    >>> page.add_charset()
    >>> output(page)
    '<html><head> <meta content="text/html; charset=UTF-8" http-equiv="Content-Type" /></head></html>'

.. _`read()`:

Testing read()
--------------

Before we do this test, we will record the value of the DTD in case some
accidental editing is done.  This might help us identify the source of an error,
if ever one occurs in the test for read().

    >>> vlam.DTD
    '<!DOCTYPE html PUBLIC "-//W3C//DTD XHTML 1.0 Strict//EN" "http://www.w3.org/TR/xhtml1/DTD/strict.dtd">\n'

Next, we create a simple page.

    >>> html = '<html><head>brain</head><body><p>This is a test.</p></body></html>'
    >>> page, out_html = process_html(html)
    >>> page.read().encode('utf8')
    '<!DOCTYPE html PUBLIC "-//W3C//DTD XHTML 1.0 Strict//EN" "http://www.w3.org/TR/xhtml1/DTD/strict.dtd">\n\n<html><head>brain<meta content="text/html; charset=UTF-8" http-equiv="Content-Type" /></head><body><p>This is a test.</p></body></html>'


.. _`handlers`:

Processing handlers: an introduction
-------------------------------------

The processing of handlers can be a bit tricky to understand the
first time around.  By handlers, we mean one of the following three types:

-  handlers1 = {} # tag -> handler function
-  handlers2 = {} # tag -> attribute -> handler function
-  handlers3 = {} # tag -> attribute -> keyword -> handler function

We do not consider here the "page handlers" (begin_pagehandler and end_pagehandler).
To simplify the processing, the same 3 arguments are passed to each handler: 

1. the CrunchyPage instance
2. an Element to which the processing is meant to be applied
3. a unique id.

Not all three elements are necessarily required by every handler,
but they must ensure that they can handle receiving 3 elements.

As a rule, the more specific an instruction is, the higher its precedence.
Thus, if a (tag, attribute, keyword) is registered by a handler of type 3,
any element with this combination must be ignored by handlers of type 1 and 2.

Note that, at the time this test was written (Crunchy version 0.9.9.3),
no handler of type 2 were required; their role had been taken over by
"page handlers".

Before we begin testing some functions, let us create some fictitious handlers,
and a test function.

    >>> def func(page, elem, id):
    ...    print elem.text
    ...    return
    >>> handlers1 = {'a': func, 'b': func, 'c': func}
    >>> handlers2 = {'a': {'aa': func}, 'b': {'aa': func}}
    >>> handlers3 = {'a': {'aa': {'aaa': func, 'bbb': func}}, 'c': {'aa': {'aaa': func}, 'cc': {'ccc': func}}}
    >>> final_handlers1 = {'a': func, 'd': func}
    >>> vlam.BasePage.handlers1 = handlers1
    >>> vlam.BasePage.handlers2 = handlers2
    >>> vlam.BasePage.handlers3 = handlers3
    >>> vlam.BasePage.final_handlers1 = final_handlers1

Next, let us create a tree with these tags, and some others.  The text we put inside
each element will be a number chosen, by inspection of the above handlers structure, 
to be the handler type (1, 2 or 3).

    >>> open_html = "<html><head> </head><body>"
    >>> end_html = "</body></html>"
    >>> inner = "<a>1</a><a ee='eee'>1</a>"
    >>> page, out_html = process_html(open_html+inner+end_html)
    >>> output(page)
    '<html><head> </head><body><a>1</a><a ee="eee">1</a></body></html>'

    >>> page.process_handlers1()
    1
    1
    >>> page.process_handlers2()
    >>> page.process_handlers3()

    >>> inner = "<a>1</a><a aa='eee'>2</a>"
    >>> page, out_html = process_html(open_html+inner+end_html)
    >>> page.process_handlers1()
    1
    >>> page.process_handlers2()
    2
    >>> page.process_handlers3()

    >>> inner = "<a>1</a><a aa='aaa'>3</a>"
    >>> page, out_html = process_html(open_html+inner+end_html)
    >>> page.process_handlers1()
    1
    >>> page.process_handlers2()
    >>> page.process_handlers3()
    3

    >>> inner = "<a>1</a><c aa='aaa'>3</c>"
    >>> page, out_html = process_html(open_html+inner+end_html)
    >>> page.process_handlers1()
    1
    >>> page.process_handlers2()
    >>> page.process_handlers3()
    3

    >>> inner = "<a>1</a><c aa='ignore'>1</c>"
    >>> page, out_html = process_html(open_html+inner+end_html)
    >>> page.process_handlers1()
    1
    1
    >>> page.process_handlers2()
    >>> page.process_handlers3()

There are two equivalent ways to process handlers of type 1.

    >>> inner = "<a>1</a><c aa='ignore'>not final 1</c>"
    >>> page, out_html = process_html(open_html+inner+end_html)
    >>> page.process_handlers1()
    1
    not final 1
    >>> page.process_type1(page.handlers1)
    1
    not final 1

There is also the "final handlers" case.

    >>> page.process_final_handlers1()
    1
    >>> page.process_type1(page.final_handlers1)
    1



.. _`extract_keyword()`:

Testing extract_keyword()
-------------------------

A vlam keyword is the first complete word in an attribute string value.
Words are separated by blank spaces.

    >>> html = '<html><head a="keyword">brain</head></html>'
    >>> page, out_html = process_html(html)
    >>> page.find_head()
    >>> print page.extract_keyword(page.head, 'a')
    keyword
    >>> html = '<html><head a=" keyword ">brain</head></html>'
    >>> page, out_html = process_html(html)
    >>> page.find_head()
    >>> print page.extract_keyword(page.head, 'a')
    keyword
    >>> html = '<html><head a="    keyword ignore the rest">brain</head></html>'
    >>> page, out_html = process_html(html)
    >>> page.find_head()
    >>> print page.extract_keyword(page.head, 'a')
    keyword
    >>> html = '<html><head a="keyword      ignore the rest">brain</head></html>'
    >>> page, out_html = process_html(html)
    >>> page.find_head()
    >>> print page.extract_keyword(page.head, 'a')
    keyword
    >>> html = '<html><head a="">brain</head></html>'
    >>> page, out_html = process_html(html)
    >>> page.find_head()
    >>> print page.extract_keyword(page.head, 'a')
    None



