import threading
import sys
import code

class Interpreter(threading.Thread):
    """Run python source asynchronously and parse the standard
        python error output to make it friendlier.  Also, helps
        with the isolation of sessions.
    """
    def __init__(self, code, name, symbols = {}, doctest=False):
        threading.Thread.__init__(self)
        self.code = code
        self.name = name
        self._doctest = doctest
        self.symbols = symbols

    def run(self):
        """run the code, redirecting stdout and returning the string representing the output
        """
        sys.stdin.register_thread(self.name)
        sys.stdout.register_thread(self.name)
        sys.stderr.register_thread(self.name)
        if self.code == "interpreter":
            v = sys.version.split(" ")[0]
            t = crunchyConsole()
            t.interact('Crunchy interpreter; Python version %s'%v)
        else:
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

class Borg(object):
    _shared_state = {}
    def __new__(cls, *a, **k):
        obj = object.__new__(cls, *a, **k)
        obj.__dict__ = cls._shared_state
        return obj

class crunchyConsole(Borg, code.InteractiveConsole):
    def __init__(self):
        code.InteractiveConsole.__init__(self)
