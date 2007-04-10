'''
colourize.py

Processes python code to embed it into an html file with styling information.
This module can easily be used with programs other than crunchy; it is
therefore strongly suggested to keep it separate.
'''

import re
import keyword
import StringIO
import token
import tokenize

# The following are introduced so as to be somewhat similar to EditArea
reserved = ['True', 'False', 'None']
"""
	builtins : see http://python.org/doc/current/lib/built-in-funcs.html
"""
builtins = ['__import__', 'abs', 'basestring', 'bool', 'callable', 'chr', 'classmethod', 'cmp',
			'compile', 'complex', 'delattr', 'dict', 'dir', 'divmod', 'enumerate', 'eval', 'execfile',
			'file', 'filter', 'float', 'frozenset', 'getattr', 'globals', 'hasattr', 'hash', 'help',
			'hex', 'id', 'input', 'int', 'isinstance', 'issubclass', 'iter', 'len', 'list', 'locals',
			'long', 'map', 'max', 'min', 'object', 'oct', 'open', 'ord', 'pow', 'property', 'range',
			'raw_input', 'reduce', 'reload', 'repr', 'reversed', 'round', 'set', 'setattr', 'slice',
			'sorted', 'staticmethod', 'str', 'sum', 'super', 'tuple', 'type', 'unichr', 'unicode',
			'vars', 'xrange', 'zip',
			# Built-in constants: http://www.python.org/doc/2.4.1/lib/node35.html
			#'False', 'True', 'None' have been included in 'reserved'
			'NotImplemented', 'Ellipsis',
			# Built-in Exceptions: http://python.org/doc/current/lib/module-exceptions.html
			'Exception', 'StandardError', 'ArithmeticError', 'LookupError', 'EnvironmentError',
			'AssertionError', 'AttributeError', 'EOFError', 'FloatingPointError', 'IOError',
			'ImportError', 'IndexError', 'KeyError', 'KeyboardInterrupt', 'MemoryError', 'NameError',
			'NotImplementedError', 'OSError', 'OverflowError', 'ReferenceError', 'RuntimeError',
			'StopIteration', 'SyntaxError', 'SystemError', 'SystemExit', 'TypeError',
			'UnboundlocalError', 'UnicodeError', 'UnicodeEncodeError', 'UnicodeDecodeError',
			'UnicodeTranslateError', 'ValueError', 'WindowsError', 'ZeroDivisionError', 'Warning',
			'UserWarning', 'DeprecationWarning', 'PendingDeprecationWarning', 'SyntaxWarning',
			'RuntimeWarning', 'FutureWarning',
			# we will include the string methods as well
			# http://python.org/doc/current/lib/string-methods.html
			'capitalize', 'center', 'count', 'decode', 'encode', 'endswith', 'expandtabs',
			'find', 'index', 'isalnum', 'isaplpha', 'isdigit', 'islower', 'isspace', 'istitle',
			'isupper', 'join', 'ljust', 'lower', 'lstrip', 'replace', 'rfind', 'rindex', 'rjust',
			'rsplit', 'rstrip', 'split', 'splitlines', 'startswith', 'strip', 'swapcase', 'title',
			'translate', 'upper', 'zfill'
]
"""
	standard library; see  http://python.org/doc/current/lib/modindex.html
"""
stdlib = [	'__builtin__', '__future__', '__main__', '_winreg', 'aifc', 'AL', 'al', 'anydbm',
			'array', 'asynchat', 'asyncore', 'atexit', 'audioop', 'base64', 'BaseHTTPServer',
			'Bastion', 'binascii', 'binhex', 'bisect', 'bsddb', 'bz2', 'calendar', 'cd', 'cgi',
			'CGIHTTPServer', 'cgitb', 'chunk', 'cmath', 'cmd', 'code', 'codecs', 'codeop',
			'collections', 'colorsys', 'commands', 'compileall', 'compiler', 'compiler',
			'ConfigParser', 'Cookie', 'cookielib', 'copy', 'copy_reg', 'cPickle', 'crypt',
			'cStringIO', 'csv', 'curses', 'datetime', 'dbhash', 'dbm', 'decimal', 'DEVICE',
			'difflib', 'dircache', 'dis', 'distutils', 'dl', 'doctest', 'DocXMLRPCServer', 'dumbdbm',
			'dummy_thread', 'dummy_threading', 'email', 'encodings', 'errno', 'exceptions', 'fcntl',
			'filecmp', 'fileinput', 'FL', 'fl', 'flp', 'fm', 'fnmatch', 'formatter', 'fpectl',
			'fpformat', 'ftplib', 'gc', 'gdbm', 'getopt', 'getpass', 'gettext', 'GL', 'gl', 'glob',
			'gopherlib', 'grp', 'gzip', 'heapq', 'hmac', 'hotshot', 'htmlentitydefs', 'htmllib',
			'HTMLParser', 'httplib', 'imageop', 'imaplib', 'imgfile', 'imghdr', 'imp', 'inspect',
			'itertools', 'jpeg', 'keyword', 'linecache', 'locale', 'logging', 'mailbox', 'mailcap',
			'marshal', 'math', 'md5', 'mhlib', 'mimetools', 'mimetypes', 'MimeWriter', 'mimify',
			'mmap', 'msvcrt', 'multifile', 'mutex', 'netrc', 'new', 'nis', 'nntplib', 'operator',
			'optparse', 'os', 'ossaudiodev', 'parser', 'pdb', 'pickle', 'pickletools', 'pipes',
			'pkgutil', 'platform', 'popen2', 'poplib', 'posix', 'posixfile', 'pprint', 'profile',
			'pstats', 'pty', 'pwd', 'py_compile', 'pyclbr', 'pydoc', 'Queue', 'quopri', 'random',
			're', 'readline', 'repr', 'resource', 'rexec', 'rfc822', 'rgbimg', 'rlcompleter',
			'robotparser', 'sched', 'ScrolledText', 'select', 'sets', 'sgmllib', 'sha', 'shelve',
			'shlex', 'shutil', 'signal', 'SimpleHTTPServer', 'SimpleXMLRPCServer', 'site', 'smtpd',
			'smtplib', 'sndhdr', 'socket', 'SocketServer', 'stat', 'statcache', 'statvfs', 'string',
			'StringIO', 'stringprep', 'struct', 'subprocess', 'sunau', 'SUNAUDIODEV', 'sunaudiodev',
			'symbol', 'sys', 'syslog', 'tabnanny', 'tarfile', 'telnetlib', 'tempfile', 'termios',
			'test', 'textwrap', 'thread', 'threading', 'time', 'timeit', 'Tix', 'Tkinter', 'token',
			'tokenize', 'traceback', 'tty', 'turtle', 'types', 'unicodedata', 'unittest', 'urllib2',
			'urllib', 'urlparse', 'user', 'UserDict', 'UserList', 'UserString', 'uu', 'warnings',
			'wave', 'weakref', 'webbrowser', 'whichdb', 'whrandom', 'winsound', 'xdrlib', 'xml',
			'xmllib', 'xmlrpclib', 'zipfile', 'zipimport', 'zlib'
]

class Colourizer(object):

    def __init__(self, linenumber=False):
        self.tokenString = ''
        self.reset(linenumber)

    def reset(self, linenumber=False):
        self.beginLine, self.beginColumn = (0, 0)
        self.endOldLine, self.endOldColumn = (0, 0)
        self.endLine, self.endColumn = (0, 0)
        self.tokenType = token.NEWLINE
        self.outputLineNumber = linenumber

#===== Keywords, numbers and operators ===
    def formatName(self, aWord):
        word = aWord.strip()
        if keyword.iskeyword(word) or word in reserved:
            return "<span class='py_keyword'>"
        elif word in builtins:
            return "<span class='py_builtins'>"
        elif word in stdlib:
            return "<span class='py_stdlib'>"
        elif word.endswith("__") and word.startswith("__"):
            return "<span class='py_special'>"
        else:
            return "<span class='py_variable'>"

    def formatNumber(self):
        return "<span class='py_number'>"

    def formatOperator(self):
        return "<span class='py_op'>"

#========= Strings, including comments ====
    def formatString(self):
        if len(self.tokenString) <= 2:
            self.tokenString = self.changeHTMLspecialCharacters(self.tokenString)
            return "<span class='py_string'>"
        if self.tokenString[0] == self.tokenString[1] and \
               self.tokenString[1] == self.tokenString[2] and\
               self.tokenString[0] in ["'", '"']:
            return self.formatMultiLineComment()
        else:
            self.tokenString = self.changeHTMLspecialCharacters(self.tokenString)
            return "<span class='py_string'>"

    def formatComment(self):
        self.tokenString = self.changeHTMLspecialCharacters(self.tokenString)
        return "<span class='py_comment'>"

    def changeHTMLspecialCharacters(self, aString):
        aString = aString.replace('&', '&amp;')
        aString = aString.replace('<', '&lt;')
        aString = aString.replace('>', '&gt;')
        return aString

    def formatMultiLineComment(self):
        self.tokenString = self.changeHTMLspecialCharacters(self.tokenString)
        if self.outputLineNumber:
            temp_in = self.tokenString.split('\n')
            line_num = self.beginLine
            if line_num == 1:
                prefix = "<span class='py_linenumber'>%3d </span>"%line_num
            else:
                prefix = ''
            temp_out = prefix + temp_in[0]
            for substring in temp_in[1:]:
                line_num += 1
                temp_out += "\n<span class='py_linenumber'>%3d </span>"%line_num \
                            + substring
            self.tokenString = temp_out
        # we will assume they are real string as opposed to multi-line comments
        return "<span class='py_string'>"
        # return "<span class='py_comment'>"

    def indent(self):
        self.tokenString = " "*self.beginColumn + self.tokenString

    def spaceToken(self):
        self.tokenString = " "*(self.beginColumn - self.endOldColumn) +  \
                            self.tokenString

# ==================================
    def htmlFormat(self):
        if self.tokenType == token.NAME:
            beginSpan = self.formatName(self.tokenString)
        elif self.tokenType == token.STRING:
            beginSpan = self.formatString()
        elif self.tokenType == tokenize.COMMENT:
            beginSpan = self.formatComment()
        elif self.tokenType == token.NUMBER:
            beginSpan = self.formatNumber()
        elif self.tokenType == token.OP:
            beginSpan = self.formatOperator()
        else:
            beginSpan = "<span>"

        if self.tokenString == '\n':
            htmlString = '\n'
        elif self.tokenString == '':
            htmlString = ''
        else:
            htmlString = beginSpan + self.tokenString + "</span>"
        return htmlString

    def processNewLine(self):
        if self.lastTokenType in [tokenize.COMMENT, tokenize.NEWLINE, tokenize.NL]:
            if self.outputLineNumber:
                self.outp.write("<span class='py_linenumber'>%3d </span>" % self.beginLine)
        elif self.tokenType != tokenize.DEDENT:  # logical line continues
            self.outp.write("\n")
        else:
            pass  # end of file

# inp.readline reads a "logical" line;
# the continuation character '\' is gobbled up.
    def parseListing(self, code):
        self.inp = StringIO.StringIO(code)
        self.outp = StringIO.StringIO()
        for tok in tokenize.generate_tokens(self.inp.readline):
            self.lastTokenType = self.tokenType
            self.tokenType = tok[0]
            self.lastTokenString = self.tokenString
            self.tokenString = tok[1]
            self.beginLine, self.beginColumn = tok[2]
            self.endOldLine, self.endOldColumn = self.endLine, self.endColumn
            self.endLine, self.endColumn = tok[3]

            if self.tokenType == token.ENDMARKER:
                break
            if self.beginLine != self.endOldLine:
                self.processNewLine()
                self.indent()
            else:
                self.spaceToken()
            self.outp.write("%s" % self.htmlFormat())
        code = self.outp.getvalue()
        self.inp.close()
        self.outp.close()
        self.reset()
        return code

# externally callable function

def style(text, line_numbering=False):
    colourizer = Colourizer()
    colourizer.outputLineNumber = line_numbering
    # remove any pre-existing markup
    text = convert_br(text)
    text = strip_html(text)
    return colourizer.parseListing(text)

def extract_code_from_interpreter(text):
    """ Strips fake interpreter prompts from html code meant to
        simulate a Python session, and remove lines without prompts, which
        are supposed to represent Python output."""
    stripped = [] # either the prompt + line number, or simulated output
    # stripped is actually a list of tuples containing either
    # (prompt, line_number_where_it_appears) or
    # ('', simulated_output)
    new_lines = [] # will contain the python code
    if not text:
        return
    lines = text.split('\n')
    linenumber = 1
    for line in lines:
        if line.endswith('\r'):
            line = line[:-1]
        if line.startswith("&gt;&gt;&gt; "):
            new_lines.append(line[13:].rstrip())
            stripped.append(("&gt;&gt;&gt; ", linenumber))
            linenumber += 1
        elif line.rstrip() == "&gt;&gt;&gt;": # tutorial writer may forget the
                                     # extra space for an empty line
            new_lines.append('')
            stripped.append(("&gt;&gt;&gt; ", linenumber))
            linenumber += 1
        elif line.startswith("... "):
            new_lines.append(line[4:].rstrip())
            stripped.append(("... ", linenumber))
            linenumber += 1
        elif line.rstrip() == "...": # tutorial writer may forget the extra
            new_lines.append('')     # space for an empty line
            stripped.append(("... ", linenumber))
            linenumber += 1
        else: # append result of output instead
            stripped.append(('', line))
    python_code = '\n'.join(new_lines)
    return python_code, stripped

def strip_html(text):
    '''removes all html markup; based on
       http://effbot.org/zone/re-sub.htm#strip-html'''
    def fixup(m):
        text = m.group(0)
        if text[:1] == "<":
            return "" # ignore tags
        return text # leave as is
    return re.sub("(?s)<[^>]*>", fixup, text)

def convert_br(text):
    '''convert <br>, <br/>, <br />, < BR / >, etc., into "\n"'''
    def fixup(m):
        text = m.group(0)
        if text[:1] == "<":
            return "" # ignore tags
        return text # leave as is
    return re.sub("(?s)<\s*[bB][rR]\s*/*\s*>", fixup, text)
