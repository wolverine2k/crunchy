"""The IO widget, handles text and graphical IO
This is just the UI part, the communication code is defined in the core
- maybe this should me moved to core?
"""

provides = set(["io_widget"])

from CrunchyPlugin import *
import CrunchyPlugin

def register():
    register_service(insert_io_subwidget, "insert_io_subwidget")

def insert_io_subwidget(page, elem, uid, borg=False):
    """insert an output widget into elem, usable for editors and interpreters,
    includes a canvas :-)
    """
    if not page.includes("io_included"):
        page.add_include("io_included")
        page.add_js_code(io_js)
        page.add_css_code(io_css)
    output = CrunchyPlugin.SubElement(elem, "span")
    output.attrib["class"] = "output"
    output.attrib["id"] = "out_" + uid
    output.text = "\n"
    inp = CrunchyPlugin.SubElement(elem, "input")
    inp.attrib["id"] = "in_" + uid
    inp.attrib["onkeydown"] = 'return push_keys(event, "%s")' % uid
    if borg:
        inp.attrib["onkeypress"] = 'return tooltip_display(event, "%s")' % uid
    inp.attrib["type"] = "text"
    inp.attrib["class"] = "input"

io_js = r"""
function push_keys(event, uid){
    // prevent Esc from breaking the interpreter
    if (event.keyCode == 27) return false;

    if (event.keyCode != 13) return true;
    data = document.getElementById("in_"+uid).value;
    document.getElementById("in_"+uid).value = "";
    var i = new XMLHttpRequest()
    i.open("POST", "/input?uid="+uid, true);
    i.send(data + "\n");

    return true;
};
"""

io_css = r"""

.stdout {
    color: blue;
    font-weight: normal;
}

.stderr {
    color: red;
}

.input {
    display: none;
    width: 80%;
    max-width: 800px;
    font: 11pt monospace;
    font-weight: bold;
    border: solid 1px
    border-width: 2px;
    background-color: #eff;
    border-color: #369;
}

.output{
    font: 10pt monospace;
    font-weight: bold;
    color:darkgreen;
    white-space: -moz-pre-wrap; /* Mozilla, supported since 1999 */
    white-space: pre-wrap; /* CSS3 - Text module (Candidate Recommendation)
                            http://www.w3.org/TR/css3-text/#white-space */
}

.crunchy_canvas{
    display: none;
}
"""
