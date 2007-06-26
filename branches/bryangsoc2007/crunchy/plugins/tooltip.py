"""This plugin provides tooltips for interpreters"""

import CrunchyPlugin

from element_tree import ElementTree
et = ElementTree

# these have yet to be implemented
provides = set(["/dir","/doc"])

# what to insert
#<div class="interp_tipbar" id="code3_tipbar"> </div>
# onkeypress="interp_trapkeys(event, &quot;code3&quot;,&quot;Waiting...&quot;)"

def register():
    # register service, /dir, and /doc
    CrunchyPlugin.register_service(insert_tooltip, "insert_tooltip")
    CrunchyPlugin.register_http_handler("/dir%s"%CrunchyPlugin.session_random_id, dir_handler)
    CrunchyPlugin.register_http_handler("/doc%s"%CrunchyPlugin.session_random_id, doc_handler)

def insert_tooltip(page, elem, uid):
    print 'called insert_tooltip'

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

        #append_html
        #append_html(get_pageid(), io_id, dialog_html)

def dir_handler(request):
    # send dir response
    content = "dir_response"
    request.send_response(200)
    request.end_headers()
    request.wfile.write(content)
    request.wfile.flush()

def doc_handler(request):
    # send doc response
    content = "doc_response"
    request.send_response(200)
    request.end_headers()
    request.wfile.write(content)
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

# javascript code
tooltip_js = """

var session_id = "%s";

/*------------------------------- interpreter-------------------------------- */
// "waiting" is a translatable string passed as a variable.
function interp_trapkeys(event, interp_id, waiting){
    switch(event.keyCode){
        case 13:
            hide_tipbar(interp_id);
            //interp_push(interp_id, waiting);
            break;
        case 48:    //close )
        case 8:    // backspace
          hide_tipbar(interp_id);
          break;
      case 57:  // open paren "("
            interp_doc(interp_id);
            break;
        case 190:  // period "."
            interp_dir(interp_id);
            break;
            // attempting to solve problem on Mac
        case 0:
            switch(event.charCode){
                case 40: // open paren "("
                    interp_doc_mac(interp_id);
                    break;
                case 41: // close )
                    hide_tipbar(interp_id);
                    break;
                case 46:  // period "."
                    interp_dir_mac(interp_id);
                    break;
                };
            break;
    };
};

// removed interp_push()

function show_tipbar(interp_id){
    tipbar = document.getElementById("tipbar_"+interp_id);
    tipbar.style.display = "block";
};

function hide_tipbar(interp_id){
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

function interp_doc_mac(interp_id) {
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

function interp_dir(interp_id) {
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

function interp_dir_mac(interp_id) {
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