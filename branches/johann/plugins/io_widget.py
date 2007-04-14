"""The IO widget, handles text and graphical IO

This is just the UI part, the communication code is defined in the core
"""

provides = set(["io_subwidget"])

from CrunchyPlugin import *

from element_tree import ElementTree, HTMLTreeBuilder
et = ElementTree

def register():
    register_service(insert_io_subwidget, "insert_io_subwidget")
    
def insert_io_subwidget(page, elem, uid):
    """insert an output widget into elem, usable for editors and interpreters,
    includes a canvas :-)
    """
    if not hasattr(page, "io_included"):
        page.io_included = True
        page.add_js_code(io_js)
    output = et.SubElement(elem, "span")
    output.attrib["class"] = "output"
    output.attrib["id"] = "out_" + uid
    output.text = "\n"
    inp = et.SubElement(elem, "input")
    inp.attrib["id"] = "in_" + uid
    inp.attrib["onkeydown"] = 'push_keys(event, "%s")' % uid
    inp.attrib["type"] = "text"
    inp.attrib["class"] = "input"
    canvas = et.SubElement(elem, "canvas")
    canvas.attrib["id"] = "canvas_" + uid
    canvas.attrib["width"] = "400"
    canvas.attrib["height"] = "400"
    canvas.attrib["class"] = "crunchy_canvas"
    canvas.text = "You need a browser that supports &lt;canvas&gt; for this to work"
    
io_js = r"""
function push_keys(event, uid){
    if(event.keyCode != 13) return;
    data = document.getElementById("in_"+uid).value;
    document.getElementById("in_"+uid).value = "";
    var i = new XMLHttpRequest()
    i.open("POST", "/input?uid="+uid, true);
    i.send(data + "\n");
};
"""
