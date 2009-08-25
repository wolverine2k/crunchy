user_markup.py tests
================================

user_markup.py has has the following functions that require testing:

1. `register()`_
#. `custom_vlam()`_
#. `add_option()`_
#. `remove_option()`_
#. `replace()`_

0. Setting things up
--------------------

    >>> from src.interface import plugin, config, Element, tostring
    >>> plugin.clear()
    >>> config.clear()
    >>> import src.plugins.user_markup as user_markup
    >>> import src.tests.mocks as mocks
    >>> mocks.init()
    >>> def repeat_args(*args):
    ...      for arg in args:
    ...          print(arg)
    >>>


.. _`register()`:

Testing register()
----------------------

    >>> user_markup.register()
    >>> print(mocks.registered_preprocess_page) #doctest: +ELLIPSIS
    {'pre': <function modify_vlam at ...>}
    >>> print(mocks.registered_final_tag_handlers) #doctest: +ELLIPSIS
    {'pre': <function custom_vlam at ...>}


.. _`custom_vlam()`:

Testing custom_vlam()
--------------------------

First, no markup specified.

    >>> page = mocks.Page(username='Crunchy')
    >>> page.pre = Element("pre")
    >>> config['Crunchy'] = {}
    >>> config['Crunchy']['no_markup'] = None
    >>> config['Crunchy']['modify_markup'] = False
    >>> user_markup.custom_vlam(page, page.pre, '42')
    >>> print(tostring(page.pre).replace('>', '>\n'))
    <pre />
    <BLANKLINE>

Next, some silly markup; we can reuse the same page since it still
has no markup.

    >>> config['Crunchy']['no_markup'] = "silly"
    >>> page.handlers3["pre"] = {}
    >>> page.handlers3["pre"]["title"] = {}
    >>> page.handlers3["pre"]["title"]["silly"] = repeat_args # fake handler
    >>> user_markup.custom_vlam(page, page.pre, '42') #doctest: +ELLIPSIS
    <src.tests.mocks.Page object at ...>
    <Element 'pre' at ...>
    42
    >>> print(tostring(page.pre).replace('>', '>\n'))
    <pre title="silly" />
    <BLANKLINE>

Since some markup options are case sensitive, make sure that they
are handled properly.

    >>> page = mocks.Page(username='Crunchy')
    >>> page.pre = Element("pre")
    >>> config['Crunchy']['no_markup'] = "Parrots"
    >>> page.handlers3["pre"] = {}
    >>> page.handlers3["pre"]["title"] = {}
    >>> page.handlers3["pre"]["title"]["Parrots"] = repeat_args # fake handler
    >>> user_markup.custom_vlam(page, page.pre, '42') #doctest: +ELLIPSIS
    <src.tests.mocks.Page object at ...>
    <Element 'pre' at ...>
    42
    >>> print(tostring(page.pre).replace('>', '>\n'))
    <pre title="Parrots" />
    <BLANKLINE>

.. _`add_option()`:

Testing add_option()
---------------------

    >>> test_vlam = "silly string"
    >>> test_vlam = user_markup.add_option(test_vlam, ['modified'])
    >>> print(test_vlam)
    silly string modified

.. _`remove_option()`:

Testing remove_option()
---------------------

    >>> test_vlam = "silly string"
    >>> test_vlam = user_markup.remove_option(test_vlam, ['not here'])
    >>> print(test_vlam)
    silly string
    >>> test_vlam = user_markup.remove_option(test_vlam, ['string'])
    >>> print(test_vlam)
    silly

.. _`replace()`:

Testing replace()
---------------------

    >>> test_vlam = "silly string"
    >>> test_vlam = user_markup.replace(test_vlam, ['silly', 'clever'])
    >>> print(test_vlam)
    clever string
    >>> test_vlam = user_markup.replace(test_vlam, ['not there', 'ok'])
    >>> print(test_vlam)
    clever string


Testing modify_vlam()
----------------------

Let's define some rules that we will use. We define the rules first just
to make sure that they are ignored when appropriate.

    >>> config['Crunchy']['_modification_rules'] = [
    ...  ['replace', 'two', 'four'],
    ...  ['remove_option', 'one'],
    ...  ['add_option', 'five']]
    >>>

    >>> elem1 = Element("pre")
    >>> elem2 = Element("pre", title="one two three")
    >>> print(elem1.attrib)
    {}
    >>> len(elem2.attrib)
    1
    >>> print(elem2.attrib['title'])
    one two three

First we test with combinations that do nothing, ignoring any pre-defined rules.

    >>> config['Crunchy']['modify_markup'] = False
    >>> user_markup.modify_vlam(page, elem2, 'dummy')
    >>> config['Crunchy']['modify_markup'] = True
    >>> user_markup.modify_vlam(page, elem1, 'dummy')
    >>> print(elem1.attrib)
    {}
    >>> len(elem2.attrib)
    1
    >>> print(elem2.attrib['title'])
    one two three

 Now, we apply the rules so as to make real changes.

    >>> user_markup.modify_vlam(page, elem2, 'dummy')
    >>> len(elem2.attrib)
    1
    >>> print(elem2.attrib['title'])
    four three five
