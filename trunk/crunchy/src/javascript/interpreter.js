// Andre Roberge: adapted from httprepl.html by Robert Brewer 
///////////////////////////////////////////
//
//  IMPORTANT: this file is no longer used by Crunchy.  However, it
//  does have some functionality (e.g. command history) that we might
//  want to reintroduce later.  While we could delete it and rely on
//  the repository to retrieve it later, we'll keep it here for now,
//  probably until version 1.0
/////////////////////////////////////////

function http() {
    var h;
    if (typeof(XMLHttpRequest) != "undefined") {
        h = new XMLHttpRequest();
    } else {
        try { h = new ActiveXObject("Msxml2.XMLHTTP"); }
        catch (e) {
            try { h = new ActiveXObject("Microsoft.XMLHTTP"); }
            catch (E) { alert("Your browser is not supported."); }
        }
    }
    return h
}
//                           HISTORY NAVIGATION                           //
function use_history(elem) {
    var content = get_text(elem);
    // Strip the leading prompt
    if (elem.className == 'stdin') content = content.substr(4);
    input.value = content;
    input.focus();
}
function history_hook() {
    use_history(this);
}
var current_history = undefined;
function prev_history() {
    if (current_history == undefined) {
        var prev = document.getElementById("output").lastChild;
    } else {
        var prev = current_history.previousSibling;
    }
    while (prev != null && prev.className != 'stdin') {
        prev = prev.previousSibling;
    }
    if (prev != null) {
        current_history = prev;
        use_history(prev);
    }
}
function next_history() {
    if (current_history == undefined) return;
   
    var next = current_history.nextSibling;
    while (next != null && next.className != 'stdin') {
        next = next.nextSibling;
    }
    if (next != null) {
        current_history = next;
        use_history(next);
    }
}
//                            CODE COMPLETION                            //
current_range = undefined;
function partial_line() {
    if (document.selection) {
        // Internet Explorer
        current_range = document.selection.createRange();
        var end = current_range.getBookmark().charCodeAt(2) - 2;
    } else {
        var end = input.selectionEnd;
    }
    return input.value.substring(0, end);
}
function insert_text(newtext) {
    if (document.selection) {
        // Internet Explorer
        current_range.text = newtext;
        current_range.select();
    } else {
        var start = input.selectionStart;
        input.value = input.value.substring(0, start) + newtext + input.value.substr(input.selectionEnd);
        var end = start + newtext.length;
        input.setSelectionRange(end, end);
    }
}
function clear_tips() {
    tipbar.style.display = '';
    while (tipbar.hasChildNodes()) {
        tipbar.removeChild(tipbar.lastChild);
    }
}
function show_tips() {
    tipbar.style.display = 'block';
}
var intip = false;
function use_tip() {
    insert_text(get_text(this));
    clear_tips();
    intip = true;
    input.focus();
}
function dir() {
    var data = partial_line();
   
    clear_tips();
   
    var h = http();
    h.onreadystatechange = function() {
        if (h.readyState == 4) {
            try {
                var status = h.status;
            } catch(e) {
                var status = "NO HTTP RESPONSE";
            }
            switch (status) {
                case 200:
                    var tips = eval(h.responseText);
                    for (var i=0; i < tips.length; i++) {
                        var tiplink = document.createElement("a");
                        tiplink.onclick = use_tip;
                        tiplink.href = "javascript:void(0)";
                        set_text(tiplink, tips[i]);
                        tipbar.appendChild(tiplink);
                        tipbar.appendChild(document.createTextNode(" "));
                    }
                    show_tips()
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
                    stdout_write(status + "\n" + h.responseText, false);
            }
        }
    }
    h.open("GET", "/dir?line=" + encodeURIComponent(data), true);
    h.send(null);
}
function doc() {
    var data = partial_line();
   
    clear_tips();
   
    var h = http();
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
                    show_tips();
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
                    stdout_write(status + "\n" + h.responseText, false);
            }
        }
    }
    h.open("GET", "/doc?"+"line=" + encodeURIComponent(data), true);
    h.send(null);
}
//                           COMMAND EXECUTION                           //
function get_text(elem) {
    if (elem.innerText != undefined) {
        // Internet Explorer
        return elem.innerText;
    } else {
        // Mozilla
        return elem.textContent;
    }
}
function set_text(elem, newvalue) {
    if (elem.innerText != undefined) {
        // Internet Explorer
        elem.innerText = newvalue;
    } else {
        // Mozilla
        elem.textContent = newvalue;
    }
}

function stdout_write(content, stdin) {
    current_history = undefined;
    if (content == "") return;
   
    var block = document.createElement("pre");
    block.ondblclick = history_hook;
    if (stdin) {
        content = get_prompt() + content;
        block.className = 'stdin';
    }
    if (block.innerText != undefined) {
        // Internet Explorer quirkiness
        block.innerText = content;
    } else {
        block.appendChild(document.createTextNode(content));
    }
    output.appendChild(block);
}
whitespace = /^\s+$/;
function push() {
    var data = input.value;
    // Uncomment to treat a line with only whitespace like a blank line
    // if (whitespace.test(data)) data = "";
   
    input.value = "";
   
    var h = http();
    h.onreadystatechange = function() {
        if (h.readyState == 4) {
            stdout_write(data, true);
            try {
                var status = h.status;
            } catch(e) {
                var status = "NO HTTP RESPONSE";
            }
            switch (status) {
                case 200:
                    set_prompt(">>> ");
                    stdout_write(h.responseText, false);
                    break;
                // Internet Explorer might return 1223 for 204
                case 1223:
                case 204:
                    set_prompt("... ");
                    // input.value *should* be blank, but just in case...
                    input.value = "    " + input.value;
                    break;
                case 12029:
                    // Internet Explorer client could not connect to server
                    status = "NO HTTP RESPONSE";
                default:
                    stdout_write(status + "\n" + h.responseText, false);
            }
            input.focus();
        }
    }
    h.open("POST", "push", true);
    h.send(data);
}

//                                 SETUP                                 //
function mapKeys(key_code) {
    if (intip) {
        intip = false;
        // Trap the bubbling keyup event from a tiplink. This means that,
        // if you actually click a tiplink instead of tab and hit 'enter',
        // you have to hit 'enter' twice to push the line. :(
        if (key_code == 13) return;
    }
    switch(key_code) {
        case 8:    // backspace
            clear_tips();
            break;
        case 13:   // enter
            clear_tips();
            push();
            break;
        case 38:   // up arrow
            prev_history();
            break;
        case 40:   // down arrow
            next_history();
            break;
        case 48:  // close paren ")"
            clear_tips();
            break;
        case 57:  // open paren "("
            doc();
            break;
        case 190:  // period "."
            dir();
            break;
    }
}
function trapKeys(e) {
    if (!e) var e = window.event;
    mapKeys(e.keyCode);
}

function get_prompt() {
    return get_text(document.getElementById("prompt"));
}
function set_prompt(newvalue) {
    var p = document.getElementById("prompt");
    set_text(p, newvalue);
}

function init() {
    input = document.getElementById("input");
    input.onkeyup = trapKeys;
    output = document.getElementById("output");
    tipbar = document.getElementById("tipbar");
    //input.focus();
}
