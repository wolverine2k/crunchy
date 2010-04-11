tools.py tests
==================

Note: this file is encoded in utf-8.

tools.py contains various functions whose definitions are dependent on the
Python version being used, but provided to the user in a totally transparent way.

    >>> import src.tools as tools
    >>> if tools.python_version < 3:
    ...     import src.tools_2k as tools_specific
    ... else: 
    ...     import src.tools_3k as tools_specific

Testing u_print and u_join
---------------------------

In Python 3, "print" is now a function. To provide a transparent way
of printing, we have defined a function called u_print() which is
meant to print a series of arguments.

Given that doctest converts from bytes to Unicode haphazardly and that
Python 3 makes writing raw bytes to standard output moderately
convoluted, we made u_print() into a bare wrapper around u_join() and
here we test u_join() instead of u_print().

    >>> to_print = tools_specific.test_name
    >>> tools.u_join(to_print) == to_print
    True
    >>> tools.u_print("a", "b", "c")
    abc


