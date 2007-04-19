

from CrunchyPlugin import *

requires = set(["io_widget", "/exec"])

def register():
    register_vlam_handler("pre", "interpreter", insert_interpreter)
           
def insert_interpreter(page, elem, uid, vlam):
    """inserts an interpreter (actually the js code to initialise an interpreter)"""
    if not page.includes("interp_included"):
        page.add_include("interp_included")
        page.add_js_code(interp_js)
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
    # 3) and the output
    page.add_js_code('init_interp("%s");' % uid)
    services.insert_io_subwidget(page, elem, uid)
    
interp_js = r"""
function init_interp(uid){
    code = "import interpreter\ninterpreter.BorgConsole().interact()";
    var j = new XMLHttpRequest();
    j.open("POST", "/exec?uid="+uid, false);
    j.send(code);
};
"""
