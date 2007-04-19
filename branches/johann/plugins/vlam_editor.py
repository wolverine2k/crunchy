from CrunchyPlugin import *

# Third party modules - included in crunchy distribution
from element_tree import ElementTree, HTMLTreeBuilder
et = ElementTree

provides = set(["editor_widget"])
requires = set(["io_widget", "/exec", "style_pycode"])

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
    
def insert_editor(page, elem, uid, vlam):
    """handles the editor widget"""
    # first we need to make sure that the required javacript code is in the page:
    if not page.includes("doctest_included"):
        page.add_include("doctest_included")
        page.add_js_code(exec_jscode)
    # then we can go ahead and display everything:
    # 1) code styling
    if "linenumber" in vlam:
        offset = 0
    else: 
        offset = None
    code, markup = services.style_pycode(page, elem, offset)
    # 2) clear the element and get the code in
    tail = elem.tail
    elem.clear()
    elem.tail = tail
    elem.tag = "div"
    if not "no-pre" in vlam:
        elem.insert(0, markup)
    # 3) get an editor in place
    if "no-copy" in vlam:
        code = "\n"
    services.insert_editor_subwidget(elem, uid, code)
    et.SubElement(elem, "br")
    # 4) the buttons
    btn = et.SubElement(elem, "button")
    btn.attrib["onclick"] = "exec_code('%s')" % uid
    btn.text = "Execute"
    et.SubElement(elem, "br")
    # 5) and the output
    services.insert_io_subwidget(page, elem, uid)
    
exec_jscode= """
function exec_code(uid){
    code = document.getElementById("code_"+uid).value;
    var j = new XMLHttpRequest();
    j.open("POST", "/exec?uid="+uid, false);
    j.send(code);
};
"""
