from CrunchyPlugin import *

# Third party modules - included in crunchy distribution
from element_tree import ElementTree, HTMLTreeBuilder
et = ElementTree

provides = set(["editor_widget"])
requires = set(["io_widget", "/exec"])

def register():
    register_vlam_handler("pre", "editor", insert_editor)
    register_service(insert_editor_subwidget, "insert_editor_subwidget")
        
def insert_editor_subwidget(elem, uid, code="\n"):
    """inserts an Elementtree that is an editor,
    used to provide a basic insert_editor_subwidget service
    """
    inp = et.SubElement(elem, "textarea")
    inp.attrib["rows"] = "10"
    inp.attrib["cols"] = "80"
    inp.attrib["id"] = "code_" + uid
    inp.text = code
    
def insert_editor(page, elem, uid):
    """handles the editor widget"""
    # first we need to make sure that the required javacript code is in the page:
    if not hasattr(page, "exec_included"):
        page.exec_included = True
        page.add_js_code(exec_jscode)
    services.insert_editor_subwidget(elem, uid)
    et.SubElement(elem, "br")
    btn = et.SubElement(elem, "button")
    btn.attrib["onclick"] = "exec_code('%s')" % uid
    btn.text = "Execute"
    et.SubElement(elem, "br")
    services.insert_io_subwidget(page, elem, uid)
    
exec_jscode= """
function exec_code(uid){
    code = document.getElementById("code_"+uid).value;
    var j = new XMLHttpRequest();
    j.open("POST", "/exec?uid="+uid, false);
    j.send(code);
};
"""

