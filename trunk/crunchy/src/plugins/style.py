'''styles the code using Pygments'''
import re
import random

from pygments import highlight
from pygments.lexers import get_lexer_by_name, guess_lexer
from pygments.formatters import HtmlFormatter
from pygments.styles import get_style_by_name, get_all_styles
from pygments.lexers._mapping import LEXERS
from pygments.token import STANDARD_TYPES, Generic, Comment

from src.interface import (fromstring, plugin, Element, SubElement,
                           additional_properties, config)
import src.interface as interface
from src.configuration import make_property, options
from src.utilities import extract_code, wrap_in_div

_pygment_lexer_names = {}
_pygment_language_names = []
for name in LEXERS:
    aliases = LEXERS[name][2]
    _pygment_lexer_names[name] = aliases[0]
    for alias in aliases:
        _pygment_language_names.append(alias)

interface.crunchy_pygments = CRUNCHY_PYGMENTS = ("crunchy_pygments_" +
                             str(int(random.random()*1000000000000)))

lexers = {}
options['style'] = list(get_all_styles())
additional_properties['style'] = make_property('style', default='tango',
doc="""\
Style used by pygments to colorize the code.  In addition to the default
value ['crunchy'], it includes all the styles [css classes] included
in the pygments distribution.""")

def register():
    for language in _pygment_language_names:
        plugin["register_tag_handler"]("code", "title", language, pygments_style)
        plugin["register_tag_handler"]("pre", "title", language, pygments_style)
    for language in _pygment_lexer_names:
        plugin["register_tag_handler"]("code", "title", language, pygments_style)
        plugin["register_tag_handler"]("pre", "title", language, pygments_style)

    # for compatibility with the old notation
    styling_choices = ['py_code', 'python_code']
    for style in styling_choices:
        plugin['register_tag_handler']("code", "title", style, pygments_style)
        plugin['register_tag_handler']("pre", "title", style, pygments_style)
        plugin['add_vlam_option']('no_markup', style)


    plugin["register_tag_handler"]("div", "title", "get_pygments_tokens",
                                   get_pygments_tokens)
    plugin['register_service']("style", pygments_style)
    randomize_css_classes()

def pygments_style(page, elem, dummy_uid='42', vlam=None):
    cssclass = config[page.username]['style']
    wrap = False
    if vlam is not None:
        show_vlam = create_show_vlam(cssclass, elem, vlam)
    elif 'show_vlam' in elem.attrib['title']:
        show_vlam = create_show_vlam(cssclass, elem, elem.attrib['title'])
        wrap = True
    else:
        show_vlam = None
    language = elem.attrib['title'].split()[0]
    if language in ['py_code', 'python_code']:
        language = "python"
    text = extract_code(elem)
    styled_code = _style(text, language, cssclass).encode("utf-8")
    if vlam is None:
        vlam = elem.attrib['title']
    if 'linenumber' in vlam:
        styled_code = add_linenumber(styled_code, vlam)

    markup = fromstring(styled_code)
    elem[:] = markup[:]
    elem.text = markup.text
    elem.attrib['class'] = CRUNCHY_PYGMENTS
    if not page.includes("pygment_cssclass"):
        # replacing class name for security reasons.
        page.add_css_code(HtmlFormatter(style=cssclass).get_style_defs("."+cssclass).replace(cssclass, CRUNCHY_PYGMENTS))
        page.add_include("pygment_cssclass")
    if wrap:
        wrap_in_div(elem, dummy_uid, '', "show_vlam", show_vlam)
    return text, show_vlam

def create_show_vlam(cssclass, elem, vlam):
    '''Creates a <code> element showing the complete vlam options
    used, as well as the element type.'''
    if 'show_vlam' not in vlam:
        return None
    attributes = ' title="%s"' % vlam
    for attr in elem.attrib:
        if attr != 'title':
            attributes += ' %s="%s"' % (attr, elem.attrib[attr])
    elem_info = '<%s%s> ... </%s>' % (elem.tag, attributes, elem.tag)
    styled_elem_info = _style(elem_info, 'html', cssclass)
    show_vlam = fromstring(styled_elem_info)
    show_vlam.tag = 'code'
    show_vlam.attrib['class'] = CRUNCHY_PYGMENTS
    display = Element('h3')
    display.attrib['class'] = "show_vlam"
    display.text = "VLAM = "
    display.append(show_vlam)
    return display

def randomize_css_classes():
    '''replace pygments names for classes by random ones'''
    # This is done for security reason, to prevent a malicious tutorial
    # writer from overriding a css class and hiding some python code
    # (especially "easy" to do in doctest) by having the css class
    # correspond to "display: none;".  Python would still execute
    # the code but the user would never see it.
    global STANDARD_TYPES
    for key in STANDARD_TYPES:
        STANDARD_TYPES[key] += "_" + str(int(random.random()*1000000000000))
    interface.generic_output = STANDARD_TYPES[Generic.Output]
    interface.generic_traceback = STANDARD_TYPES[Generic.Traceback]
    interface.generic_prompt = STANDARD_TYPES[Generic.Prompt]
    interface.comment = STANDARD_TYPES[Comment]
    interface.init_stdios() # re-init to have proper css class

def get_pygments_tokens(page, elem, uid):
    """inserts a table containing all existent token types and corresponding
       css class, with an example"""
    # The original div in the raw html page may contain some text
    # as a visual reminder that we need to remove here.
    elem.text = ''
    elem.attrib['class'] = CRUNCHY_PYGMENTS
    table = SubElement(elem, 'table')
    row = SubElement(table, 'tr')
    for title in ['Token type', 'css class']:
        column = SubElement(row, 'th')
        column.text = title
    keys = STANDARD_TYPES.keys()
    keys.sort()
    for token in keys:
        if len(repr(token)) == 5: # token = Token
            continue
        row = SubElement(table, 'tr')
        column1 = SubElement(row, 'td')
        column1.text = repr(token)[6:] # remove "Token."
        column2 = SubElement(row, 'td')
        token_class = STANDARD_TYPES[token]
        column2.text = token_class.split('_')[0]
        column3 = SubElement(row, 'td')
        span = SubElement(column3, 'span')
        span.attrib['class'] = token_class
        span.text = " * test * "
        column4 = SubElement(row, 'td')
        _code = SubElement(column4, 'code')
        _code.attrib['class'] = token_class
        _code.text = " * test * "
        column5 = SubElement(row, 'td')
        var = SubElement(column5, 'var')
        var.attrib['class'] = token_class
        var.text = " * test * "
    return

class PreHtmlFormatter(HtmlFormatter):
    '''unlike HtmlFormatter, does not embed the styled code inside both
       a <div> and a <pre>; rather embeds it inside a <pre> only.'''

    def wrap(self, source, outfile):
        return self._wrap_code(source)

    def _wrap_code(self, source):
        yield 0, '<pre>\n'
        for i, t in source:
            yield i, t
        yield 0, '</pre>'


def _style(raw_code, language, cssclass):
    """Returns a string of formatted and styled HTML, where
    raw_code is a string, language is a string that Pygments has a lexer for,
    and cssclass is a class style available for Pygments."""
    # Note: eventually, cssclass would be obtained from a user's preferences
    # and would not need to be passed as an argument to style()
    global _pygment_lexer_names
    requested_language = language
    try:
        lexer = lexers[language]
    except:
        if language in _pygment_lexer_names:
            language = _pygment_lexer_names[requested_language]
            lexers[requested_language] = get_lexer_by_name(language, stripall=True)
        else:
            lexers[language] = get_lexer_by_name(language, stripall=True)
        lexer = lexers[requested_language]

    formatter = PreHtmlFormatter()
    formatter.cssclass = cssclass
    formatter.style = get_style_by_name(cssclass)

    # the removal of "\n" below prevents an extra space to be introduced
    # with the background color of the selected cssclass
    return highlight(raw_code, lexer, formatter).replace("\n</pre>", "</pre>")

def add_linenumber(styled_code, vlam):
    '''adds the line number information'''
    lines = styled_code.split('\n')
    # is the class surrounded by quotes or double quotes?
    prompt1 = '<span class="%s"' % interface.generic_prompt
    prompt2 = "<span class='%s'" % interface.generic_prompt
    if lines[1].startswith(prompt1):
        prompt_present = True
        prompt = prompt1
    elif lines[1].startswith(prompt2):
        prompt_present = True
        prompt = prompt2
    else:
        prompt_present = False
    lineno = get_linenumber_offset(vlam)
    # first and last lines are the embedding <pre>...</pre>
    open_span = "<span class = 'linenumber %s'>" % interface.comment
    for index, line in enumerate(lines[1:-1]):
        if prompt_present:
            if lines[index+1].startswith(prompt):
                lines[index+1] = open_span + "%3d </span>" % (lineno) + line
                lineno += 1
            else:
                lines[index+1] = open_span + "    </span>" + line
        else:
            lines[index+1] = open_span + "%3d </span>" % (lineno) + line
            lineno += 1
    return '\n'.join(lines)

def get_linenumber_offset(vlam):
    """ Determine the desired number for the 1st line of Python code.
        The vlam code is expected to be of the form
        [linenumber [=n]]    (where n is an integer).
    """
    try:
        res = re.search(r'linenumber\s*=\s*([0-9]*)', vlam)
        offset = int(res.groups()[0])
    except:
        offset = 1
    return offset