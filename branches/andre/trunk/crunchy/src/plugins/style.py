'''styles the code using Pygments'''

from pygments import highlight
from pygments.lexers import get_lexer_by_name, guess_lexer
from pygments.formatters import HtmlFormatter
from pygments.styles import get_style_by_name, get_all_styles
from pygments.lexers._mapping import LEXERS

from src.interface import fromstring, plugin, SubElement, additional_properties, config
from src.configuration import make_property, options

_pygment_lexer_names = {}
_pygment_language_names = []
for name in LEXERS:
    aliases = LEXERS[name][2]
    _pygment_lexer_names[name] = aliases[0]
    for alias in aliases:
        _pygment_language_names.append(alias)

lexers = {}

def register():
    for language in _pygment_language_names:
        plugin["register_tag_handler"]("code", "title", language, pygment_style)
        plugin["register_tag_handler"]("pre", "title", language, pygment_style)
    for language in _pygment_lexer_names:
        plugin["register_tag_handler"]("code", "title", language, pygment_style)
        plugin["register_tag_handler"]("pre", "title", language, pygment_style)
    options['cssclass'] = list(get_all_styles())
    additional_properties['cssclass'] = make_property('cssclass', default='crunchy',
                                                      doc="some help")

def extract_code(elem):
    text = elem.text or ""
    for node in elem:
        text += extract_code(node)
        if node.tag == "br": text += "\n"
        if node.tail: text += node.tail
    return text.replace("\r", "")

def pygment_style(page, elem, dummy_uid):
    language = elem.attrib['title']
    text = extract_code(elem)
    cssclass = config[page.username]['cssclass']
    styled_code = style(text, language, cssclass)
    markup = fromstring(styled_code)
    elem.text = ''
    elem[:] = markup[:]
    elem.attrib['class'] = cssclass
    if not page.includes("pygment_cssclass"):
        page.add_css_code(HtmlFormatter(style=cssclass).get_style_defs("."+cssclass))
        page.add_include("pygment_cssclass")
    return

class PreHtmlFormatter(HtmlFormatter):
    '''unlike HtmlFormatter, does not embed the styled code inside both
       a <div> and a <pre>; rather embeds it inside a <pre> only.'''

    def wrap(self, source, outfile):
        return self._wrap_code(source)

    def _wrap_code(self, source):
        yield 0, '<pre>'
        for i, t in source:
            yield i, t
        yield 0, '</pre>'


def style(raw_code, language, cssclass="highlight"):
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

    return highlight(raw_code, lexer, formatter)
