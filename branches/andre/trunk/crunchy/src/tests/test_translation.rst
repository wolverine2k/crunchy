translation.py tests
================================

Minimal test: making sure it imports properly.  This can help identify
imcompatibilities with various Python version (e.g. Python 2/3)

Unfortunately, depending on src.interface seems like a necessary evil.
src.translation imports u_print form src.interface, which in turn
imports src.translation, thereby creating a cyclic dependency and
precluding us from simply importing "src.translation". Unfortunately,
to compound this quirk of the Python module system with another quirk,
this only shows up when you run test_translation in relative
isolation: if another module gets to src.interface before us, this
never shows up. For the most accurate, test this doctest file with
"--include-only translation" passed to the test runner.

    >>> from src.interface import translation
