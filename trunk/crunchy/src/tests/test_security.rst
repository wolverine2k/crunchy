security.py tests
================================

security.py is a module which removes unwanted tags/attributes from html files.
It has the following functions that require testing:

1. remove_unwanted(): the main function, called by other modules.
2. __cleanup(): See http://effbot.org/zone/element-bits-and-pieces.htm
3. validate_image(): verifies that the file contents is consistent with an image
4. is_link_safe(): evaluate if <link> referring to style sheets appears to be safe
5. find_url(): combines relative url of "child" with base url of "parent"
6. open_local_file():   wrong name; need to fix
7. scan_for_unwanted(): scan for potentially unsafe strings.

0. Setting things up
--------------------

See how_to.rst_ for details.

.. _how_to.rst: how_to.rst


    >>> from src.interface import python_version, config, ElementTree, Element, SubElement
    >>> et = ElementTree.ElementTree
    >>> config.clear()
    >>> import src.tests.mocks as mocks
    >>> mocks.init()
    >>> page = mocks.Page()
    >>> import os
    >>> config['crunchy_base_dir'] = os.getcwd()
    >>> import src.security as security


We also need to define some mock functions and values.

    >>> def get_security_level(level):
    ...     return level
    >>> config['page_security_level'] = get_security_level
    >>> security_levels = ['trusted', 'display trusted', 'normal', 'display normal',
    ...                    'strict', 'display strict']

Finally, we will create some utility functions that we will use repeatedly.

    >>> def new_tree(add_to_head=None, add_to_body=None):
    ...    root = Element("html")
    ...    head = SubElement(root, "head")
    ...    title = SubElement(head, "title")
    ...    body = SubElement(root, "body")
    ...    body.text = "Crunchy is neat!"
    ...    if add_to_head is not None:
    ...       head.append(add_to_head)
    ...    if add_to_body is not None:
    ...       body.append(add_to_body)    
    ...    return ElementTree.ElementTree(root), ElementTree.tostring(root)
    >>>
    >>> def to_string(tree):
    ...    return ElementTree.tostring(tree.getroot())

1. Testing remove_unwanted()
-----------------------------

We first start with a totally acceptable tree, making sure that nothing is removed
and that the object identity is not changed in the process.

    >>> tree, tree_string = new_tree()
    >>> page.url = 'trusted'
    >>> cleaned_tree = security.remove_unwanted(tree, page)
    >>> cleaned_string = to_string(cleaned_tree)
    >>> tree_string == cleaned_string
    True
    >>> id(tree_string) != id(cleaned_string)
    True
    >>> id(tree) == id(cleaned_tree)
    True

Next, we add some javascript which should definitely be removed.

    >>> script = Element('script')
    >>> script.text = "nasty stuff"
    >>> bad_tree, bad_tree_string = new_tree(add_to_head=script)
    >>> 'script' in bad_tree_string
    True
    >>> cleaned_tree = security.remove_unwanted(bad_tree, page)
    >>> cleaned_string = to_string(cleaned_tree)
    >>> cleaned_string == tree_string
    True
    >>> cleaned_string != bad_tree_string # obvious, but we do not take any chances with tests.
    True

Next, we repeat this for all security levels.

    >>> for level in security_levels:
    ...    page.url = level
    ...    script = Element('script')
    ...    script.text = "nasty stuff"
    ...    bad_tree, bad_tree_string = new_tree(add_to_head=script)
    ...    if not 'script' in bad_tree_string:
    ...        print "javascript not inserted properly"
    ...    cleaned_tree = security.remove_unwanted(bad_tree, page)
    ...    cleaned_string = to_string(cleaned_tree)
    ...    if cleaned_string != tree_string:
    ...        print "Problem with removing unwanted stuff."
    ...    if cleaned_string == bad_tree_string:
    ...        print "Nothing was removed."



