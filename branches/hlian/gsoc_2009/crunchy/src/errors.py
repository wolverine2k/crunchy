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
        return u"Internal error: could not retrieve traceback information."
    try:
        lineno = trace.tb_next.tb_lineno
    except:
        lineno = trace.tb_lineno
    if ex_type is SyntaxError:
        return simplify_syntax_error(code, ex_type, value, trace, lineno, username)
    if ex_type is SystemExit:
        value = u"Your program exited.\n"

    tblist = traceback.extract_tb(trace)
    del tblist[:1]
    tb_list = traceback.format_list(tblist)
    if tb_list:
        tb_list.insert(0, u"Traceback (most recent call last):\n")
    tb_list[len(tb_list):] = traceback.format_exception_only(ex_type, value)

    saved_tb_list = []
    for line in tb_list:
        saved_tb_list.append(line)

    if username and config[username]['friendly']:
        try:
            if code is not None:
                code_line = code.split(u'\n')[lineno - 1]
            else:
                try:
                    dummy_filename, dummy_line_number, dummy_function_name, \
                                    code_line = traceback.extract_tb(trace)[2]
                except:
                    code_line = None
            del tb_list[0]
            tb_list[0] = tb_list[0].replace(u'  File "Crunchy console", line',
                                   _(u"Error on line"))
            tb_list[0] = tb_list[0].replace(u' File "User\'s code", line',
                                   _(u"Error on line"))
            tb_list[0] = tb_list[0].replace(u', in <module>', u':')
            if code_line is not None:
                tb_list.insert(1, u">>> " + code_line + u"\n")
            for index, line in enumerate(tb_list):
                if u' File "Crunchy console", line' in line:
                    tb_list[index] = line.replace(u' File "Crunchy console", line',
                                        _(u"called by line"))
                if u', in <module>' in line:
                    tb_list[index] = line.replace(u', in <module>', u'')
        except:
            tb_list = saved_tb_list

    retval = StringIO()
    list(map(retval.write, tb_list))
    if ex_type is SystemExit:
        out = retval.getvalue().replace(u"Your program exited.",
                             _(u"Your program exited.") )
        return out

    if debug:
        added_info = u'Crunchy debug::  In errors.simplify_traceback:'
        if username:
            info = (username, config[username]['friendly'])
            added_info += u'\nusername = %s friendly = %s' % info
        else:
            added_info += u' username=%s\n' % username
    else:
        added_info = u''
    return retval.getvalue() + added_info


def simplify_syntax_error(code, ex_type, value, trace, lineno, username):
    """
    print out a syntax error
    closely based on showsyntaxerror from the code module
    in the standard library
    """
    filename = _(u"User's code")  # will most likely not be used
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
        excs = traceback.format_exception_only(ex_type, value)[1:]
        excs.insert(0, u"Error on line %s:\n" % lineno)
    else:
        excs = traceback.format_exception_only(ex_type, value)
    retval = StringIO()
    list(map(retval.write, excs))

    out = retval.getvalue().replace(u"Error on line",
                             _(u"Error on line") )
    return out

def simplify_doctest_error_message(msg):
    '''Simplifies doctest messages, assuming standard format.'''

    # new for Python 2.6
    #- Doctest now returns results as a named tuple for readability:
    # (0, 7) --> TestResults(failed=0, attempted=7)
    if u"TestResults" in msg:
        msg = msg.replace(u"TestResults", u'').replace(u"=", u'')
        msg = msg.replace(u"failed", u'').replace(u"attempted", u'')
    failures, total = eval( msg.split(u'\n')[-1])

    if failures:
        success = False
    else:
        success = True
    if total == 0:
        summary = _(u"There was no test to satisfy.")
    elif total == 1:
        if failures == 0:
            summary = _(u"Congratulations, your code passed the test!")
        else:
            summary = _(u"You code failed the test.")
    else:
        if failures == 0:
            summary = (_(u"Congratulations, your code passed all (%d) tests!")%total)
        elif failures == total:
            summary = (_(u"Your code failed all (%d) tests.")%total)
        else:
            summary = (_(u"Your code passed %s out of %s tests.")%(total-failures, total))

    if failures == 0:
        return summary, success

    stars = u"*" * 70 # doctest prints this before each failed test
    failed = msg.split(stars)
    new_mesg=[summary]
    new_mesg.append(u"=" * 70)
    exception_found = False
    for fail in failed:
        if fail: # ignore empty lines
            lines = fail.split(u'\n')
            for line in lines[2:-2]:
                if line.startswith(u"Failed example:"):
                    new_mesg.append(_(u"The following example failed:"))
                elif line.startswith(u"Expected:"):
                    new_mesg.append(_(u"The expected result was:"))
                elif line.startswith(u"Got"):
                    new_mesg.append(_(u"The result obtained was:"))
                elif line.startswith(u"Exception raised:"):
                    new_mesg.append(_(u"An exception was raised:"))
                    exception_found = True
                    break
                else:
                    new_mesg.append(line)
            new_mesg.append(lines[-2])
            new_mesg.append(u"-" * 70)
    return u'\n'.join(new_mesg), success
