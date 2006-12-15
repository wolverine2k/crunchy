"""
custom printing out of tracebacks to make them easier to understand
"""

import sys
import traceback
from StringIO import StringIO

from translation import _

def get_traceback(code):
    ex_type, ex_val, ex_trace = sys.exc_info()
    ex_lineno = ex_trace.tb_next.tb_lineno
    ex_line = code.splitlines(True)[ex_lineno - 1]
    return _("Error on line %s:\n%s%s\n")%(ex_lineno, ex_line, ex_val)

        
def get_syntax_error(code):
    """
    print out a syntax error
    closely based on showsyntaxerror from the code module
    in the standard library
    """
    filename = "crunchy_exec"
    type, value, sys.last_traceback = sys.exc_info()
    sys.last_type = type
    sys.last_value = value
    if filename and type is SyntaxError:
        # Work hard to stuff the correct filename in the exception
        try:
            msg, (dummy_filename, lineno, offset, line) = value
        except:
            # Not the format we expect; leave it alone
            pass
        else:
            # Stuff in the right filename
            value = SyntaxError(msg, (filename, lineno, offset, line))
            sys.last_value = value
    list = traceback.format_exception_only(type, value)
    retval = StringIO()
    map(retval.write, list)
    return retval.getvalue()
