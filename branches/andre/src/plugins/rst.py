"""Plugin for loading and transforming ReST files."""

# All plugins should import the crunchy plugin API via interface.py
from src.interface import plugin, SubElement

_docutils_installed = True
try:
    from docutils.core import publish_string
except:
    _docutils_installed = False

if _docutils_installed:
    provides = set(["/rst"])

def register():
    """Registers new http handler and new widget for loading ReST files"""
    if _docutils_installed:
        plugin['register_http_handler']("/rst", load_rst)
        plugin['register_tag_handler']("span", "title", "load_rst", insert_load_rst)

class ReST_file:
    """Represents file with transformed text from rst into html.
    vlam thinks it is an ordinary file object"""
    def __init__(self, data):
        self._data = data
    def read(self):
        return self._data

def load_rst(request):
    """Loads rst file from disk, 
    transforms it into html and then creates new page"""
    url = request.args["url"]
    file_ = open(url)

    rst_file = ReST_file(publish_string(file_.read(), writer_name="html"))
    page = plugin['create_vlam_page'](rst_file, url, local=True)
    
    request.send_response(200)
    request.end_headers()
    request.wfile.write(page.read())

def insert_load_rst(dummy_page, parent, dummy_uid):
    """Creates new widget for loading rst files.
    Only include <span title="load_rst"> </span>"""
    name1 = 'browser_rst'
    name2 = 'submit_rst'
    form1 = SubElement(parent, 'form', name=name1,
                        onblur = "document.%s.url.value="%name2+\
                        "document.%s.filename.value"%name1)
    SubElement(form1, 'input', type='file', name='filename', size='80')
    SubElement(form1, 'br')

    form2 = SubElement(parent, 'form', name=name2, method='get', action='/rst')
    SubElement(form2, 'input', type='hidden', name='url')
    input3 = SubElement(form2, 'input', type='submit',
                        value='Load local ReST file')
    input3.attrib['class'] = 'crunchy'
