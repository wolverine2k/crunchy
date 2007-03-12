

from CrunchyPlugin import *

requires = set(["io_subwidget"])

def register():
    register_vlam_handler("pre", "interpreter", insert_interpreter)
           
def insert_interpreter(page, elem, uid):
    """inserts an interpreter (actually the js code to initialise an interpreter)"""
    if not hasattr(page, "interp_included"):
        page.interp_included = True
        page.add_js_code(interp_js)
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
