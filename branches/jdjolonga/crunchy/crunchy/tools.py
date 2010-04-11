# -*- coding: utf-8 -*-
'''tools.py

This module contains various utility functions and act as a gateway
to other modules to ensure compatibility with both Python 2.x and Python 3.x.

'''

import sys

# We can't import these from crunchy.interface because that would create a
# mutual dependency.
python_version = sys.version_info[0]  # name also defined for testing purpose
if python_version < 3:
    _bytes = str
    crunchy_unicode = unicode
    import tools_2k as specific_tools
else:
    _bytes = bytes
    crunchy_unicode = str
    import crunchy.tools_3k as specific_tools

def u_print(*args):
    '''u_print is short for unicode_print

    Given a list of objects, prints a concatenated Unicode string to
    standard output. If an object is a byte string, it will be decoded
    under UTF-8. Clients should avoid passing byte strings into
    u_print. If an object is not a string at all, it is converted into
    its unicode representation.

    Unicode representations of objects are concatenated and printed.'''

    print(u_join(*args))

def u_join(*args):
    '''u_print is short for unicode_join

    Given a list of objects, returns a concatenated Unicode string. If
    an object is a byte string, it will be decoded under UTF-8.
    Clients should avoid passing byte strings into u_join. If an object
    is not a string at all, it is converted into its unicode
    representation.

    This method mainly exists for doctest testing.'''

    # Make a copy so we can modify while enumerating.
    u_args = list(args)

    for i, arg in enumerate(args):
        if isinstance(arg, _bytes):
            try:
                u_args[i] = arg.decode('utf8')
            except UnicodeDecodeError:
                print("Problem in u_print: argument already encoded:")
                print(repr(arg))
                raise

    args = u_args
    try:  # exceptions appear to be catched silently elsewhere
          # without this try/except block...
          # likely a problem with printing encoded args
        s = ''.join(crunchy_unicode(arg) for arg in args)
        return s
    except:
        print("Problem in u_print: could not print args:")
        print(repr(args))
        raise

exec_code = specific_tools.exec_code

#def exec_code(code, local_dict, source='', username=None): # tested via test_interface.rst
#    import crunchy.errors as errors   # prevent premature import
#    import sys                    #
#    try:
#        exec(code, local_dict)
#    except:
#        if source is not None:
#            sys.stderr.write(errors.simplify_traceback(source, username=username))
#        else:
#            raise