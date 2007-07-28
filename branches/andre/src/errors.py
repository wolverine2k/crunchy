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

import configuration

def _(msg):  # dummy for now
    return msg

def simplify_traceback(code=None):
    ''' inspired by simplifytraceback from the code module in the
    standard library.
    The first stack item because it is our own code; it is removed in
    the standard traceback in the code module.
    '''
    ex_type, value, trace = sys.exc_info()
    sys.last_type = ex_type
    sys.last_traceback = trace
    sys.last_value = value
    try:
        lineno = trace.tb_next.tb_lineno
    except:
        lineno = trace.tb_lineno
    if ex_type is SyntaxError:
        return simplify_syntax_error(code, ex_type, value, trace, lineno)
    if ex_type is SystemExit:
        value = _("Your program tried to exit Crunchy.\n")
    if configuration.defaults.friendly:
        if code is not None:
            code_line = code.split('\n')[lineno - 1]
        else:
            try:
                dummy_filename, dummy_line_number, dummy_function_name, \
                                code_line = traceback.extract_tb(trace)[2]
            except:
                return _("Error on line %s:\n%s: %s\n")%(lineno,
                         ex_type.__name__, value)
        return _("Error on line %s:\n%s\n%s: %s\n")%(lineno, code_line,
                         ex_type.__name__, value)
    else:   # from InteractiveInterpreter showtraceback in module code.py
        tblist = traceback.extract_tb(trace)
        del tblist[:1]
        list = traceback.format_list(tblist)
        if list:
            list.insert(0, "Traceback (most recent call last):\n")
        list[len(list):] = traceback.format_exception_only(ex_type, value)
        retval = StringIO()
        map(retval.write, list)
        return retval.getvalue()

def simplify_syntax_error(code, ex_type, value, trace, lineno):
    """
    print out a syntax error
    closely based on showsyntaxerror from the code module
    in the standard library
    """
    filename = _("User's code")  # will most likely not be used
    # Work hard to stuff the correct filename in the exception
    try:
        msg, (filename, lineno, offset, line) = value
    except:
        # Not the format we expect; leave it alone
        pass
    else:
        # Stuff in the right filename
        value = SyntaxError(msg, (filename, lineno, offset, line))
        sys.last_value = value
    if configuration.defaults.friendly:  # ignore that filename stuff!
        list = traceback.format_exception_only(ex_type, value)[1:]
        list.insert(0, _("Error on line %s:\n"%lineno))
    else:
        list = traceback.format_exception_only(ex_type, value)
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