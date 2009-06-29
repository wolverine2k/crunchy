interface.py tests
==================

Note: this file is encoded in utf-8.


interface.py contains various functions whose definitions are dependent on the
Python version being used, but provided to the user in a totally transparent way.

Testing u_print
---------------

Whereas the original Python used ascii as the default encoding,
Python 3k is using utf-8 as a default.  One of the many consequences is that
unicode strings are not specified with a prefix "u".  Thus, whereas in the
original Python, one might have written u"André", in Python 3k the same
string is simply written "André".

Furthermore, in Python 3k, "print" is now a function.   To provide a
transparent way of printing, we have defined a function called u_print()
which is meant to print a series of arguments.

    >>> import src.interface as interface
    >>> interface.config.clear()
    >>> interface.plugin.clear()
    >>> from os import getcwd
    >>> interface.config['crunchy_base_dir'] = getcwd()
    >>> if interface.python_version < 3:
    ...     to_print = "André".decode('utf-8')
    ... else:
    ...     to_print = "André"

Given that doctest converts from bytes to Unicode haphazardly and that
Python 3 makes writing raw bytes to standard output moderately
convoluted, we made u_print() into a bare wrapper around u_join() and
here we test u_join() instead of u_print().

    >>> interface.u_join(to_print) == to_print
    True
    >>> interface.u_print("a", "b", "c")
    abc

Testing ElementTree and friends
-------------------------------

The following is incomplete.

    >>> elem = interface.Element("p")
    >>> elem.attrib['class'] = 'crunchy'
    >>> elem.text = "This is a neat sentence."
    >>> to_print = interface.tostring(elem)
    >>> if interface.python_version < 3:
    ...     print(type(to_print) == unicode)
    ... else:
    ...     print(type(to_print) == str)
    True
    >>> interface.u_print(to_print)
    <p class="crunchy">This is a neat sentence.</p>

We create a fake html file
    >>> html_content = """<!DOCTYPE html PUBLIC "-//W3C//DTD XHTML 1.0 Strict//EN"
    ... "http://www.w3.org/TR/xhtml1/DTD/xhtml1-strict.dtd">
    ... <html>
    ... <head>
    ... <title>Crunchy fun</title>
    ... </head>
    ... <body>
    ... <p>This is some text.</p>
    ... </body>
    ... </html>"""
    >>> fake_file = interface.StringIO()
    >>> dummy = fake_file.write(html_content) # return value in Py3k
    >>> dummy = fake_file.seek(0)  # return value in Py3k
    >>> tree = interface.parse(fake_file)

Testing exec_code()
-------------------

Whereas exec used to be a statement, in Python 3000 it is now a function.
So, just like for print, we need to give a transparent access to the right version.

    >>> def double(n):
    ...     return 2*n
    ...
    >>> locals = {'double': double, 'interface': interface}
    >>> test_code = "a = double(21)\ninterface.u_print(str(a))"
    >>> interface.exec_code(test_code, locals)
    42

