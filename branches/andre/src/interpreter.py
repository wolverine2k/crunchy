import threading, sys
from code import InteractiveConsole, InteractiveInterpreter, softspace
import sys
import traceback
from codeop import CommandCompiler, compile_command

from StringIO import StringIO

from utilities import trim_empty_lines_from_end, log_session
import configuration
import errors

def _(msg):  # dummy for now
    return msg

class Interpreter(threading.Thread):
    """
    Run python source asynchronously
    """
    def __init__(self, code, channel, symbols = {}, doctest=False):
        threading.Thread.__init__(self)
        self.code = trim_empty_lines_from_end(code)
        self.channel = channel
        self.symbols = symbols
        self.doctest = doctest
        if self.doctest:
            self.doctest_out = StringIO()
            self.symbols['doctest_out'] = self.doctest_out

    def run(self):
        """run the code, redirecting stdout, stderr, stdin and
           returning the string representing the output
        """
        sys.stdin.register_thread(self.channel)
        sys.stdout.register_thread(self.channel)
        sys.stderr.register_thread(self.channel)
        try:
            try:
                self.ccode = compile(self.code, "User's code", 'exec')
            except:
                sys.stderr.write(errors.simplify_traceback(self.code))
                #traceback.print_exc()
                raise
            if not self.ccode:    #code does nothing
                return
            try:
                # logging the user input first, if required
                if self.channel in configuration.defaults.logging_uids:
                    vlam_type = configuration.defaults.logging_uids[self.channel][1]
                    if vlam_type == 'editor':
                        user_code = self.code.split("\n")
                        log_id = configuration.defaults.logging_uids[self.channel][0]
                        if user_code:
                            user_code = '\n'.join(user_code)
                            if not user_code.endswith('\n'):
                                user_code += '\n'
                        else:
                            user_code = _("# no code entered by user\n")
                        data = "<span class='stdin'>" + user_code + "</span>"
                        configuration.defaults.log[log_id].append(data)
                        log_session()
                exec self.ccode in self.symbols#, {}
                # note: previously, the "local" directory used for exec
                # was simply an empty directory.  However, this meant that
                # module names imported outside a function definition
                # were not available inside that function.  This is why
                # we have commented out the {} as a reminder; self.symbols
                # will be used for holding both global and local variables.
            #except SystemExit:
                #sys.stderr.write(errors.simplify_traceback(self.code))
                #traceback.print_exc()
            except:
                #print errors.simplify_traceback(self.code)
                sys.stderr.write(errors.simplify_traceback(self.code))
                #traceback.print_exc()
                #raise
        finally:
            if self.doctest:
                # attempting to log
                if self.channel in configuration.defaults.logging_uids:
                    code_lines = self.code.split("\n")
                    user_code = []
                    for line in code_lines:
                        # __teststring identifies the beginning of the code
                        # that is passed to a doctest (see vlam_doctest.py)
                        # This will have been appended to the user's code.
                        if line.startswith("__teststring"):
                            break
                        user_code.append(line)
                    log_id = configuration.defaults.logging_uids[self.channel][0]
                    if user_code:
                        user_code = '\n' + '\n'.join(user_code)
                        if not user_code.endswith('\n'):
                            user_code += '\n'
                    else:
                        user_code = _("# no code entered by user\n")
                    data = "<span class='stdin'>" + user_code + "</span>"
                    configuration.defaults.log[log_id].append(data)
                    log_session()
                # proceed with regular output
                if configuration.defaults.friendly:
                    message, success = errors.simplify_doctest_error_message(
                           self.doctest_out.getvalue())
                    if success:
                        sys.stdout.write(message)
                    else:
                        sys.stderr.write(message)
                else:
                    sys.stdout.write(self.doctest_out.getvalue())
            sys.stdin.unregister_thread()
            sys.stdout.unregister_thread()
            sys.stderr.unregister_thread()

def runcode(self, code):
    """Execute a code object.
    This is almost the same method as defined in
    InteractiveInterpreter.

    When an exception occurs, self.showtraceback() is called to
    display a traceback.  The original code was such that all
    exceptions were caught except SystemExit, which was reraised.
    Here we treat it the same as others.

    [From the original] A note about KeyboardInterrupt:
    this exception may occur elsewhere in this code, and may not always
    be caught.  The caller should be prepared to deal with it.

    """
    try:
        exec code in self.locals
# -- removed from the original:
##        except SystemExit:
##            raise
    except:
        #errors.simplify_traceback(code)
        self.showtraceback()
    else:
        if softspace(sys.stdout, 0):
            print

InteractiveInterpreter.runcode = runcode

class Borg(object):
    '''Borg Idiom, from the Python Cookbook, 2nd Edition, p:273

    Derive a class form this; all instances of that class will share the
    same state, provided that they don't override __new__; otherwise,
    remember to use Borg.__new__ within the overriden class.
    '''
    _shared_state = {}
    def __new__(cls, *a, **k):
        obj = object.__new__(cls, *a, **k)
        obj.__dict__ = cls._shared_state
        return obj

# The following BorgConsole class is defined such that all instances
# of an interpreter on a same html page share the same environment.
# However, for reasons that are not clear and that need to be explained
# (but do present the desired behaviour!!!!), request for new
# pages are such that interpreters on new pages start with fresh
# environments.

class SingleConsole(InteractiveConsole):
    '''SingleConsole are isolated one from another'''
    def __init__(self, locals={}):
        InteractiveConsole.__init__(self, locals)

class BorgConsole(Borg, SingleConsole):
    '''Every BorgConsole share a common state'''
    def __init__(self, locals={}):
        SingleConsole.__init__(self, locals)

##try:
##    from IPython.Shell import IPShellEmbed
##    from IPython.Release import version as IPythonVersion
##
##    class IPythonShell(IPShellEmbed):
##        def __init__(self, locals={}):
##            IPShellEmbed.__init__(self, ['-colors', 'NoColor'],
##                banner="Crunchy IPython (Python version %s, IPython version %s)"%(
##                           sys.version.split(" ")[0], IPythonVersion),
##                                        user_ns = locals)
##except:
##    pass  # for now