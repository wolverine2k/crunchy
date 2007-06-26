"""This plugin provides tooltips for interpreters"""

import CrunchyPlugin
import interpreter
import re
from element_tree import ElementTree
et = ElementTree

provides = set(["/dir","/doc"])

def register():
    # register service, /dir, and /doc
    CrunchyPlugin.register_service(insert_tooltip, "insert_tooltip")
    CrunchyPlugin.register_http_handler("/dir%s"%CrunchyPlugin.session_random_id, dir_handler)
    CrunchyPlugin.register_http_handler("/doc%s"%CrunchyPlugin.session_random_id, doc_handler)

def insert_tooltip(page, elem, uid):
    # add div for displaying the tooltip
    tipbar = et.SubElement(elem, "div")
    tipbar.attrib["id"] = "tipbar_" + uid
    tipbar.attrib["class"] = "interp_tipbar"

    if not page.includes("tooltip_included"):
        print 'tooltip_included'
        page.add_include("tooltip_included")
        page.add_js_code(tooltip_js)
        page.add_css_code(tooltip_css)

        # move javascript into a seperate file perhaps?
        #page.insert_js_file("/tooltip/tooltip.js")

def get_global_dir(line):
    """Examine a partial line and provide attr list of final expr without self.locals."""
    line = re.split(r"\s", line)[-1].strip()
    # Support lines like "thing.attr" as "thing.", because the browser
    # may not finish calculating the partial line until after the user
    # has clicked on a few more keys.
    line = ".".join(line.split(".")[:-1])
    try:
        result = eval("dir(%s)" % line, {})
    except:
        return []
    return result

def dir_handler(request):
    # return tooltip function list (after typing '.')
    #result = interpreters.interps[request.args['name']].dir(request.args["line"])
    result = get_global_dir(request.args["amp;line"])
    if result == None:
        request.send_response(204)
        request.end_headers()
    else:
        #have to convert the list to a string
        result = repr(result)
        request.send_response(200)
        request.end_headers()
        request.wfile.write(result)
        request.wfile.flush()

def doc_handler(request):
    # return tooltip function definition (after typing '(')
    #result = interpreters.interps[request.args['name']].doc(request.args["line"])
    result = 'Requested '+request.args["amp;line"]
    if not result:
        request.send_response(204)
        request.end_headers()
    else:
        request.send_response(200)
        request.end_headers()
        request.wfile.write(result)
        request.wfile.flush()

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

# THIS CODE IS COPIED FROM THE OLD INTERPRETERS.PY
def dir(self, line):
    """Examine a partial line and provide attr list of final expr."""
    line = re.split(r"\s", line)[-1].strip()
    # Support lines like "thing.attr" as "thing.", because the browser
    # may not finish calculating the partial line until after the user
    # has clicked on a few more keys.
    line = ".".join(line.split(".")[:-1])
    try:
        result = eval("dir(%s)" % line, {}, self.locals)
    except:
        return []
    return result

def doc(self, line):
    """Examine a partial line and provide sig+doc of final expr."""
    line = re.split(r"\s", line)[-1].strip()
    # Support lines like "func(text" as "func(", because the browser
    # may not finish calculating the partial line until after the user
    # has clicked on a few more keys.
    line = "(".join(line.split("(")[:-1])
    try:
        result = eval(line, {}, self.locals)
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
        return _('%s is not defined yet')%line

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
    return "%s(%s)\n%s" % (line, ", ".join(arglist), doc)

# javascript code
tooltip_js = """

var session_id = "%s";

/*------------------------------- tooltip -------------------------------- */

function tooltip_display(event, interp_id, waiting) {
    switch(event.keyCode) {
    	// BUG: pressing 'escape' breaks crunchy interpreter
        case 27:    // escape
        case 13:    // enter
        case 48:    // close )
        case 8:     // backspace
          hide_tipbar(interp_id);
          break;
      case 57:  // open paren "("
            tooltip_doc(interp_id);
            break;
        case 190:  // period "."
            tooltip_dir(interp_id);
            break;
            // attempting to solve problem on Mac
        case 0:
            switch(event.charCode) {
                case 40: // open paren "("
                    tooltip_doc_mac(interp_id);
                    break;
                case 41: // close )
                    hide_tipbar(interp_id);
                    break;
                case 46:  // period "."
                    tooltip_dir_mac(interp_id);
                    break;
                };
            break;
    };
};

function show_tipbar(interp_id) {
    tipbar = document.getElementById("tipbar_"+interp_id);
    tipbar.style.display = "block";
};

function hide_tipbar(interp_id) {
    tipbar = document.getElementById("tipbar_"+interp_id);
    tipbar.style.display = "none";
    tipbar.innerHTML = " ";
};

function interp_doc(interp_id) {
    input = document.getElementById("in_"+interp_id);
    end = input.selectionEnd;    
    data = input.value.substring(0, end);
    tipbar = document.getElementById("tipbar_"+interp_id);
    hide_tipbar(interp_id);
   
    h = new XMLHttpRequest();
    h.onreadystatechange = function() {
        if (h.readyState == 4) {
            try {
                var status = h.status;
            } catch(e) {
                var status = "NO HTTP RESPONSE";
            }
            switch (status) {
                case 200:
                    tipbar.appendChild(document.createTextNode(h.responseText));
                    //alert("tipping: "+h.responseText);
                    show_tipbar(interp_id);
                    input.focus();
                    break;
                // Internet Explorer might return 1223 for 204
                case 1223:
                case 204:
                    // No tips available
                    break;
                case 12029:
                    // Internet Explorer client could not connect to server
                    status = "NO HTTP RESPONSE";
                default:
                    alert(status + "\\n" + h.responseText, false);
            }
        }
    }
    h.open("GET", "/doc"+session_id+"?name="+interp_id+"&line=" + encodeURIComponent(data), true);
    h.send(null);
};

function tooltip_doc_mac(interp_id) {
    input = document.getElementById("in_"+interp_id);
    data = input.value + "(";
    tipbar = document.getElementById("tipbar_"+interp_id);
    hide_tipbar(interp_id);
   
    h = new XMLHttpRequest();
    h.onreadystatechange = function() {
        if (h.readyState == 4) {
            try {
                var status = h.status;
            } catch(e) {
                var status = "NO HTTP RESPONSE";
            }
            switch (status) {
                case 200:
                    tipbar.appendChild(document.createTextNode(h.responseText));
                    show_tipbar(interp_id);
                    input.focus();
                    break;
                // Internet Explorer might return 1223 for 204
                case 1223:
                case 204:
                    // No tips available
                    break;
                case 12029:
                    // Internet Explorer client could not connect to server
                    status = "NO HTTP RESPONSE";
                default:
                    alert(status + "\\n" + h.responseText, false);
            }
        }
    }
    h.open("GET", "/doc"+session_id+"?name="+interp_id+"&line=" + encodeURIComponent(data), true);
    h.send(null);
};

function tooltip_dir(interp_id) {
    input = document.getElementById("in_"+interp_id);
    end = input.selectionEnd;    
    data = input.value.substring(0, end);
    tipbar = document.getElementById("tipbar_"+interp_id);
    hide_tipbar(interp_id);
   
    h = new XMLHttpRequest();
    h.onreadystatechange = function() {
        if (h.readyState == 4) {
            try {
                var status = h.status;
            } catch(e) {
                var status = "NO HTTP RESPONSE";
            }
            switch (status) {
                case 200:
                    tipbar.appendChild(document.createTextNode(h.responseText));
                    show_tipbar(interp_id);
                    input.focus();
                    break;
                // Internet Explorer might return 1223 for 204
                case 1223:
                case 204:
                    // No tips available
                    break;
                case 12029:
                    // Internet Explorer client could not connect to server
                    status = "NO HTTP RESPONSE";
                default:
                    alert(status + "\\n" + h.responseText, false);
            }
        }
    }
    h.open("GET", "/dir"+session_id+"?name="+interp_id+"&line=" + encodeURIComponent(data), true);
    h.send(null);
};

function tooltip_dir_mac(interp_id) {
    input = document.getElementById("in_"+interp_id);
    data = input.value + ".";
    tipbar = document.getElementById("tipbar_"+interp_id);
    hide_tipbar(interp_id);
   
    h = new XMLHttpRequest();
    h.onreadystatechange = function() {
        if (h.readyState == 4) {
            try {
                var status = h.status;
            } catch(e) {
                var status = "NO HTTP RESPONSE";
            }
            switch (status) {
                case 200:
                    tipbar.appendChild(document.createTextNode(h.responseText));
                    show_tipbar(interp_id);
                    input.focus();
                    break;
                // Internet Explorer might return 1223 for 204
                case 1223:
                case 204:
                    // No tips available
                    break;
                case 12029:
                    // Internet Explorer client could not connect to server
                    status = "NO HTTP RESPONSE";
                default:
                    alert(status + "\\n" + h.responseText, false);
            }
        }
    }
    h.open("GET", "/dir"+session_id+"?name="+interp_id+"&line=" + encodeURIComponent(data), true);
    h.send(null);
};

"""%CrunchyPlugin.session_random_id