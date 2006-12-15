'''
code execution and simplification of error messages

'''
from doctest import DocTestRunner, DocTestParser
import re
from xml.sax.saxutils import escape as _escape
import threading
import sys
import crunchytraceback

import crunchytute
import soundout

from translation import _

interpreters = {}
success = False

def escape(data):
    """make a string suitable for embedding in HTML"""
    data =  _escape(data)
    data = data.replace('\n', '<br/>')
    return data

    
class CrunchyInterpreter(threading.Thread):
    """Run python source asynchronously and parse the standard 
        python error output to make it friendlier.  Also, helps 
        with the isolation of sessions.
    """
    def __init__(self, code, name, symbols = {}, doctest=False):
        threading.Thread.__init__(self)
        self.code = code
        interpreters[name] = self
        self.name = name
        self.symbols = dict(symbols, **soundout.all_sounds)
        self._doctest = doctest
        
    def run(self):
        """run the code, redirecting stdout and returning the string representing the output
        """
        sys.stdout.register_thread(id = self.name)
        sys.stderr.register_thread(self.name)
        self.code = fixLineEnding(self.code)
        try:
            self.ccode = compile(self.code, "crunchy_exec", 'exec')
        except:
            sys.stderr.write(crunchytraceback.get_syntax_error(self.code))
            return
        if not self.ccode:    #code does nothing
            return
        try:
            exec self.ccode in self.symbols
        except:
            sys.stderr.write(crunchytraceback.get_traceback(self.code))
            
    def get(self):
        global success
        str1 = sys.stdout.get_by_id(self.name)
        str2 = sys.stderr.get_by_id(self.name)
        info = ''
        if self._doctest and str1: # str1 should mean that doctest was executed
            str1 = '<span class="error_info">' + escape(str1) + "</span>"
            if not success:
                str2, exception_found = self.simplify_doctest_error_message(str2)
                if exception_found:
                    info = '<br/><span class="error_info">' + \
                       '<a href="/docs/reference/errors.html">' + \
                       '%s</a></span>'%_("Follow this link if you want to know more about exceptions.")
        elif self._doctest:  # should be: a syntax error prevented execution
            lines = str2.split('\n')
            if lines[0].strip().startswith("File"): # remove meaningless line
                lines = lines[1:]
            # Python indicates the approximative location of a syntax error by
            # a caret (^) preceded by a number of whitespaces.  The whitespaces
            # are essentially removed by html; so we replace them by something
            # visible so that the caret is located where Python indicated.
            for n, line in enumerate(lines):
                nb_spaces = 0
                for character in line:
                    if character == " ":
                        nb_spaces += 1
                    else:
                        break
                if nb_spaces >= 4:
                    nb_spaces -= 4
                    lines[n] = "~"*nb_spaces + lines[n][nb_spaces:]
            str2 = '\n'.join(lines)
        else:
            str1 = '<span class="stdout">' + escape(str1) + "</span>"
        str2 = '<span class="stderr">' + escape(str2) + "</span>" + info
        return str1 + str2

    def simplify_doctest_error_message(self, msg):
        stars = "*"*70
        failures = msg.split(stars)
        new_mesg = ["="*70]
        exception_found = False
        for fail in failures:
            if fail: # ignore empty lines
                lines = fail.split('\n')
                for line in lines[2:-2]:
                    if line.startswith("Failed example:"):
                        new_mesg.append(_("The following example failed:"))
                    elif line.startswith("Expected:"):
                        new_mesg.append(_("The expected result was:"))
                    elif line.startswith("Got:"):
                        new_mesg.append(_("The result obtained was:"))
                    elif line.startswith("Exception raised:"):
                        new_mesg.append(_("An exception was raised:"))
                        exception_found = True
                        break
                    else:
                        new_mesg.append(line)
                new_mesg.append(lines[-2])
                new_mesg.append("-"*70)
        return '\n'.join(new_mesg), exception_found

def run_doctest(code, doctestname):
    '''Executes some Python code treated as a module accompanied by some
       doctests to be tested by the doctest module from the standard
       library.
    '''
    doctest = fixLineEnding('\n"""\n' + crunchytute.DOCTESTS[doctestname] + '\n"""\n')
    code += '''
import sys
__t=sys.stdout
sys.stdout = sys.stderr
__test = __parser.get_doctest(__teststring, globals(),"Crunchy Doctest", "<crunchy>", 0)
_x= __runner.run(__test)
sys.stdout=__t
print analyse(_x)
'''
    runner = DocTestRunner()
    parser = DocTestParser()
    symbols = {'__parser': parser, 
                '__runner': runner, 
                '__teststring': doctest,
                'analyse': analyse_doctest_result}

    i = CrunchyInterpreter(code, doctestname, symbols, True)
    i.start()
    return
    
def analyse_doctest_result(x):
    """Determines the message to give based on the number of failures."""
    global success
    failures, total = x
    if failures:
        success = False
    else:
        success = True
    if total == 0:
        return _("There was no test to satisfy.")
    elif total == 1:
        if failures == 0:
            return _("Congratulation, your code passed the test!")
        else:
            return _("You code failed the test.")
    else:
        if failures == 0:
            return _("Congratulation, your code passed all %d tests!")%total
        elif failures == total:
            return _("Your code failed all %d tests.")%total
        else:
            return _("Your code failed %s out of %s tests.")%(failures, total)


def fixLineEnding(txt):
    # Python recognize line endings as '\n' whereas, afaik:
    # Windows uses '\r\n' to identify line endings
    # *nix uses '\n'   (ok :-)
    # Mac OS uses '\r'
    # So, we're going to convert all to '\n'
    txt1 = re.sub('\r\n', '\n', txt) # Windows: tested
    txt = re.sub('\r', '\n', txt1)  # not tested yet: no Mac :-(
    return txt


class StrBuf(object):
    """A buffer that can be written to on one end and read from the other
        This IS thread safe.
    """
    def __init__(self):
        self.buf = ''
        self.lock = threading.RLock()
    def close(self):
        """noop"""
        pass
    def flush(self):
        """noop"""
        pass
    def write(self, data):
        self.lock.acquire()
        self.buf += data
        self.lock.release()
    def read(self):
        self.lock.acquire()
        t = self.buf
        self.buf = ''
        self.lock.release()
        return t
    closed = False

    