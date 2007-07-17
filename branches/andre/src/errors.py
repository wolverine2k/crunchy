'''
errors.py

Handle errors produced while running Crunchy, as well as Python
tracebacks, displaying the result to the user in a friendly way.
At present, this is just a very basic module.  The "friendly" messages
will eventually be translated to other languages.
'''

import sys
import traceback
from StringIO import StringIO

def _(msg):  # dummy for now
    return msg

def simplify_traceback(code):
    ex_type, ex_val, ex_trace = sys.exc_info()
    if ex_type is SyntaxError:
        return simplify_syntax_error(code)
    ex_lineno = ex_trace.tb_next.tb_lineno
    if type is SystemExit:
        ex_value = _("Your program tried to exit Crunchy.")
    # needs to be made more robust to take care of \n embedded in strings
    ex_line = code.split('\n')[ex_lineno - 1]
    return _("Error on line %s:\n%s\n%s: %s\n")%(ex_lineno, ex_line, ex_type.__name__, ex_val)

def simplify_syntax_error(code):
    """
    print out a syntax error
    closely based on showsyntaxerror from the code module
    in the standard library
    """
    filename = _("User's code")
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

def simplify_doctest_error_message(msg):
    '''Simplifies doctest messages, assuming standard format.'''

    failures, total = eval( msg.split('\n')[-1])

    if failures:
        success = False
    else:
        success = True
    if total == 0:
        summary = _("There was no test to satisfy.")
    elif total == 1:
        if failures == 0:
            summary = _("Congratulations, your code passed the test!")
        else:
            summary = _("You code failed the test.")
    else:
        if failures == 0:
            summary = _("Congratulations, your code passed all (%d) tests!")%total
        elif failures == total:
            summary = _("Your code failed all (%d) tests.")%total
        else:
            summary = _("Your code failed %s out of %s tests.")%(failures, total)

    if failures == 0:
        return summary, success

    stars = "*"*70  # doctest prints this before each failed test
    failed = msg.split(stars)
    new_mesg=[summary]
    new_mesg.append("="*70)
    exception_found = False
    for fail in failed:
        if fail: # ignore empty lines
            lines = fail.split('\n')
            for line in lines[2:-2]:
                if line.startswith("Failed example:"):
                    new_mesg.append(_("The following example failed:"))
                elif line.startswith("Expected:"):
                    new_mesg.append(_("The expected result was:"))
                elif line.startswith("Got:"):
                    new_mesg.append(_("The result obtained was:"))
                elif line.startswith("Exception raised:"):
                    new_mesg.append(_("An exception was raised:"))
                    exception_found = True
                    break
                else:
                    new_mesg.append(line)
            new_mesg.append(lines[-2])
            new_mesg.append("-"*70)
    return '\n'.join(new_mesg), success