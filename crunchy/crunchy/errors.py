# -*- coding: utf-8 -*-
'''
errors.py

Handle errors produced while running Crunchy, as well as Python
tracebacks, displaying the result to the user in a friendly way.
At present, it just dispatches blindly to the appropriate module which
is dependent on the Python version.
'''

from crunchy.interface import python_version

if python_version < 3:
    from errors_2k import simplify_doctest_error_message, simplify_syntax_error, simplify_traceback
else:
    from crunchy.errors_3k import simplify_doctest_error_message, simplify_syntax_error, simplify_traceback
