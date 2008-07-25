# -*- coding: utf-8 -*-
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

#import configuration
from src.interface import config

import translation
_ = translation._

def simplify_traceback(code=None):
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
        return simplify_syntax_error(code, ex_type, value, trace, lineno)
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

    if config['friendly']:#configuration.defaults.friendly:
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
                                   _(u"Error on line"))
            tb_list[0] = tb_list[0].replace(' File "User\'s code", line',
                                   _(u"Error on line"))
            tb_list[0] = tb_list[0].replace(', in <module>', ':')
            if code_line is not None:
                tb_list.insert(1, ">>> " + code_line + "\n")
            for index, line in enumerate(tb_list):
                if ' File "Crunchy console", line' in line:
                    tb_list[index] = line.replace(' File "Crunchy console", line',
                                        _(u"called by line"))
                if ', in <module>' in line:
                    tb_list[index] = line.replace(', in <module>', '')
        except:
            tb_list = saved_tb_list

    retval = StringIO()
    map(retval.write, tb_list)
    if ex_type is SystemExit:
        out = retval.getvalue().replace("Your program exited.",
                             _(u"Your program exited.") )
        return out.encode("utf-8")
    return retval.getvalue().encode("utf-8")


def simplify_syntax_error(code, ex_type, value, trace, lineno):
    """
    print out a syntax error
    closely based on showsyntaxerror from the code module
    in the standard library
    """
    filename = _(u"User's code").encode("utf-8")  # will most likely not be used
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
    if config['friendly']:#configuration.defaults.friendly:  # ignore that filename stuff!
        list = traceback.format_exception_only(ex_type, value)[1:]
        list.insert(0, "Error on line %s:\n"%lineno)
    else:
        list = traceback.format_exception_only(ex_type, value)
    retval = StringIO()
    map(retval.write, list)

    out = retval.getvalue().replace("Error on line",
                             _(u"Error on line") )
    return out.encode("utf-8")

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
        summary = _(u"There was no test to satisfy.").encode("utf-8")
    elif total == 1:
        if failures == 0:
            summary = _(u"Congratulations, your code passed the test!").encode("utf-8")
        else:
            summary = _(u"You code failed the test.").encode("utf-8")
    else:
        if failures == 0:
            summary = (_(u"Congratulations, your code passed all (%d) tests!")%total).encode("utf-8")
        elif failures == total:
            summary = (_(u"Your code failed all (%d) tests.")%total).encode("utf-8")
        else:
            summary = (_(u"Your code passed %s out of %s tests.")%(total-failures, total)).encode("utf-8")

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
                    new_mesg.append(_(u"The following example failed:").encode("utf-8"))
                elif line.startswith("Expected:"):
                    new_mesg.append(_(u"The expected result was:").encode("utf-8"))
                elif line.startswith("Got"):
                    new_mesg.append(_(u"The result obtained was:").encode("utf-8"))
                elif line.startswith("Exception raised:"):
                    new_mesg.append(_(u"An exception was raised:").encode("utf-8"))
                    exception_found = True
                    break
                else:
                    new_mesg.append(line)
            new_mesg.append(lines[-2])
            new_mesg.append("-"*70)
    return '\n'.join(new_mesg), success