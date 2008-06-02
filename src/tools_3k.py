# -*- coding: utf-8 -*-
'''tools_3k.py

This module contains various utility functions compatible with
Python 3.x.

The corresponding functions compatible with Python 2.x are to be found
in tools.py
'''
import traceback
import sys
def u_print(*args):
    '''u_print is short for unicode_print
    
    Concatenate a series of string arguments
    (encoded in utf-8 usually) and prints
    out the resulting string.'''
    to_print = []
    for arg in args:
        to_print.append(arg)
    print(''.join(to_print))

def exec_code(code, local_dict, source="ignore"):
    try:
        exec(code, local_dict)
    except:
        showtraceback()

def showtraceback():
    """Display the exception that just occurred.

    We remove the first stack item because it is our own code.

    The output is written by self.write(), below.

    """
    try:
        type, value, tb = sys.exc_info()
        sys.last_type = type
        sys.last_value = value
        sys.last_traceback = tb
        tblist = traceback.extract_tb(tb)
        del tblist[:1]
        lines = traceback.format_list(tblist)
        if lines:
            lines.insert(0, "Traceback (most recent call last):\n")
        lines.extend(traceback.format_exception_only(type, value))
    finally:
        tblist = tb = None
    print(''.join(lines))