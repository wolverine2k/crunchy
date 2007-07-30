"""The IO widget, handles text and graphical IO
This is just the UI part, the communication code is defined in the core
- maybe this should me moved to core?
"""

provides = set(["io_widget"])

import src.CrunchyPlugin as CrunchyPlugin
import src.configuration as configuration

# for converting to edit area
from editarea import editArea_load_and_save

# dummy function for now
def _(msg):
    return msg

def register():
    CrunchyPlugin.register_service(insert_io_subwidget, "insert_io_subwidget")

def insert_io_subwidget(page, elem, uid, interp_kind=None, sample_code=''):
    """insert an output widget into elem, usable for editors and interpreters,
    includes a canvas :-)
    """

    # When a security mode is set to "display ...", we only parse the
    # page, but no Python execution from is allowed from that page.
    # If that is the case, we won't include javascript either, to make
    # thus making the source easier to read.
    if 'display' not in configuration.defaults.security:

        if not page.includes("io_included"):
            page.add_include("io_included")
            page.add_js_code(io_js)
            page.add_css_code(io_css)

        if interp_kind is not None:
            if not page.includes("push_input_included"):
                page.add_include("push_input_included")
                page.add_js_code(push_input)
            # needed for switching to edit area; not currently working
            if not page.includes("editarea_included"):
                page.add_include("editarea_included")
                page.add_js_code(editArea_load_and_save)
                page.insert_js_file("/edit_area/edit_area_crunchy.js")

    output = CrunchyPlugin.SubElement(elem, "span")
    output.attrib["class"] = "output"
    output.attrib["id"] = "out_" + uid
    output.text = "\n"
    inp = CrunchyPlugin.SubElement(elem, "input")
    inp.attrib["id"] = "in_" + uid
    inp.attrib["onkeydown"] = 'return push_keys(event, "%s")' % uid
    if interp_kind is not None:
        editor_link = CrunchyPlugin.SubElement(inp, "a")
        editor_link.attrib["onclick"]= "return convertToEditor(this,'%s', '%s')"\
                                      %(_("Execute"), _("Copy code sample"))
        editor_link.attrib["id"] = "ed_link_" + uid
        image = CrunchyPlugin.SubElement(editor_link, 'img')
        image.attrib["src"] = "/editor.png"
        image.attrib["style"] = "border:0;padding:0;position:relative;top:12px;height:30px;"
        code_sample = CrunchyPlugin.SubElement(elem, "textarea")
        code_sample.attrib["id"] = "code_sample_" + uid
        code_sample.attrib["style"] = 'visibility:hidden;overflow:hidden;z-index:-1;position:fixed;top:0;'
        code_sample.text = sample_code
    if interp_kind == 'borg':
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

push_input = r"""
function push_input(uid){
    data = document.getElementById("code_"+uid).value;
    document.getElementById("in_"+uid).value = "";
    var i = new XMLHttpRequest()
    i.open("POST", "/input?uid="+uid, true);
    i.send(data + "\n");
    convertFromEditor(uid);
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
