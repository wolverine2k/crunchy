'''httprepl.py
Adapted from Robert (fumanchu) Brewer's code.
Basic class to provide a Python interpreter embedded in a browser.
repl: read-eval-print loop.
'''

import codeop
import inspect
import re
from StringIO import StringIO
import sys
import crunchytraceback

from translation import _

interps = {}

class Singleton(object):
    """From the 2nd edition of the Python cookbook.
       Ensures that only one instance is created per running script"""
    def __new__(cls, *args, **kwargs):
        if '_inst' not in vars(cls):
            cls._inst = object.__new__(cls, *args, **kwargs)
        return cls._inst

class HTTPrepl(Singleton):
   
    def __init__(self):
        self.locals = {}
        self.buffer = []
   
    def push(self, line):
        """Push 'line' and return exec results (None if more input needed)."""
        if line == "help":
            return _("Type help(object) for help about object.")
        if line == "help()":
            return _("You cannot call help() without an argument.")
        self.buffer.append(line)
        source = "\n".join(self.buffer)
        try:
            code = codeop.compile_command(source, "<Crunchy :-)>", 'single')
        except (OverflowError, SyntaxError, ValueError):
            self.buffer = []
            return crunchytraceback.get_syntax_error(line)
        if code is None:
            # More lines needed.
            return None
        self.buffer = []
        res = self.execute(code)
        if not res:
            return ''
        else: 
            return res
   
    def execute(self, code):
        """Execute the given code in self.locals and return any stdout/sterr."""
        out = StringIO()
        oldout = sys.stdout
        olderr = sys.stderr
        sys.stdout = sys.stderr = out
        try:
            try:
                exec code in self.locals
            except:
                result = crunchytraceback.get_traceback(" ")
            else:
                result = out.getvalue()
        finally:
            sys.stdout = oldout
            sys.stderr = olderr
        out.close()
        return result
   
    def dir(self, line):
        """Examine a partial line and provide attr list of final expr."""
        line = re.split(r"\s", line)[-1].strip()
        # Support lines like "thing.attr" as "thing.", because the browser
        # may not finish calculating the partial line until after the user
        # has clicked on a few more keys.
        line = ".".join(line.split(".")[:-1])
        try:
            result = eval("dir(%s)" % line, {}, self.locals)
        except:
            return []
        return result
   
    def doc(self, line):
        """Examine a partial line and provide sig+doc of final expr."""
        line = re.split(r"\s", line)[-1].strip()
        # Support lines like "func(text" as "func(", because the browser
        # may not finish calculating the partial line until after the user
        # has clicked on a few more keys.
        line = "(".join(line.split("(")[:-1])
        try:
            result = eval(line, {}, self.locals)
            try:
                if isinstance(result, type):
                    func = result.__init__
                else:
                    func = result
                args, varargs, varkw, defaults = inspect.getargspec(func)
            except TypeError:
                if callable(result):
                    doc = getattr(result, "__doc__", "") or ""
                    return "%s\n\n%s" % (line, doc)
                return None
        except:
            return _('%s is not defined yet')%line
       
        if args and args[0] == 'self':
            args.pop(0)
        missing = object()
        defaults = defaults or []
        defaults = ([missing] * (len(args) - len(defaults))) + list(defaults)
        arglist = []
        for a, d in zip(args, defaults):
            if d is missing:
                arglist.append(a)
            else:
                arglist.append("%s=%s" % (a, d))
        if varargs:
            arglist.append("*%s" % varargs)
        if varkw:
            arglist.append("**%s" % varkw)
        doc = getattr(result, "__doc__", "") or ""
        return "%s(%s)\n%s" % (line, ", ".join(arglist), doc)