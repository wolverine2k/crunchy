# -*- coding: utf-8 -*-
'''tools_3k.py

This module contains various utility functions compatible with
Python 3.x.

The corresponding functions compatible with Python 2.x are to be found
in tools.py
'''

def u_print(*args):
    '''u_print is short for unicode_print
    
    Concatenate a series of arguments (encoded in utf-8 usually) and prints
    out the resulting string.'''
    to_print = []
    for arg in args:
        to_print.append(arg)
    print(''.join(to_print))
