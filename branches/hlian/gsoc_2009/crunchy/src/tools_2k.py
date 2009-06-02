import sys

'''tools_2k.py

This module contains various utility functions compatible with
Python 2.4+ (but not with Python 3.x).

The corresponding functions compatible with Python 3.x are to be found
in tools_3k.py
'''

def u_print(*args):
    '''u_print is short for unicode_print

    Given a list of objects, prints them to standard output. If an
    object is unicode, it is encoded to UTF-8. If an object is a bytes
    string, it must be in UTF-8 encoding. If an object is not a string
    at all, it is converted into its unicode representation.

    The resulting list of strings is concatenated and printed.'''

    # Make a copy so we can modify while enumerating.
    u_args = list(args)

    for i, arg in enumerate(args):
        if getattr(arg, 'decode', None):
            try:
                u_args[i] = arg.decode('utf8')
            except:
                print("Problem in u_print: argument already encoded:")
                print(repr(arg))

    args = u_args

    try:  # exceptions appear to be catched silently elsewhere
          # without this try/except block...
          # likely a problem with printing encoded args
        s = ''.join(unicode(arg) for arg in args)
        print(s)
    except:
        raise
        print("Problem in u_print: could not print args:")
        print(args)

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