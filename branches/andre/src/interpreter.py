
import inspect
import threading, sys
import sys
import traceback
from codeop import CommandCompiler, compile_command

from src.interface import StringIO, exec_code, python_version, translate

from src.utilities import trim_empty_lines_from_end, log_session
import src.configuration as configuration
if python_version < 3:
    import src.errors as errors

_ = translate['_']

class Interpreter(threading.Thread):
    """
    Run python source asynchronously
    """
    def __init__(self, code, channel, symbols = {}, doctest=False):
        threading.Thread.__init__(self)
        if python_version < 3:
            self.code = trim_empty_lines_from_end(code) # problem with Py3k?
        else:
            self.code = code
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
                if configuration.defaults.friendly and python_version < 3:
                    sys.stderr.write(errors.simplify_traceback(self.code))
                else:
                    traceback.print_exc()
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
                            user_code = _("# no code entered by user\n").encode("utf-8")
                        data = "<span class='stdin'>" + user_code + "</span>"
                        configuration.defaults.log[log_id].append(data)
                        log_session()
                exec_code(self.ccode, self.symbols, source=None)
                #exec self.ccode in self.symbols#, {}
                # note: previously, the "local" directory used for exec
                # was simply an empty directory.  However, this meant that
                # module names imported outside a function definition
                # were not available inside that function.  This is why
                # we have commented out the {} as a reminder; self.symbols
                # will be used for holding both global and local variables.
            except:
                if configuration.defaults.friendly and python_version < 3:
                    sys.stderr.write(errors.simplify_traceback(self.code))
                else:
                    traceback.print_exc()
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
                        user_code = _("# no code entered by user\n").encode("utf-8")
                    # separating each attempts
                    user_code = "\n" + "- "*25 + "\n" + user_code

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

    def __init__(self, locals=None):
        """
        The optional 'locals' argument specifies the dictionary in
        which code will be executed; it defaults to a newly created
        dictionary with key "__name__" set to "__console__" and key
        "__doc__" set to None.

        """
        if locals is None:
            locals = {"__name__": "__console__", "__doc__": None}
        self.locals = locals
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
            if python_version < 3:
                sys.stderr.write(errors.simplify_traceback(source))
            else:
                traceback.print_exc()
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
            exec_code(code, self.locals, source=source)
            #exec code in self.locals
        except:
            sys.stderr.write(errors.simplify_traceback(source))
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

    def __init__(self, locals=None, filename="<console>"):
        """Constructor.

        The optional locals argument will be passed to the
        InteractiveInterpreter base class.

        The optional filename argument should specify the (file)name
        of the input stream; it will show up in tracebacks.

        """
        InteractiveInterpreter.__init__(self, locals)
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
        ## Getting ahead of ourselves: ready for Python 3000 ;-)
        #if int(sys.version.split('.')[0]) > 2:
        #    return input(prompt)
        #return raw_input(prompt)
        if python_version < 3:
            return raw_input(prompt)
        else:
            return input(prompt)
            sys.stdout.write(prompt)
            sys.stdout.flush()
            return sys.stdin.readline()

#===== End of modified code.py ========

class SingleConsole(InteractiveConsole):
    '''SingleConsole are isolated one from another'''
    def __init__(self, locals={}, filename="Crunchy console"):
        self.locals = locals
        self.locals['restart'] = self.restart
        InteractiveConsole.__init__(self, self.locals, filename=filename)

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


class Borg(object):
    '''Borg Idiom, from the Python Cookbook, 2nd Edition, p:273

    Derive a class form this; all instances of that class will share the
    same state, provided that they don't override __new__; otherwise,
    remember to use Borg.__new__ within the overriden class.
    '''
    _shared_state = {}

    if python_version < 3:
        def __new__(cls, *a, **k):
            obj = object.__new__(cls, *a, **k)
            obj.__dict__ = cls._shared_state
            return obj
    else:
        def __init__(self):
            self.__dict__ = self._shared_state


# The following BorgConsole class is defined such that all instances
# of an interpreter on a same html page share the same environment.
# However, for reasons that are not clear and that need to be explained
# (but do present the desired behaviour!!!!), request for new
# pages are such that interpreters on new pages start with fresh
# environments.

class BorgConsole(Borg, SingleConsole):
    '''Every BorgConsole share a common state'''
    def __init__(self, locals={}, filename="Crunchy console"):
        if python_version >=3:
            super(BorgConsole, self).__init__()
        SingleConsole.__init__(self, locals, filename=filename)

class TypeInfoConsole(Borg, SingleConsole):
    '''meant to provide feedback as to type information
       inspired by John Posner's post on edu-sig
       http://mail.python.org/pipermail/edu-sig/2007-August/008166.html
    '''
    def __init__(self, locals={}, filename="Crunchy console"):
        if python_version >=3:
            super(BorgConsole, self).__init__()
        SingleConsole.__init__(self, locals, filename=filename)

    def runcode(self, code, source):
        """Execute a code object.

           This version temporarily re-assigns sys.displayhook
           so as to give feedback about type when echoing a value
           entered at the prompt.
        """
        saved_dp = sys.displayhook
        sys.displayhook = self.show_expression_value
        try:
            exec_code(code, self.locals, source=source)
            #exec code in self.locals
        except:
            sys.stderr.write(errors.simplify_traceback(source))
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
