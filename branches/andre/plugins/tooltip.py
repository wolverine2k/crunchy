"""This plugin provides tooltips for interpreters"""

import CrunchyPlugin
import interpreter
import re
import urllib

from element_tree import ElementTree
et = ElementTree

borg_console = interpreter.BorgConsole()

provides = set(["/dir","/doc","/help"])

def register():
    # register service, /dir, /doc, and /help
    CrunchyPlugin.register_service(insert_tooltip, "insert_tooltip")
    CrunchyPlugin.register_http_handler("/dir%s"%CrunchyPlugin.session_random_id, dir_handler)
    CrunchyPlugin.register_http_handler("/doc%s"%CrunchyPlugin.session_random_id, doc_handler)
    CrunchyPlugin.register_http_handler("/help%s"%CrunchyPlugin.session_random_id, help_handler)

def insert_tooltip(page, elem, uid):
    # add span for displaying the tooltip - using div messes things up; avoid!
    tipbar = et.SubElement(elem, "span")
    tipbar.attrib["id"] = "tipbar_" + uid
    tipbar.attrib["class"] = "interp_tipbar"

    if not page.includes("tooltip_included") and page.body:
        page.add_include("tooltip_included")
        page.insert_js_file("/tooltip.js")
        page.add_js_code(tooltip_js)
        page.add_css_code(tooltip_css)

        help_menu = et.Element("div")
        help_menu.attrib["id"] = "help_menu"
        help_menu.text = " "
        page.body.append(help_menu)

        help_menu_x = et.Element("div")
        help_menu_x.attrib["id"] = "help_menu_x"
        help_menu_x.attrib["onclick"] = "hide_helpers()"
        help_menu_x.text = "X"
        page.body.append(help_menu_x)

def dir_handler(request):
    """Examine a partial line and provide attr list of final expr"""

    line = re.split(r"\s", request.data)[-1].strip()
    # Support lines like "thing.attr" as "thing.", because the browser
    # may not finish calculating the partial line until after the user
    # has clicked on a few more keys.
    line = ".".join(line.split(".")[:-1])
    try:
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

    line = re.split(r"\s", urllib.unquote_plus(request.data))[-1].strip()
    # Support lines like "func(text" as "func(", because the browser
    # may not finish calculating the partial line until after the user
    # has clicked on a few more keys.
    line = "(".join(line.split("(")[:-1])
    if line in borg_console.__dict__['locals']:
        result = "%s()\n %s"%(line, borg_console.__dict__['locals'][line].__doc__)
    elif '__builtins__' in borg_console.__dict__['locals']:
        if line in borg_console.__dict__['locals']['__builtins__']:
            result = "%s()\n %s"%(line, borg_console.__dict__['locals']['__builtins__'][line].__doc__)
        else:
            result = "%s() not defined"%line
    else:
        result = "builtins not defined in console yet."

    request.send_response(200)
    request.end_headers()
    request.wfile.write(result)
    request.wfile.flush()
    return

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
    padding-right: 30px;
    white-space: -moz-pre-wrap; /* Mozilla, supported since 1999 */
    white-space: -pre-wrap; /* Opera 4 - 6 */
    white-space: -o-pre-wrap; /* Opera 7 */
    white-space: pre-wrap; /* CSS3 - Text module (Candidate Recommendation)
                            http://www.w3.org/TR/css3-text/#white-space */
    word-wrap: break-word; /* IE 5.5+ */
    display: none;  /* will appear only when needed */
    z-index:11;
}
#help_menu {
    position: fixed;
    top: 10px;
    right: 10px;
    width: 50%;
    height: 50%;
    overflow:auto;
    border: 1px solid #000000;
    background-color: #FFEEDD;
    font: 9pt monospace;
    margin: 0;
    padding: 4px;
    padding-right: 10px;
    white-space: -moz-pre-wrap; /* Mozilla, supported since 1999 */
    white-space: -pre-wrap; /* Opera 4 - 6 */
    white-space: -o-pre-wrap; /* Opera 7 */
    white-space: pre-wrap; /* CSS3 - Text module (Candidate Recommendation)
                            http://www.w3.org/TR/css3-text/#white-space */
    word-wrap: break-word; /* IE 5.5+ */
    display: none;  /* will appear only when needed */
    z-index:11;
}
#help_menu_x {
    position: fixed;
    top: 15px;
    right: 30px;
    color: red;
    background-color: #FFEEDD;
    font: 12pt monospace;
    cursor: pointer;
    padding: 0px;
    display: none;  /* will appear only when needed */
    z-index:12;
}
"""

# javascript code
tooltip_js = """

var session_id = "%s";

"""%CrunchyPlugin.session_random_id