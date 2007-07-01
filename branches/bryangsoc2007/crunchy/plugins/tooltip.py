"""This plugin provides tooltips for interpreters"""

import CrunchyPlugin
import interpreter
import re

from element_tree import ElementTree
et = ElementTree

provides = set(["/dir","/doc","/help"])

def register():
    # register service, /dir, /doc, and /help
    CrunchyPlugin.register_service(insert_tooltip, "insert_tooltip")
    CrunchyPlugin.register_http_handler("/dir%s"%CrunchyPlugin.session_random_id, dir_handler)
    CrunchyPlugin.register_http_handler("/doc%s"%CrunchyPlugin.session_random_id, doc_handler)
    CrunchyPlugin.register_http_handler("/help%s"%CrunchyPlugin.session_random_id, help_handler)

def insert_tooltip(page, elem, uid):
    # add div for displaying the tooltip
    tipbar = et.SubElement(elem, "div")
    tipbar.attrib["id"] = "tipbar_" + uid
    tipbar.attrib["class"] = "interp_tipbar"

    if not page.includes("tooltip_included"):
        page.add_include("tooltip_included")
        page.insert_js_file("/tooltip.js")
        page.add_js_code(tooltip_js)
        page.add_css_code(tooltip_css)
"""
        # add help div
        help_menu = et.SubElement(elem, "div")
        help_menu.attrib["id"] = "help_menu"
        help_menu.attrib["class"] = "interp_tipbar"
"""
def dir_handler(request):
    """Examine a partial line and provide attr list of final expr"""

    line = re.split(r"\s", request.data)[-1].strip()
    # Support lines like "thing.attr" as "thing.", because the browser
    # may not finish calculating the partial line until after the user
    # has clicked on a few more keys.
    line = ".".join(line.split(".")[:-1])
    try:
        borg_console = interpreter.BorgConsole()
        result = eval("dir(%s)" % line, {}, borg_console.__dict__['locals'])
        result = repr(result)
    except:
        result = "Module or method not found."

    # have to convert the list to a string
    request.send_response(200)
    request.end_headers()
    request.wfile.write(result)
    request.wfile.flush()

def doc_handler(request):
    """Examine a partial line and provide sig+doc of final expr."""

    line = re.split(r"\s", request.data)[-1].strip()
    # Support lines like "func(text" as "func(", because the browser
    # may not finish calculating the partial line until after the user
    # has clicked on a few more keys.
    line = "(".join(line.split("(")[:-1])
    try:
        borg_console = interpreter.BorgConsole()
        result = eval(line, {}, borg_console.__dict__['locals'])
        try:
            if isinstance(result, type):
                func = result.__init__
            else:
                func = result
            args, varargs, varkw, defaults = inspect.getargspec(func)
        except TypeError:
            if callable(result):
                doc = getattr(result, "__doc__", "") or ""
                return "%s\n\n%s" % (line, doc)
            return None
    except:
        return ('%s is not defined yet')%line

    if args and args[0] == 'self':
        args.pop(0)
    missing = object()
    defaults = defaults or []
    defaults = ([missing] * (len(args) - len(defaults))) + list(defaults)
    arglist = []
    for a, d in zip(args, defaults):
        if d is missing:
            arglist.append(a)
        else:
            arglist.append("%s=%s" % (a, d))
    if varargs:
        arglist.append("*%s" % varargs)
    if varkw:
        arglist.append("**%s" % varkw)
    doc = getattr(result, "__doc__", "") or ""
    result = "%s(%s)\n%s" % (line, ", ".join(arglist), doc)

    request.send_response(200)
    request.end_headers()
    request.wfile.write(result)
    request.wfile.flush()

def help_handler(request):
    """Provide help documentation.
    Currently, it uses stdout. Ideally, it will use a scrollable iframe"""
    push_input(request)

# css
tooltip_css = """
.interp_tipbar {
    position: fixed;
    top: 10px;
    right: 10px;
    width: 50%;  
    border: 2px outset #DDCCBB;
    background-color: #FFEEDD;
    font: 9pt monospace;
    margin: 0;
    padding: 4px;
    white-space: -moz-pre-wrap; /* Mozilla, supported since 1999 */
    white-space: -pre-wrap; /* Opera 4 - 6 */
    white-space: -o-pre-wrap; /* Opera 7 */
    white-space: pre-wrap; /* CSS3 - Text module (Candidate Recommendation)
                            http://www.w3.org/TR/css3-text/#white-space */
    word-wrap: break-word; /* IE 5.5+ */
    display: none;  /* will appear only when needed */
        z-index:11;
}
"""

# javascript code
tooltip_js = """

var session_id = "%s";

"""%CrunchyPlugin.session_random_id