'''
rst_edit is a plugin designed to insert an editor for reStructuredText with
instant previewer of corresponding html code.
'''

import os, sys

from src.interface import plugin, SubElement, python_version
import src.interface
from src.plugins.editarea import editArea_load_and_save
import src.plugins.rst_directives

from docutils.core import publish_string

def register():
    """registers a tag handler to make an rst widget and a callback for
    taking care of ajaxy stuff.
       """
    # 'doctest' only appears inside <pre> elements, using the notation
    # <pre title='doctest ...'>
    plugin['register_tag_handler']("pre", "title", "rst_edit", rst_edit_setup)
    plugin['register_http_handler']("/rst_edit", rst_edit_callback)

def rst_edit_setup(page, elem, uid):
    elem.tag = "div"
    elem.text = ''
    textarea = SubElement(elem, "textarea", name="rst_enter", style="width:48%; height:20em; float:left;")
    textarea.attrib["id"] = uid + "_rst_edit"
    plugin['services'].enable_editarea(page, elem, textarea.attrib["id"])
    if not page.includes("editarea_included"):
        page.add_include("editarea_included")
        page.add_js_code(editArea_load_and_save)
        page.insert_js_file("/edit_area/edit_area_crunchy.js")
    div = SubElement(elem, "div", style="width:50%; border: solid 1px green; float: left;")
    div.attrib["id"] = "html_preview"
    page.add_js_code(js_code)
    if page.is_local:
        src.interface.path_info['source_base_dir'] = page.url
    else:
        src.interface.path_info['source_base_dir'] = os.path.normpath(os.path.join(
                        plugin['crunchy_base_dir'](), "server_root", page.url[1:]))
    base_dir = os.path.dirname(src.interface.path_info['source_base_dir'])
    if base_dir not in sys.path:
        sys.path.insert(0, base_dir)

def rst_edit_callback(request):
    """Handles all execution of doctests. The request object will contain
    all the data in the AJAX message sent from the browser."""
    if python_version >= 3:
        request.data = request.data.decode('utf-8')
    text = request.data
    text = publish_string(text, writer_name="html")
    request.send_response(200)
    request.send_header('Cache-Control', 'no-cache, no-store')
    request.end_headers()
    request.wfile.write(text.encode('utf-8'))


js_code = '''
$(document).ready(function(){
    function send_rst(text){
        $.post("/rst_edit", text, function(data){$("#html_preview").html(data)});
    };

    $("textarea[name='rst_enter']")
      .bind("keyup", function(){ $("#html_preview").html(
                                                    send_rst($(this).val()));
                                }); });

'''