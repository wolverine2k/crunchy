links.py tests
=================

Tested successfully with Python 2.4, 2.5

links.py is a plugin whose main purpose is to rewrite urls in a form that
can be used by Crunchy.  
It has the following functions that require testing:

1. register(): registers some tag handlers.
2. external_link(): deal with links that point to external file meant to be 
unprocessed by Crunchy.
3. a_tag_handler(): 
4. link_tag_handler():
5. src_handler():
6. style_handler()
7. secure_url():

0. Setting things up
--------------------

See how_to.rst_ for details.

.. _how_to.rst: how_to.rst

    >>> from src.interface import plugin, Element, SubElement
    >>> plugin.clear()
    >>> import src.plugins.links as links
    >>> import src.tests.mocks as mocks
    >>> mocks.init()
    >>> page_default = mocks.Page()
    >>> page_default.is_from_root = True
    >>> page_remote = mocks.Page()
    >>> page_remote.is_remote = True
    >>> page_local = mocks.Page()
    >>> page_local.is_local = True


1. Testing register()
----------------------

    >>> links.register()
    >>> 
    >>> mocks.registered_tag_handler['a'][None][None] == links.a_tag_handler
    True
    >>> mocks.registered_tag_handler['a']['title']['external_link'] == links.external_link
    True
    >>> mocks.registered_tag_handler['img'][None][None] == links.src_handler
    True
    >>> mocks.registered_tag_handler['link'][None][None] == links.link_tag_handler
    True
    >>> mocks.registered_tag_handler['style'][None][None] == links.style_handler
    True


2. Testing external_link()
--------------------------

This function leaves an external link, of the form http://... unchanged,
except that it adds an image to help the user identify it.

    >>> fake_url_1 = "http://www.python.org"
    >>> a_link = Element('a', href=fake_url_1)
    >>> a_link.text = "Python"

We will first do a test with each page type, with a different number of
arguments for each.

    >>> links.external_link(page_default, a_link)
    >>> print a_link[0].tag, a_link[0].attrib['src']
    img /external_link.png
    >>> links.external_link(page_local, a_link, 'dummy1')
    >>> print a_link[0].tag, a_link[0].attrib['src']
    img /external_link.png
    >>> links.external_link(page_remote, a_link, 'dummy1', 'dummy2')
    >>> print a_link[0].tag, a_link[0].attrib['src']
    img /external_link.png

Next, we do an example with a more complicated link object, one that
has a subelement.

    >>> a_link = Element('a', href=fake_url_1)
    >>> a_link.text = " "
    >>> an_image = SubElement(a_link, 'img', src="logo.png", alt="Python")
    >>> a_link.tail = "official website"
    >>> links.external_link(page_default, a_link)
    >>> print a_link[0].tag, a_link[0].attrib['src']
    img logo.png
    >>> print a_link[1].tag, a_link[1].attrib['src']
    img /external_link.png

3. Testing a_tag_handler()
--------------------------

To do.

4. Testing link_tag_handler()
-----------------------------

To do.

5. Testing src_handler()
------------------------



