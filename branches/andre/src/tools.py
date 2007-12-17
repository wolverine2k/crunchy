'''tools.py

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
        to_print.append(arg.encode("utf-8"))
    print ''.join(to_print)

def exec_code(code, local_dict, source=''):
    import src.errors as errors   # prevent premature import
    import sys                    # 
    try:
        exec code in local_dict
    except:
        if source is not None:
            sys.stderr.write(errors.simplify_traceback(source))
        else:
            raise