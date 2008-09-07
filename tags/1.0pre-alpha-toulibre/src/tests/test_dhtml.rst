dhtml.py tests
================

dhtml.py is a module which is meant to be imported by a Crunchy user
to add elements (such as images) dynamically on an html page.
It has the following elements that require testing:

#. `\_Tree class`_
#. `\_Tree.append_child()`_
#. `\_Tree.remove_child()`_
#. `\_Tree.remove_all_children()`_
#. `\_Tree.delete()`_
#. `append() and remove()`_  # we need to test them together
#. `image()`_ - a special case of append()
#. `_js_append_html()`_
#. `_js_remove_html()`_

Setting things up
------------------

See how_to.rst_ for details.

.. _how_to.rst: how_to.rst

    >>> import os
    >>> import re
    >>> remove_pattern = re.compile('\(\"(.+?)\"\)')
    >>> append_pattern1 = remove_pattern  
    >>> append_pattern2 = re.compile("\(\'(.+?)\', \'(.+?)\'\)")
    >>> append_pattern3 = re.compile("\(\'(.+?)\'\)\.([_A-Za-z0-9]*)=\'(.+?)\';")
    >>> from src.interface import plugin, config
    >>> plugin.clear()
    >>> def dummy1():
    ...    return
    >>> plugin['get_pageid'] = dummy1
    >>> def dummy2(dummy, javascript):
    ...    if 'obsolete' in javascript:  # from _js_remove_html
    ...        print(remove_pattern.findall(javascript))
    ...    else:
    ...        print(append_pattern1.findall(javascript) + 
    ...              append_pattern2.findall(javascript) +
    ...              append_pattern3.findall(javascript))
    >>> plugin['exec_js'] = dummy2
    >>> def get_uid():
    ...    return '42'
    >>> plugin['get_uid'] = get_uid
    >>> config.clear()
    >>> config['temp_dir'] = os.path.expanduser('~') # only for tests
    >>> import src.imports.dhtml as dhtml

.. _\_Tree class:

Testing the _Tree class
------------------------

The _Tree class has the following methods:

- append_child()
- remove_child()
- remove_all_children()
- delete()

Let us create a Tree with the following structure::

  root
     c1
     c2
         c3
         c4
              c5
              c6
         c7
              c8
     c9
     c10

Afterwards, we will manipulate this tree to remove elements.

    >>> root = dhtml._Tree(0)
    >>> c1 = dhtml._Tree(1, root)
    >>> c2 = dhtml._Tree(2, root)
    >>> c3 = dhtml._Tree(3, c2)
    >>> c4 = dhtml._Tree(4, c2)
    >>> c5 = dhtml._Tree(5, c4)
    >>> c6 = dhtml._Tree(6, c4)
    >>> c7 = dhtml._Tree(7, c2)
    >>> c8 = dhtml._Tree(8, c7)
    >>> c9 = dhtml._Tree(9, root)
    >>> c10 = dhtml._Tree(10, root)
    >>> all_labels = list(dhtml._nodes.keys())
    >>> all_labels
    [0, 1, 2, 3, 4, 5, 6, 7, 8, 9, 10]
    >>> ids = []
    >>> for child in root.children:
    ...    ids.append(child.label)
    >>> ids
    [1, 2, 9, 10]

.. _\_Tree.remove_child():

Testing remove_child().

    >>> root.remove_child(c9)
    >>> ids = []
    >>> for child in root.children:
    ...    ids.append(child.label)
    >>> ids
    [1, 2, 10]
    >>> all_labels = list(dhtml._nodes.keys())
    >>> all_labels
    [0, 1, 2, 3, 4, 5, 6, 7, 8, 10]
    >>> root.deletedlabels
    [(9, 0)]
    >>> c2.remove_child(c4)
    >>> c2.deletedlabels
    [(5, 4), (6, 4), (4, 2)]
    >>> all_labels = list(dhtml._nodes.keys())
    >>> all_labels
    [0, 1, 2, 3, 7, 8, 10]


.. _\_Tree.remove_all_children():

Testing remove_all_children().

    >>> root.remove_all_children()
    >>> root.children
    []
    >>> root.deletedlabels
    [(9, 0), (1, 0), (5, 4), (6, 4), (4, 2), (3, 2), (8, 7), (7, 2), (2, 0), (10, 0)]
    
.. _append() and remove():

.. _\_Tree.append_child():
.. _\_Tree.delete():

Unit tests for \_Tree.append() and \_Tree.delete() are to be done.

Testing append() and remove()
--------------------------------
    
    >>> dhtml._nodes = {}  # start from fresh
    >>> dhtml.append('first', label='1')
    ['div_42', 'first', ('id', 'dhtml_42_1')]
    >>> ids = list(dhtml._nodes.keys())
    >>> ids
    ['div_42', 'dhtml_42_1']
    >>> dhtml.append('second', label='2')
    ['div_42', 'second', ('id', 'dhtml_42_2')]
    >>> ids = list(dhtml._nodes.keys())
    >>> ids
    ['div_42', 'dhtml_42_2', 'dhtml_42_1']
    >>> dhtml.remove(1)   # list of parent, deleted_child
    ['div_42', 'dhtml_42_1']
    >>> ids = list(dhtml._nodes.keys()) # list of remaining nodes
    >>> ids
    ['div_42', 'dhtml_42_2']
    >>> dhtml._nodes['div_42'].deletedlabels # cleared internally
    []

.. _image():

Testing image()
------------------

Try creating an image with default values.
    >>> dhtml.image('foo.png') # doctest:+ELLIPSIS
    ['div_42', 'img', ('id', 'dhtml_42_')]
    [('dhtml_42_', 'width', '400'), ('dhtml_42_', 'src', 'foo.png...'), ('dhtml_42_', 'height', '400')]

.. _\_js_append_html():

Testing \_js_append_html()
--------------------------

to do.

.. _\_js_remove_html():

Testing \_js_remove_html()
--------------------------

to do.
