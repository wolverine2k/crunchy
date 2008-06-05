=================
security.py tests
=================

security.py is a module which removes unwanted tags/attributes from html files.
It has the following functions that require testing:

#. remove_unwanted_: the main function, called by other modules.
#. cleanup_: See http://effbot.org/zone/element-bits-and-pieces.htm
#. validate_image_: verifies that the file contents is consistent with an image
#. is_link_safe_: evaluate if <link> referring to style sheets appears to be safe
#. find_url_: combines relative url of "child" with base url of "parent"
#. open_local_file_:   wrong name; need to fix
#. scan_for_unwanted_: scan for potentially unsafe strings.

Setting things up
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

.. _remove_unwanted:

Testing remove_unwanted()
-----------------------------

We first start with a totally acceptable tree, making sure that nothing is removed
and that the object identity is not changed in the process.

    >>> tree, tree_string = new_tree()
    >>> print tree_string
    <html><head><title /></head><body>Crunchy is neat!</body></html>
    >>> page.url = 'trusted'
    >>> cleaned_tree = security.remove_unwanted(tree, page)
    >>> cleaned_string = to_string(cleaned_tree)
    >>> tree_string == cleaned_string
    True
    >>> id(tree_string) != id(cleaned_string)
    True
    >>> id(tree) == id(cleaned_tree)
    True

Note how we need to compare the "strings" - they are like an html page.
We will continue with more tests, comparing "strings" before and after the security purge.

For the next step, we add some javascript which should definitely be removed.

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


We now move to even more comprehensive tests.
We create a tree with all allowed attributes under 'strict' conditions.
We then clean up this tree.  Nothing should be removed.

    >>> div = Element('div')
    >>> page.url = 'strict'
    >>> allowed = security.allowed_attributes['strict']
    >>> for tag in allowed:
    ...     elem = SubElement(div, tag)
    ...     for attr in allowed[tag]:
    ...         elem.attrib[attr] = tag + '_' + attr   # just because...
    >>> strict_tree, strict_tree_string = new_tree(add_to_body=div)
    >>> cleaned_tree = security.remove_unwanted(strict_tree, page)
    >>> cleaned_string = to_string(cleaned_tree)
    >>> cleaned_string == strict_tree_string
    True

A tree created under 'display strict' conditions should yield the same result.

    >>> div = Element('div')
    >>> page.url = 'display strict'
    >>> allowed = security.allowed_attributes['display strict']
    >>> for tag in allowed:
    ...     elem = SubElement(div, tag)
    ...     for attr in allowed[tag]:
    ...         elem.attrib[attr] = tag + '_' + attr   # just because...
    >>> d_strict_tree, d_strict_tree_string = new_tree(add_to_body=div)
    >>> d_strict_tree_string == strict_tree_string
    True

Let's repeat this test with "normal" and "display normal".
First, with 'normal'.  Note that we can't validate images (so we'll skip the tag <img>)
nor can we validate <link>, and we only allow some specific values for <meta>.  
We will need to treat these separately later.

    >>> div = Element('div')
    >>> page.url = 'normal'
    >>> allowed = security.allowed_attributes['normal']
    >>> for tag in allowed:
    ...     if tag not in ['img', 'meta', 'link']:
    ...         elem = SubElement(div, tag)
    ...         for attr in allowed[tag]:
    ...            elem.attrib[attr] = tag + '_' + attr   # just because...
    >>> normal_tree, normal_tree_string = new_tree(add_to_body=div)
    >>> cleaned_normal_tree = security.remove_unwanted(normal_tree, page)
    >>> cleaned_normal_string = to_string(cleaned_normal_tree)
    >>> cleaned_normal_string == normal_tree_string
    True

Then the 'display normal' test which should yield the same result as "normal".

    >>> div = Element('div')
    >>> page.url = 'display normal'
    >>> allowed = security.allowed_attributes['display normal']
    >>> for tag in allowed:
    ...     if tag not in ['img', 'meta', 'link']:
    ...         elem = SubElement(div, tag)
    ...         for attr in allowed[tag]:
    ...             elem.attrib[attr] = tag + '_' + attr   # just because...
    >>> d_normal_tree, d_normal_tree_string = new_tree(add_to_body=div)
    >>> d_normal_tree_string == normal_tree_string
    True

We finally do the same for "trusted" and "display trusted".  The allowed content is
basically the same as for normal, except that we do not validate <img> nor <link>. 
Therefore, we can keep them in.

    >>> div = Element('div')
    >>> page.url = 'trusted'
    >>> allowed = security.allowed_attributes['trusted']
    >>> for tag in allowed:
    ...     if tag != 'meta':
    ...         elem = SubElement(div, tag)
    ...         for attr in allowed[tag]:
    ...            elem.attrib[attr] = tag + '_' + attr   # just because...
    >>> trusted_tree, trusted_tree_string = new_tree(add_to_body=div)
    >>> cleaned_trusted_tree = security.remove_unwanted(trusted_tree, page)
    >>> cleaned_trusted_string = to_string(cleaned_trusted_tree)
    >>> cleaned_trusted_string == trusted_tree_string
    True

Then the 'display trusted'

    >>> div = Element('div')
    >>> page.url = 'display trusted'
    >>> allowed = security.allowed_attributes['display trusted']
    >>> for tag in allowed:
    ...     if tag != 'meta':
    ...         elem = SubElement(div, tag)
    ...         for attr in allowed[tag]:
    ...             elem.attrib[attr] = tag + '_' + attr   # just because...
    >>> d_trusted_tree, d_trusted_tree_string = new_tree(add_to_body=div)
    >>> d_trusted_tree_string == trusted_tree_string
    True


Now, something more fun.  We should be able to clean our "trusted" tree to make it the
same as a "normal" one, by selecting a different security mode for the page.

    >>> trusted_tree_string == normal_tree_string  # they are not the same originally
    False
    >>> page.url = 'normal'
    >>> trusted_to_normal_tree = security.remove_unwanted(trusted_tree, page)
    >>> trusted_to_normal_string = to_string(trusted_to_normal_tree)
    >>> trusted_to_normal_string == normal_tree_string  # now, they should be the same
    True

Finally, let's do another comparison...  
We first create a "normal" tree with no <style> tag.

    >>> div = Element('div')
    >>> page.url = 'normal'
    >>> allowed = security.allowed_attributes['normal']
    >>> for tag in allowed:
    ...     if tag != 'style':
    ...         elem = SubElement(div, tag)
    ...         for attr in allowed[tag]:
    ...             elem.attrib[attr] = tag + '_' + attr   # just because...
    >>> new_normal_tree, new_normal_tree_string = new_tree(add_to_body=div)


    >>> new_normal_tree_string == strict_tree_string # originally different
    False
    >>> page.url = 'strict'
    >>> normal_to_strict_tree = security.remove_unwanted(new_normal_tree, page)
    >>> normal_to_strict_string = to_string(normal_to_strict_tree)
    >>> normal_to_strict_string == strict_tree_string  # now, they should be the same
    True

.. _cleanup:

Testing __cleanup()
-------------------

to do


.. _is_link_safe:

Testing is_link_safe()
----------------------

to do

.. _validate_image:

Testing validate_image()
------------------------

to do

.. _find_url:

Testing find_url()
------------------

to do

.. _open_local_file:

Testing open_local_file()
-------------------------

to do

.. _scan_for_unwanted:

Testing scan_for_unwanted()
---------------------------

to do
