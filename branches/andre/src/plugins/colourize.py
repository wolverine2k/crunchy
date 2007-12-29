# -*- coding: utf-8 -*-
'''colourize.py

This module is a intended to style Python code
contained inside a <pre> or a <code> element and possibly insert the it
into a more complicated html structure.

The current module assumes that html element have been parsed by
ElementTree to become ElementTree Elements.
If we replaced ElementTree by another parser (say, BeautifulSoup), we
would only need to modify only parts of this module, as idenfied below.
'''

# stdlib modules
import copy
import re
import keyword
import token
import tokenize

from src.interface import StringIO, ElementTree, python_version, translate
et = ElementTree
from src.utilities import trim_empty_lines_from_end, changeHTMLspecialCharacters

#---------begin plugin specific---------------------
# All plugins should import the crunchy plugin API
import src.CrunchyPlugin as CrunchyPlugin

_ = translate['_']

# The set of other "widgets/services" provided by this plugin
provides = set(["style_pycode"])

def register():
    """The register() function is required for all plugins.
       In this case, we need to register two types of 'actions':
       1. a custom 'vlam handler' designed to tell Crunchy how to
          interpret the special Crunchy markup with 4 different cases;
       2. a custom service to style some code when requested by this or
          another plugin.
       """
    # 'py_code' or 'python_code' (both are equivalent) only appears inside
    # <pre> or <code> elements, using the notation
    # <pre title='py_code ...'>, etc.
    CrunchyPlugin.register_tag_handler("code", "title", "py_code", plugin_style)
    CrunchyPlugin.register_tag_handler("code", "title", "python_code", plugin_style)
    CrunchyPlugin.register_tag_handler("pre", "title", "py_code", plugin_style)
    CrunchyPlugin.register_tag_handler("pre", "title", "python_code", plugin_style)
    # this plugin can style some Python code, returning both the styled
    # code and either the extracted Python code ...
    CrunchyPlugin.register_service(service_style, "style_pycode")
    # ... or the simulated interactive session, usable as a doctest.
    CrunchyPlugin.register_service(service_style_nostrip, "style_pycode_nostrip")



def plugin_style(dummy_page, elem, dummy_uid):
    '''Handles the vlam py_code elements'''
    code, markup, error = style(elem)
    if error is None:
        replace_element(elem, markup)
    else:
        br = et.Element("br")
        br.tail = elem.text
        elem.text = ''
        elem.insert(0, br)
        elem.insert(0, error)

def service_style(dummy_page, elem):
    return style(elem)

def service_style_nostrip(dummy_page, elem):
    return nostrip_style(elem)

#---------end plugin specific-------------------------

#--------Begin ElementTree dependent part-------------

def style(elem):
    """
    style some Python code (adding html markup) and return it inside the
    original html element (<pre> or <code>, most likely) with attributes
    unchanged.  Any original markup inside the Python code
    will be removed, except that <br/> will have been converted into "\n".

    To be more specific, if 'title' is present, style() does the following:
    1. take as input an ElementTree Element corresponding to
       an html element (such as <pre> or <code>) containing some Python code;
       this Python code may already be marked up;
    2. pass the content of the Element (including any other markup present)
       as an "html string" (i.e. no longer an ElementTree Element)
       to colourize.py so that it can be styled appropriately;
    4. return the new marked up element, as well as the corresponding
       Python code;
    5. empty lines of code appearing either at the beginning or the
       end of the <pre> or <code> element are removed

    For example (using html notation), we could have as input
    <pre title="some value">
    print <span class="some value">"Hi!"</span>

    </pre>

    and the corresponding output would be
    <pre title="some value">
    <span class="py_keyword">print</span> <span class="string">"Hi!"</span>
    </pre>
    """
    py_code = extract_code(elem)

    tail = elem.tail
    if "no_style" in elem.attrib['title']:
        markup = copy.deepcopy(elem)
        return py_code, markup, None

    # styling
    offset = get_linenumber_offset(elem.attrib['title'])
    styled_code, py_code = _style(py_code, offset)

    # re-creating element
    tag = elem.tag
    new_html = "<%s>\n%s\n</%s>"%(tag, styled_code, tag)
    try:
        new_elem = et.fromstring(new_html)
    except:
        new_html = new_html.encode('utf-8')
        try:
            new_elem = et.fromstring(new_html)
        except:
            sp = et.Element("span")
            sp.attrib['class'] = "py_warning"
            sp.text = _("Crunchy: could not style the following code")
            return '', '', sp
    new_elem.attrib = dict(elem.attrib) # quick *copy* of a dict!
    if 'class' in new_elem.attrib:
        if 'crunchy' not in new_elem.attrib['class']:
            new_elem.attrib['class'] += ' crunchy'
    else:
        new_elem.attrib['class'] = 'crunchy'
    new_elem.tail = tail
    return py_code, new_elem, None

def nostrip_style(elem):
    """performs exactly the same as style(elem) except that the python
    code it returns is intended to be the exact copy of an original
    interpreter session (stripped of any html markup).
    It is intended to be used with 'doctest' - and any other similar
    future plugin.  Note: we could have included this functionality
    within style() by parsing elem.attrib['title'] for 'doctest',
    but this would have prevented the creation of a doctest-like plugin
    independently of changing the code for style().
    """
    py_code = extract_code(elem)
    if "no_style" in elem.attrib['title']:
        new_elem = copy.deepcopy(elem)
        return py_code, new_elem

    tail = elem.tail
    # styling
    offset = get_linenumber_offset(elem.attrib['title'])
    styled_code, dummy = _style(py_code, offset)
    # re-creating element
    tag = elem.tag
    new_html = "<%s>\n%s\n</%s>"%(tag, styled_code, tag)
    try:
        new_elem = et.fromstring(new_html)
    except:
        new_html = new_html.encode('utf-8')
        try:
            new_elem = et.fromstring(new_html)
        except:
            sp = et.Element("span")
            sp.attrib['class'] = "py_warning"
            sp.text = _("Crunchy: could not style the following code")
            return '', '', sp   # will be treated as special case in vlam_image_file.py
                                # Need to treat this more consistently i.e. have the
                                # same number of arguments returned - perhaps check
                                # if return a tuple as second argument
    new_elem.attrib = dict(elem.attrib) # quick *copy* of a dict!
    if 'class' in new_elem.attrib:
        new_elem.attrib['class'] += ' crunchy'
    else:
        new_elem.attrib['class'] = 'crunchy'
    new_elem.tail = tail
    return py_code, new_elem

def extract_code(elem, trim=False):
    """extract all the text (Python code) from a marked up
    code sample encoded as an ElementTree structure, but converting
    <br/> into "\n" and removing "\r" which are not
    expected in Python code; inspired by F.Lundh's gettext()
    """
    text = elem.text or ""

    for e in elem:
        text += extract_code(e)
        if e.tag == 'br':
            text += '\n'
        if e.tail:
            text += e.tail
    # \r causes bugs!
    text = text.replace("\r", "")
    if trim:
        text = trim_empty_lines_from_end(text)
    return text

def get_linenumber_offset(vlam):
    """ Determine the desired number for the 1st line of Python code.
        The vlam code is expected to be of the form
        [linenumber [=n]]    (where n is an integer)
        but could contain upper case letters as well.

        Note that the vlam code uses "linenumber" as it is easier to read,
        but we use "offset" (i.e. difference from the normal starting
        number 1) in internal calculations as it is easier to simply
        add an offset without having to remember to subtract 1
        everywhere."""
    if 'linenumber' in vlam.lower():
        try:
            res = re.search(r'linenumber\s*=\s*([0-9]*)', vlam.lower())
            offset = int(res.groups()[0]) - 1
        except:
            offset = 0 # linenumber will start at 1
    else:
        offset = None # no linenumber will be added
    return offset

def replace_element(elem, replacement):
    '''replace the content of an ElementTree Element by that of another
       one.'''
    if python_version < 3:
        elem.clear()
        elem.text = replacement.text
        elem.tail = replacement.tail
        elem.tag = replacement.tag
        elem.attrib = replacement.attrib
        elem[:] = replacement[:]   # does not work with py3k
    else:
        elem.__dict__ = replacement.__dict__
    return

#--------End ElementTree dependent part-------------
# ===== The following code deals with regular html encoded content.

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

    def __init__(self, offset=None):
        self.tokenString = ''
        self.beginLine, self.beginColumn = (0, 0)
        self.endOldLine, self.endOldColumn = (0, 0)
        self.endLine, self.endColumn = (0, 0)
        self.tokenType = token.NEWLINE
        self.offset = offset
    # if offset != None, we start to count the line numbers at 1 + offset

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
        self.tokenString = self.changeHTMLspecialCharacters(self.tokenString)
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
        if self.offset is not None:
            temp_in = self.tokenString.split('\n')
            line_num = self.beginLine + self.offset
            #
            temp_out = temp_in[0]
            for substring in temp_in[1:]:
                line_num += 1
                temp_out += "\n<span class='py_linenumber'>%3d </span>"%line_num \
                            + substring
            self.tokenString = temp_out
        if self.lastTokenType == token.OP:
        # we will assume they are real string as opposed to multi-line comments
            return "<span class='py_string'>"
        else:
            return "<span class='py_comment'>"

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
            if self.offset is not None:
                self.outp.write("<span class='py_linenumber'>%3d </span>" % (self.beginLine+self.offset))
        elif self.tokenType != tokenize.DEDENT:  # logical line continues
            self.outp.write("\n")
        else:
            pass  # end of file

# inp.readline reads a "logical" line;
# the continuation character '\' is gobbled up.
    def parseListing(self, code):
        self.inp = StringIO(code)
        self.outp = StringIO()
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
        #self.reset()
        return code

# externally callable function

def _style(text, offset=None):
    """remove prompts and output (if interpreter session)
       and return code with html markup for styling as well as raw Python
       code."""
    colourizer = Colourizer(offset)
    raw_code = trim_empty_lines_from_end(text)
    interpreter = is_interpreter_session(raw_code)
    if interpreter:
        raw_code, stripped = extract_code_from_interpreter(raw_code)
    try:
        styled_code = colourizer.parseListing(raw_code)
        if interpreter:
            styled_code = add_back_prompt_and_output(styled_code, stripped,
                                                     offset)
        # \r is unnecesary and causes bugs!
        raw_code = raw_code.replace('\r', '')
        return styled_code, raw_code
    except Exception:#, parsingErrorMessage:
        error_message = parsing_error_dialog()#parsingErrorMessage)
        return "<span class='py_warning'>%s</span>\n<span>%s</span>"%(
                                       error_message, raw_code), None

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
        if line.startswith(">>> "):
            new_lines.append(line[4:].rstrip())
            stripped.append(("&gt;&gt;&gt; ", linenumber))
            linenumber += 1
        elif line.rstrip() == ">>>": # tutorial writer may forget the
                                     # extra space for an empty line
            new_lines.append(' ')
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


def add_back_prompt_and_output(py_code, stripped, offset=None):
    '''adds back the interpreter prompt and simulated output to a
       styled interpreter session.'''
    newlines = []
    lines = py_code.split('\n')
    # making some explicit definitions for clarity
    if offset != -1:
        line_info_len = len("<span class='py_linenumber'>    </span>")
    else:
        line_info_len = 0
    span_len = len("<span>")
    endspan_len = len("</span>")

    for (prompt, info) in stripped:
        if prompt:
            if offset is not None:
                #sometimes, a <span> or </span> gets prepended to
                # a line; we need to make sure that this does not
                # result in overlapping <span>s which makes the
                # prompt the same font size as the linenumber
                if lines[info-1].startswith("<span>"):
                    length = span_len + line_info_len#pr_len
                elif lines[info-1].startswith("</span>"):
                    length = endspan_len + line_info_len#pr_len
                else:
                    length = line_info_len#pr_len
                newlines.append(lines[info-1][:length] +
                                '<span class="py_prompt">' + prompt +
                      '</span>' + lines[info-1][length:])
            else:
                newlines.append('<span class="py_prompt">' + prompt +
                      '</span>' + lines[info-1])
        elif info:
            info = changeHTMLspecialCharacters(info)
            if offset is not None:  # get the spacing right...
                newlines.append("<span class='py_linenumber'>    </span>"
                               + '<span class="py_output">' + info +
                               '</span>')
            else:
                newlines.append('<span class="py_output">' + info +
                                '</span>')
    return '\n'.join(newlines)

def is_interpreter_session(py_code):
    '''determine if the python code corresponds to a simulated
       interpreter session'''
    lines = py_code.split('\n')
    for line in lines:
        if line.strip():  # look for first non-blank line
            if line.startswith(">>>"):
                return True
            else:
                return False

def parsing_error_dialog():
#def parsing_error_dialog(info):
    '''Information given when the code colourizer fails.'''
    #return _("Parsing error occurred in the following Python code.\nInfo: %s.")%info
    return _("Parsing error occurred in the following Python code.")


