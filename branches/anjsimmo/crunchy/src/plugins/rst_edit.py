'''
rst_edit is a plugin designed to insert an editor for reStructuredText with
instant previewer of corresponding html code.
'''

import os, sys

from src.interface import plugin, SubElement, python_version, translate
_ = translate['_']
import src.interface
from src.plugins.editarea import editArea_load_and_save, insert_file_browser
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
    # editor
    textarea = SubElement(elem, "textarea", name="rst_enter")
    textarea.attrib["id"] = uid + "_rst_edit"
    textarea.attrib["class"] = "rst_enter"
    textarea.text = elem.text
    elem.text = ''
    plugin['services'].enable_editarea(page, elem, textarea.attrib["id"], syntax="robotstxt")
    if not page.includes("editarea_included"):
        page.add_include("editarea_included")
        page.add_js_code(editArea_load_and_save)
        page.insert_js_file("/edit_area/edit_area_crunchy.js")

    # save html
    button = SubElement(elem, "button")
    button.text = _("Save html")

    # preview area
    div = SubElement(elem, "div")
    div.attrib["id"] = "html_preview"
    page.add_js_code(js_code)

    # hidden save file
    hidden_div = SubElement(elem, "div")
    h_uid = "hidden_div_" + uid
    hidden_div.attrib["id"] = h_uid
    button.attrib["onclick"] = show_save_file_js % h_uid
    add_save_file(page, hidden_div, h_uid, div.attrib["id"])
    page.add_js_code(save_html_file_js%(h_uid, h_uid))

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
    try:
        request.wfile.write(text)
    except:
        request.wfile.write(text.encode('utf-8'))

def add_save_file(page, parent, hidden_save_id, textarea_id):
    '''Inserts the widget required to browse for and save a local Python
       file.  This is intended to be used to save a file from the editor.
    '''
    input_id = "input_" + hidden_save_id
    js_saved_script = """save_html_file(document.getElementById('%s').value,
                        '%s');""" % (input_id, textarea_id)
    SubElement(parent, "br")
    SubElement(parent, 'input', name='url', size='60', id=input_id)
    SubElement(parent, "br")
    btn = SubElement(parent, 'button', onclick=js_saved_script)
    btn.text = _("Save file")

    js_script = """document.getElementById('%s').value=file;""" % input_id
    insert_file_browser(page, parent, hidden_save_id, '/jquery_file_tree_all',
                 _('Select a file to save'), js_script, "save_file")
    btn = SubElement(parent, 'button',
        onclick="c=getElementById('%s');c.style.visibility='hidden';c.style.zIndex=-1;"%hidden_save_id)
    btn.text = _("Cancel")
    return

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

show_save_file_js = """
var obj = document.getElementById('%s');
obj.style.zIndex = 99999;
obj.style.visibility = "visible";
"""

save_html_file_js = """
function save_html_file(path, id)
{
    if (path == ''){
        alert("No file specified");
        var obj = document.getElementById('%s');
        obj.style.visibility = "hidden";
        obj.style.zIndex = -1;
        return;
    }
    data = document.getElementById(id).innerHTML;
    var j = new XMLHttpRequest();
	j.open("POST", "/save_file", true);
	// Use an unlikely part of a filename (path) as a separator between file
	// path and file content.
	j.send(path+"_::EOF::_"+data);
    var obj = document.getElementById('%s');
    obj.style.visibility = "hidden";
    obj.style.zIndex = -1;
};
"""