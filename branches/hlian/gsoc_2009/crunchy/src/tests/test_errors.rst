errors.py tests
===============


Setting things up
-----------------

    >>> import src.errors as errors
    >>> from src.errors import simplify_traceback

Here's some code with a syntax error.

    >>> code = "2 + "

Now we try to evaluate that code and calling ``simplify_traceback`` on
the resulting ``sys.exc_info()``:

    >>> try:
    ...     exec(code)
    ... except:
    ...     print(simplify_traceback(code, None))
      File "<string>", line 1
        2 +
           ^
    SyntaxError: unexpected EOF while parsing
    <BLANKLINE>

(TODO: test more code paths in errors.py.)
