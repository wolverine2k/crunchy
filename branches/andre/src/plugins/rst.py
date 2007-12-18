"""Plugin for loading and transforming ReST files."""
import os, sys
import src.CrunchyPlugin as CrunchyPlugin

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
        CrunchyPlugin.register_http_handler("/rst", load_rst)
        CrunchyPlugin.register_tag_handler("span", "title", "load_rst", insert_load_rst)

def load_rst(request):
    """Loads rst file from disk, 
    transforms it into html and then creates new page"""
    class ReST_file:
        """Represents file with transformed text from rst into html.
        Vlam thinks it is ordinary file object"""
        def __init__(self, data):
            self._data = data
        def read(self):
            return self._data

    url = request.args["url"]
    file = open(url)

    rst_file = ReST_file(publish_string(file.read(), writer_name="html"))
    page = CrunchyPlugin.create_vlam_page(rst_file, 
            url, local=True)
    
    request.send_response(200)
    request.end_headers()
    request.wfile.write(page.read())

def insert_load_rst(page, parent, uid):
    """Creates new widget for loading rst files.
    Only include <span title="load_rst"> </span>"""
    name1 = 'browser_rst'
    name2 = 'submit_rst'
    form1 = CrunchyPlugin.SubElement(parent, 'form', name=name1,
                        onblur = "document.%s.url.value="%name2+\
                        "document.%s.filename.value"%name1)
    input1 = CrunchyPlugin.SubElement(form1, 'input', type='file',
                 name='filename', size='80')
    br = CrunchyPlugin.SubElement(form1, 'br')

    form2 = CrunchyPlugin.SubElement(parent, 'form', name=name2, method='get',
                action='/rst')
    input2 = CrunchyPlugin.SubElement(form2, 'input', type='hidden', name='url')
    input3 = CrunchyPlugin.SubElement(form2, 'input', type='submit',
             value='Load local ReST file')
    input3.attrib['class'] = 'crunchy'
