# -*- coding: utf-8 -*-
'''tools_3k.py

This module contains various utility functions compatible with
Python 3.x (but not with Python 2.x).

The corresponding functions compatible with Python 2.x are to be found
in tools_2k.py
'''

test_name = "André"

def exec_code(code, local_dict, source='', username=None): # tested via test_interface.rst
    #import crunchy.errors as errors   # prevent premature import
    import sys                    #
    try:
        exec(code, local_dict)
    except:
        if source is not None:
            #sys.stderr.write(errors.simplify_traceback(source, username=username))
            sys.stderr.write("Some traceback needs to appear here.")
        else:
            raise
