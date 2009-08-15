# -*- coding: utf-8 -*-
'''
errors_3k.py

Handle errors produced while running Crunchy, as well as Python
tracebacks, displaying the result to the user in a friendly way.
At present, this is just a very basic module.  The "friendly" messages
will eventually be translated to other languages.
'''

import sys
import traceback

#import configuration
from src.interface import config, StringIO

from . import translation
_ = translation._

debug = False

def simplify_traceback(code=None, username=None):
    ''' inspired by simplifytraceback from the code module in the
    standard library.
    The first stack item because it is our own code; it is removed in
    the standard traceback in the code module.
    '''
    try:
        ex_type, value, trace = sys.exc_info()
        sys.last_type = ex_type
        sys.last_traceback = trace
        sys.last_value = value
    except:
        return "Internal error: could not retrieve traceback information."
    try:
        lineno = trace.tb_next.tb_lineno
    except:
        lineno = trace.tb_lineno
    if ex_type is SyntaxError:
        return simplify_syntax_error(code, ex_type, value, trace, lineno, username)
    if ex_type is SystemExit:
        value = "Your program exited.\n"

    tblist = traceback.extract_tb(trace)
    del tblist[:1]
    tb_list = traceback.format_list(tblist)
    if tb_list:
        tb_list.insert(0, "Traceback (most recent call last):\n")
    tb_list[len(tb_list):] = traceback.format_exception_only(ex_type, value)

    saved_tb_list = []
    for line in tb_list:
        saved_tb_list.append(line)

    if username and config[username]['friendly']:
        try:
            if code is not None:
                code_line = code.split('\n')[lineno - 1]
            else:
                try:
                    dummy_filename, dummy_line_number, dummy_function_name, \
                                    code_line = traceback.extract_tb(trace)[2]
                except:
                    code_line = None
            del tb_list[0]
            tb_list[0] = tb_list[0].replace('  File "Crunchy console", line',
                                   _("Error on line"))
            tb_list[0] = tb_list[0].replace(' File "User\'s code", line',
                                   _("Error on line"))
            tb_list[0] = tb_list[0].replace(', in <module>', ':')
            if code_line is not None:
                tb_list.insert(1, ">>> " + code_line + "\n")
            for index, line in enumerate(tb_list):
                if ' File "Crunchy console", line' in line:
                    tb_list[index] = line.replace(' File "Crunchy console", line',
                                        _("called by line"))
                if ', in <module>' in line:
                    tb_list[index] = line.replace(', in <module>', '')
        except:
            tb_list = saved_tb_list

    retval = StringIO()
    list(map(retval.write, tb_list))
    if ex_type is SystemExit:
        out = retval.getvalue().replace("Your program exited.",
                             _("Your program exited.") )
        return out

    if debug:
        if username:
            added_info = ("Crunchy debug::  In errors.simplify_traceback:\n"
                          "username = %s"%username + "friendly = " +
                                            str(config[username]['friendly']))
        else:
            added_info = ("Crunchy debug::  "
                          "In errors.simplify_traceback: username=%s\n"%username)
    else:
        added_info = ''
    return retval.getvalue() + added_info


def simplify_syntax_error(code, ex_type, value, trace, lineno, username):
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
    if username and config[username]['friendly']:# ignore that filename stuff!
        tb_list = traceback.format_exception_only(ex_type, value)[1:]
        tb_list.insert(0, "Error on line %s:\n"%lineno)
    else:
        tb_list = traceback.format_exception_only(ex_type, value)
    retval = StringIO()
    list(map(retval.write, tb_list))

    out = retval.getvalue().replace("Error on line",
                             _("Error on line") )
    return out

def simplify_doctest_error_message(msg):
    '''Simplifies doctest messages, assuming standard format.'''

    # new for Python 2.6
    #- Doctest now returns results as a named tuple for readability:
    # (0, 7) --> TestResults(failed=0, attempted=7)
    if "TestResults" in msg:
        msg = msg.replace("TestResults", '').replace("=", '')
        msg = msg.replace("failed", '').replace("attempted", '')
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
            summary = (_("Congratulations, your code passed all (%d) tests!")%total)
        elif failures == total:
            summary = (_("Your code failed all (%d) tests.")%total)
        else:
            summary = (_("Your code passed %s out of %s tests.")%(total-failures, total))

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
                elif line.startswith("Got"):
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