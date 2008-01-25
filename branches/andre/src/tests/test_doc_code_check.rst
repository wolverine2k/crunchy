doc_code_check.py tests
================================

Not tested successfully with Python 2.4, 2.5, 3.0a1 and 3.0a2


It contains one method that need to be tested:
1. register()

0. Setting things up
--------------------

See how_to.rst_ for details.

.. _how_to.rst: how_to.rst

   >>> from src.interface import plugin
   >>> plugin.clear()
   >>> import src.plugins.doc_code_check as dcc


1. Testing compare()
--------------------

compare() is a function used to compare two strings.  In order to test
it, we need to set up a few cases.

    >>> test1 = """This is a short test."""
    >>> test2 = """This is a short test too."""
    >>> test3 = """This is a much longer test
    ... that spans multiple lines
    ... with some meaningless dribble."""
    >>> test4 = test3 + " Yes, it is."
    >>> print(dcc.compare(test1, test1))
    Checked!
    >>> print(dcc.compare(test1, test2))
    - This is a short test.
    + This is a short test too.
    ?                     ++++
    <BLANKLINE>
    >>> print(dcc.compare(test3, test3))
    Checked!
    >>> print(dcc.compare(test3, test4))
      This is a much longer test
      that spans multiple lines
    - with some meaningless dribble.
    + with some meaningless dribble. Yes, it is.
    ?                               ++++++++++++
    <BLANKLINE>


2. Testing run_sample()
-----------------------

First, we create a simple example.

    >>> dcc.code_setups['1'] = "a = 1"
    >>> dcc.code_samples['1'] = "print(a)"
    >>> dcc.expected_outputs['1'] = "1\n"
    >>> dcc.run_sample('1')
    Checked!

A second example with no setup code.

    >>> dcc.code_samples['2'] = "print(1)"
    >>> dcc.expected_outputs['2'] = "1\n"
    >>> dcc.run_sample('2')
    Checked!



1. Testing register()
---------------------

# Test - check that the two http_handlers have been registered
