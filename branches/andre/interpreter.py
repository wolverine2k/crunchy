import threading, sys
from code import InteractiveConsole
from traceback import print_exc

def trim_empty_lines_from_end(text):
    '''remove blank lines at beginning and end of code sample'''
    # this is needed to prevent indentation error if a blank line
    # with spaces at different levels is inserted at the end or beginning
    # of some code to be executed.
    # The same function is found in the plugin colourize.py - however
    # we can't import it here.
    lines = text.split('\n')
    top = 0
    for line in lines:
        if line.strip():
            break
        else:
            top += 1
    bottom = 0
    for line in lines[::-1]:
        if line.strip():
            break
        else:
            bottom += 1
    if bottom == 0:
        return '\n'.join(lines[top:])
    return '\n'.join(lines[top:-bottom])

class Interpreter(threading.Thread):
    """
    Run python source asynchronously
    """
    def __init__(self, code, channel, symbols = {}):
        threading.Thread.__init__(self)
        self.code = trim_empty_lines_from_end(code)
        self.channel = channel
        self.symbols = symbols

    def run(self):
        """run the code, redirecting stdout, stderr, stdin and
           returning the string representing the output
        """
        sys.stdin.register_thread(self.channel)
        sys.stdout.register_thread(self.channel)
        sys.stderr.register_thread(self.channel)
        try:
            try:
                self.ccode = compile(self.code, "crunchy_exec", 'exec')
            except:
                print_exc()
                raise
            if not self.ccode:    #code does nothing
                return
            try:
                exec self.ccode in self.symbols#, {}
                # note: previously, the "local" directory used for exec
                # was simply an empty directory.  However, this meant that
                # module names imported outside a function definition
                # were not available inside that function.  This is why
                # we have commented out the {} as a reminder; self.symbols
                # will be used for holding both global and local variables.
            except:
                print_exc()
                raise
        finally:
            sys.stdin.unregister_thread()
            sys.stdout.unregister_thread()
            sys.stderr.unregister_thread()
            print "finished run with channel=", self.channel


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

# Unexplained bug?  When a page is opened in a new tab (ctrl-T)
# with Firefox, we have problems with code execution....

# Note: In the future, I (andre) plan to have the two Crunchy consoles
# derive from a more feature complete version of Interactive Console.
# This is why, for now, SingleConsole is essentially the same
# as Intereactive console

class SingleConsole(InteractiveConsole):
    '''SingleConsole are isolated one from another'''
    def __init__(self, locals={}):
        InteractiveConsole.__init__(self, locals)

class BorgConsole(Borg, SingleConsole):
    '''Every BorgConsole share a common state'''
    def __init__(self, locals={}):
        SingleConsole.__init__(self, locals)
