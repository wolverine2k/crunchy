

from pygments import highlight
from pygments.lexers import get_lexer_by_name, guess_lexer
from pygments.formatters import HtmlFormatter
from pygments.styles import get_style_by_name

from src.interface import fromstring, plugin, SubElement

# The following can and should be extended to many more languages.
# See http://pygments.org/docs/lexers/
allowed_languages = ['python', 'html']
lexers = {}

def register():
    for language in allowed_languages:
        plugin["register_tag_handler"]("code", "title", language, pygment_style)
        plugin["register_tag_handler"]("pre", "title", language, pygment_style)

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
    cssclass = "default"
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


def style(raw_code, language=None, cssclass="highlight"):
    """Returns a string of formatted and styled HTML, where
    raw_code is a string, language is a string that Pygments has a lexer for,
    and cssclass is a class style available for Pygments."""
    # Note: eventually, cssclass would be obtained from a user's preferences
    # and would not need to be passed as an argument to style()

    # avoid calling get_lexer_by_name more than necessary
    if language is None:                # WARNING: could throw
        lexer = guess_lexer(raw_code)	# pygments.util.ClassNotFound if no lexer
    else:                               # can be found for raw_code.  Needs to be
        try:							# handled.
            lexer = lexers[language]
        except:
            lexers[language] = get_lexer_by_name(language, stripall = True)
            lexer = lexers[language]

    formatter = PreHtmlFormatter()
    formatter.cssclass = cssclass
    formatter.style = get_style_by_name(cssclass)

    return highlight(raw_code, lexer, formatter)
