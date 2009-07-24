
import inspect
import threading, sys
import sys
import traceback
from codeop import CommandCompiler, compile_command
try:
    import ctypes
    ctypes_available = True
except:
    ctypes_available = False

from src.interface import StringIO, exec_code, translate, config, plugin, names, u_print
config['ctypes_available'] = ctypes_available

from src.utilities import trim_empty_lines_from_end, log_session
import src.errors as errors

_ = translate['_']

# The following function and class are taken from
# http://aspn.activestate.com/ASPN/Cookbook/Python/Recipe/496960
# but modified to behave nicely if ctypes is not present
def _async_raise(tid, excobj):
    if not ctypes_available:
        return      # exit nicely of ctypes isn't available
    res = ctypes.pythonapi.PyThreadState_SetAsyncExc(tid, ctypes.py_object(excobj))
    if res == 0:
        raise ValueError("nonexistent thread id")
    elif res > 1:
        # """if it returns a number greater than one, you're in trouble,
        # and you should call it again with exc=NULL to revert the effect"""
        ctypes.pythonapi.PyThreadState_SetAsyncExc(tid, 0)
        raise SystemError("PyThreadState_SetAsyncExc failed")

class KillableThread(threading.Thread):
    def raise_exc(self, excobj):
        assert self.isAlive(), "thread must be started"
        for tid, tobj in threading._active.items():
            if tobj is self:
                _async_raise(tid, excobj)
                return

        # the thread was alive when we entered the loop, but was not found
        # in the dict, hence it must have been already terminated. should we raise
        # an exception here? silently ignore?

    def terminate(self):
        # must raise the SystemExit type, instead of a SystemExit() instance
        # due to a bug in PyThreadState_SetAsyncExc
        self.raise_exc(KeyboardInterrupt)

class Interpreter(KillableThread):
    """
    Run python source asynchronously
    """
    def __init__(self, code, channel, symbols = None, doctest=False,
                 username=None):
        threading.Thread.__init__(self)
        self.code = trim_empty_lines_from_end(code) + "\n"
        # the extra new line character at the end above prevents a syntax error
        # if the last line is a comment.
        self.channel = channel
        if username is not None:
            self.username = username
            self.friendly = config[self.username]['friendly']
        else:
            try:
                pageid = self.channel.split("_")[0]
                self.username = names[pageid]
                self.friendly = config[self.username]['friendly']
            except:
                self.friendly = False
                print ("Exception raised in Interpreter.init(); channel = %s" %
                                                                    self.channel)
                try:
                    u_print("username = ", self.username)
                except:
                    print("username not defined...")
                    self.username = None
                try:
                    u_print("pageid in names: ", self.channel.split("_")[0] in names)
                except:
                    pass

        self.symbols = {}
        if symbols is not None:
            self.symbols.update(symbols)
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
                try:
                    if self.friendly:
                        sys.stderr.write(errors.simplify_traceback(self.code, self.username))
                    else:
                        traceback.print_exc()
                    return
                except:
                    sys.stderr.write("Recovering from internal error in Interpreter.run()")
                    sys.stderr.write("self.channel =%s"%self.channel)
                    return
            if not self.ccode:    #code does nothing
                return
            try:
                # logging the user input first, if required
                if self.username and self.channel in config[self.username]['logging_uids']:
                    vlam_type = config[self.username]['logging_uids'][self.channel][1]
                    if vlam_type == 'editor':
                        user_code = self.code.split("\n")
                        log_id = config[self.username]['logging_uids'][self.channel][0]
                        if user_code:
                            user_code = '\n'.join(user_code)
                            if not user_code.endswith('\n'):
                                user_code += '\n'
                        else:
                            user_code = _("# no code entered by user\n")
                        data = "<span class='stdin'>" + user_code + "</span>"
                        config[self.username]['log'][log_id].append(data)
                        log_session(username)
                exec_code(self.ccode, self.symbols, source=None,
                          username=self.username)
                #exec self.ccode in self.symbols#, {}
                # note: previously, the "local" directory used for exec
                # was simply an empty directory.  However, this meant that
                # module names imported outside a function definition
                # were not available inside that function.  This is why
                # we have commented out the {} as a reminder; self.symbols
                # will be used for holding both global and local variables.
            except:
                try:
                    if self.friendly:
                        sys.stderr.write(errors.simplify_traceback(self.code, self.username))
                    else:
                        traceback.print_exc()
                except:
                    sys.stderr.write("Recovering from internal error in Interpreter.run()")
                    sys.stderr.write(".. after trying to call exec_code.")
                    sys.stderr.write("self.channel = %s"%self.channel)
        finally:
            if self.doctest:
                # attempting to log
                if self.username and self.channel in config[self.username]['logging_uids']:
                    code_lines = self.code.split("\n")
                    user_code = []
                    for line in code_lines:
                        # __teststring identifies the beginning of the code
                        # that is passed to a doctest (see vlam_doctest.py)
                        # This will have been appended to the user's code.
                        if line.startswith("__teststring"):
                            break
                        user_code.append(line)
                    log_id = config[self.username]['logging_uids'][self.channel][0]
                    if user_code:
                        user_code = '\n' + '\n'.join(user_code)
                        if not user_code.endswith('\n'):
                            user_code += '\n'
                    else:
                        user_code = _("# no code entered by user\n")
                    # separating each attempts
                    user_code = "\n" + "- "*25 + "\n" + user_code

                    data = "<span class='stdin'>" + user_code + "</span>"
                    config[self.username]['log'][log_id].append(data)
                    log_session(self.username)
                # proceed with regular output
                if self.friendly:
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

#=======Begin modified code
# The following is a modified version of code.py that is found in
# Pythons's standard library.  We leave much of the original
# code and comments in this.
#======
# Inspired by similar code by Jeff Epler and Fredrik Lundh.

def softspace(file, newvalue):
    oldvalue = 0
    try:
        oldvalue = file.softspace
    except AttributeError:
        pass
    try:
        file.softspace = newvalue
    except (AttributeError, TypeError):
        # "attribute-less object" or "read-only attributes"
        pass
    return oldvalue

##Crunchy: derived this class from object, rather than using old-style
class InteractiveInterpreter(object):
    """Base class for InteractiveConsole.

    This class deals with parsing and interpreter state (the user's
    namespace); it doesn't deal with input buffering or prompting or
    input file naming (the filename is always passed in explicitly).

    """

    def __init__(self, locals=None, username=None):
        """
        The optional 'locals' argument specifies the dictionary in
        which code will be executed; it defaults to a newly created
        dictionary with key "__name__" set to "__console__" and key
        "__doc__" set to None.

        """

        if locals is None:
            locals = {"__name__": "__console__", "__doc__": None}
        self.locals = locals
        self.username = username
        if username is not None:
            self.locals.update(config[username]['symbols'])
            #print _("Hello %s ! "% username)
            print('')
        self.compile = CommandCompiler()

    def runsource(self, source, filename="User's code", symbol="single"):
        """Compile and run some source in the interpreter.

        Arguments are as for compile_command().

        One several things can happen:

        1) The input is incorrect; compile_command() raised an
        exception (SyntaxError or OverflowError).  A syntax traceback
        will be printed by calling the showsyntaxerror() method.
            ##Crunchy: or calling errors.simplify_syntax_error()

        2) The input is incomplete, and more input is required;
        compile_command() returned None.  Nothing happens.

        3) The input is complete; compile_command() returned a code
        object.  The code is executed by calling self.runcode() (which
        also handles run-time exceptions).

        The return value is True in case 2, False in the other cases
        (unless an exception is raised).  The return value can be used to
        decide whether to use sys.ps1 or sys.ps2 to prompt the next
        line.
        """
        try:
            code = self.compile(source, filename, symbol)
        except (OverflowError, SyntaxError, ValueError):
            sys.stderr.write(errors.simplify_traceback(source, self.username))
            return False

        if code is None:
            return True
        self.runcode(code, source)
        return False

    def runcode(self, code, source):
        """Execute a code object.

        When an exception occurs, errors.simplify_traceback() is called to
        display a traceback.  All exceptions are caught.

        A note about KeyboardInterrupt: this exception may occur
        elsewhere in this code, and may not always be caught.  The
        caller should be prepared to deal with it.
        """
        try:
            exec_code(code, self.locals, source=source, username=self.username)
            #exec code in self.locals
        except:
            sys.stderr.write(errors.simplify_traceback(source, self.username))
        else:
            if softspace(sys.stdout, 0):
                print('')

    def write(self, data):
        """Write a string.

        The base implementation writes to sys.stderr; a subclass may
        replace this with a different implementation.

        """
        sys.stderr.write(data)

class InteractiveConsole(InteractiveInterpreter):
    """Closely emulate the behavior of the interactive Python interpreter.

    This class builds on InteractiveInterpreter and adds prompting
    using the familiar sys.ps1 and sys.ps2, and input buffering.

    """

    def __init__(self, locals=None, filename="<console>", username=None):
        """Constructor.

        The optional locals argument will be passed to the
        InteractiveInterpreter base class.

        The optional filename argument should specify the (file)name
        of the input stream; it will show up in tracebacks.

        """
        InteractiveInterpreter.__init__(self, locals, username=username)
        self.filename = filename
        self.resetbuffer()

    def resetbuffer(self):
        """Reset the input buffer."""
        self.buffer = []

    def interact(self, ps1=">>> ", ps2 = "... ", symbol="single"):
        """Closely emulate the interactive Python console.
        """
        # >' get translated as '&gt;' when passing through Crunchy...
        ps1 = ps1.replace('&gt;', '>')
        ps1 = ps1.replace('&lt;', '<')
        ps2 = ps2.replace('&gt;', '>')
        ps2 = ps2.replace('&lt;', '<')
        more = False
        # the following will be used to style the prompt
        # in cometIO.TreadedBuffer.write
        ps1 = 'crunchy_py_prompt' + ps1
        ps2 = 'crunchy_py_prompt' + ps2

        while True:
            try:
                if more:
                    prompt = ps2
                else:
                    prompt = ps1
                try:
                    line = self.raw_input(prompt)
                except EOFError:
                    self.write("\n")
                    break
                else:
                    more = self.push(line, symbol)
            except KeyboardInterrupt:
                self.write("\nKeyboardInterrupt\n")
                self.resetbuffer()
                more = False

    def push(self, line, symbol='single'):
        """Push a line to the interpreter.

        The line should not have a trailing newline; it may have
        internal newlines.  The line is appended to a buffer and the
        interpreter's runsource() method is called with the
        concatenated contents of the buffer as source.  If this
        indicates that the command was executed or invalid, the buffer
        is reset; otherwise, the command is incomplete, and the buffer
        is left as it was after the line was appended.  The return
        value is 1 if more input is required, 0 if the line was dealt
        with in some way (this is the same as runsource()).

        """
        self.buffer.append(line)
        source = "\n".join(self.buffer)
        more = self.runsource(source, self.filename, symbol)
        if not more:
            self.resetbuffer()
        return more

    def raw_input(self, prompt=""):
        """Write a prompt and read a line.

        The returned line does not include the trailing newline.
        When the user enters the EOF key sequence, EOFError is raised.

        The base implementation uses the built-in function
        raw_input(); a subclass may replace this with a different
        implementation.

        """
        # will need to replace by input(prompt)... for Python 3.0
        return raw_input(prompt)

#===== End of modified code.py ========

class SingleConsole(InteractiveConsole):
    '''SingleConsole are isolated one from another'''
    def __init__(self, locals={}, filename="Crunchy console", username=None):
        self.locals = locals
        self.locals['restart'] = self.restart
        InteractiveConsole.__init__(self, self.locals, filename=filename,
                                    username=username)

    def restart(self):
        """Used to restart an interpreter session, removing all variables
           and functions introduced by the user, but leaving Crunchy specific
           ones in."""
        to_delete = set()
        loc = inspect.currentframe(1).f_locals # == locals() of the calling
                                    # frame i.e. the interpreter session
        # We can't iterate over a dict while changing its size; however,
        # we can use the keys() method which creates a list of keys
        # and use that instead.
        for x in loc.keys():
            if x not in ['__builtins__', 'crunchy', 'restart']:
                del loc[x]
        return

class BorgGroups(object):
    '''Inspired by the Borg Idiom, from the Python Cookbook, 2nd Edition, p:273
    to deal with multiple Borg groups (one per crunchy page)
    while being compatible with Python 3.0a1/2.
    Derived class must use a super() call to work with this properly.
    '''
    _shared_states = {}
    def __init__(self, group="Borg"):
        if group not in self._shared_states:
            self._shared_states[group] = {}
        self.__dict__ = self._shared_states[group]

# The following BorgConsole class is defined such that all instances
# of an interpreter on a same html page share the same environment.

class BorgConsole(BorgGroups, SingleConsole):
    '''Every BorgConsole share a common state'''
    def __init__(self, locals={}, filename="Crunchy console", group="Borg",
                 username=None):
        super(BorgConsole, self).__init__(group=group)
        SingleConsole.__init__(self, locals, filename=filename,
                               username=username)

class TypeInfoConsole(BorgGroups, SingleConsole):
    '''meant to provide feedback as to type information
       inspired by John Posner's post on edu-sig
       http://mail.python.org/pipermail/edu-sig/2007-August/008166.html
    '''
    def __init__(self, locals={}, filename="Crunchy console", group="Borg",
                 username=None):
        super(TypeInfoConsole, self).__init__(group=group)
        SingleConsole.__init__(self, locals, filename=filename, username=username)

    def runcode(self, code, source):
        """Execute a code object.

           This version temporarily re-assigns sys.displayhook
           so as to give feedback about type when echoing a value
           entered at the prompt.
        """
        saved_dp = sys.displayhook
        sys.displayhook = self.show_expression_value
        try:
            exec_code(code, self.locals, source=source, username=self.username)
            #exec code in self.locals
        except:
            sys.stderr.write(errors.simplify_traceback(source, self.username))
        else:
            if softspace(sys.stdout, 0):
                print
        sys.displayhook = saved_dp

    def show_expression_value(self, val):
        """
        Show expression value or function return value.
        """
        try:
            t = type(val)
        except:
            t = ''
        if t == type(None):
            t = ''

        if t:
            if t == type('string'):
                print("'" + str(val) + "'      " + str(t))
            else:
                print(str(val) + "      " + str(t))

#  Unfortunately, IPython interferes with Crunchy; I'm commenting it out, keeping it in as a reference.
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
