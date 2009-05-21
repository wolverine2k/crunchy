'''tools_2k.py

This module contains various utility functions compatible with
Python 2.4+ (but not with Python 3.x).

The corresponding functions compatible with Python 3.x are to be found
in tools_3k.py
'''

def u_print(*args):
    '''u_print is short for unicode_print

    Encodes a series of string arguments in utf-8, concatenate them
    and prints out the resulting string.'''
    to_print = []
    for arg in args:
        try:
            to_print.append(arg.encode("utf-8"))
        except:
            to_print.append(str(arg))
    try:  # exceptions appear to be catched silently elsewhere
          # without this try/except block...
          # likely a problem with printing encoded args
        print ''.join(to_print)
    except:
        print "PROBLEM in u_print; could not print encoded args:"
        print args

def exec_code(code, local_dict, source='', username=None): # tested via test_interface.rst
    import src.errors as errors   # prevent premature import
    import sys                    #
    try:
        exec code in local_dict
    except:
        if source is not None:
            sys.stderr.write(errors.simplify_traceback(source, username=username))
        else:
            raise