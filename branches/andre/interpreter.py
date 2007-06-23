import threading, sys
from code import InteractiveConsole
from traceback import print_exc

interp_code = """
BorgConsole().interact()
"""

class Interpreter(threading.Thread):
    """
    Run python source asynchronously
    """
    def __init__(self, code, channel, symbols = {}, doctest=False):
        threading.Thread.__init__(self)
        self.code = code
        self.channel = channel
        self._doctest = doctest
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
                exec self.ccode in self.symbols, {}
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

class BorgConsole(Borg, InteractiveConsole):
    def __init__(self):
        InteractiveConsole.__init__(self)
