import threading, sys
from code import InteractiveConsole

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
        """run the code, redirecting stdout, stderr, stdin and returning the string representing the output
        """
        sys.stdin.register_thread(self.channel)
        sys.stdout.register_thread(self.channel)
        sys.stderr.register_thread(self.channel)
        try:
            self.ccode = compile(self.code, "crunchy_exec", 'exec')
        except:
            raise
        if not self.ccode:    #code does nothing
            return
        try:
            exec self.ccode in self.symbols
        except:
            raise
        sys.stdin.unregister_thread()
        sys.stdout.unregister_thread()
        sys.stderr.unregister_thread()
    

class BorgConsole(InteractiveConsole):
    _shared_state = {}
    def __new__(cls, *a, **k):
        obj = object.__new__(cls, *a, **k)
        obj.__dict__ = cls._shared_state
        return obj
    def __init__(self):
        InteractiveConsole.__init__(self)
