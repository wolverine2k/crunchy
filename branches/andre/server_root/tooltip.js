/*------------------------------- tooltip -------------------------------- */

function tooltip_display(event, interp_id) {
	// help menu prevents tooltip from displaying
    if (document.getElementById("help_menu").style.display == "block") {
	    return;
    }
    inputBox = document.getElementById("in_"+interp_id);

    switch(event.keyCode) {
        case 13:    // enter
        case 27:    // escape
        case 48:    // close )
        //case 8:     // backspace
            hide_tooltip();
            break;
        case 57:  // open paren "("
            tooltip_doc(interp_id, inputBox.value.substring(0, inputBox.selectionEnd));
            break;
        case 190:  // period "."
            tooltip_dir(interp_id, inputBox.value.substring(0, inputBox.selectionEnd));
            break;

        // win32 safari
        case 40: // open paren "("
            tooltip_doc(interp_id, inputBox.value + "(");
            break;
        case 41: // close )
            hide_tooltip();
            break;
        case 46:  // period "."
            tooltip_dir(interp_id, inputBox.value + ".");
            break;

            // attempting to solve problem on Mac
        case 0:
            switch(event.charCode) {
                case 40: // open paren "("
                    tooltip_doc(interp_id, inputBox.value + "("); // mac safari - untested
                    break;
                case 41: // close )
                    hide_tooltip();
                    break;
                case 46:  // period "."
                    tooltip_dir(interp_id, inputBox.value + "."); // mac safari - untested
                    break;
                };
            break;
    };
};

function hide_help() {
    var help_menu = document.getElementById("help_menu");
    help_menu.style.display = "none";
    //document.getElementById("help_menu").style.display = "none";
    help_menu.style.position = "fixed";
    help_menu.style.top = "70px";
    help_menu.style.right = "5px";
    

    
    hide_tooltip();
};

function hide_tooltip() {
    document.getElementById("help_menu_x").style.display = "none";
    var tool_tip = document.getElementById("tooltip");
    tool_tip.style.display = "none";
    tool_tip.innerHTML = " ";

    tool_tip.style.position = "fixed";
    tool_tip.style.top = "70px";
    tool_tip.style.right = "5px";

};

function show_tooltip(tipText) {
    document.getElementById("help_menu").style.display = "none";
    document.getElementById("help_menu_x").style.display = "block";
    document.getElementById("tooltip").appendChild(document.createTextNode(tipText));
    document.getElementById("tooltip").style.display = "block";
}

function tooltip_doc(interp_id, data) {
	hide_tooltip();

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
                    show_tooltip(h.responseText);
                    document.getElementById("in_"+interp_id).focus();
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
    h.open("POST", "/doc"+session_id+"?uid="+interp_id, true);
    h.send(encodeURIComponent(data));
};

function tooltip_dir(interp_id, data) {
	hide_tooltip();

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
                    show_tooltip(h.responseText);
                    document.getElementById("in_"+interp_id).focus();
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
    h.open("POST", "/dir"+session_id+"?uid="+interp_id, true);
    h.send(encodeURIComponent(data));
};

function convertFromEditor(uid){
    outputSpan = document.getElementById("out_"+uid);
    editor = document.getElementById("code_" + uid);
    outputSpan.parentNode.removeChild(editor);
    exec_button = document.getElementById("exec_but_"+uid);
    outputSpan.parentNode.removeChild(exec_button);
    newReturn = document.getElementById("br_"+uid);
    outputSpan.parentNode.removeChild(newReturn);
    document.getElementById("ed_link_"+uid).style.backgroundColor = "white";
};

function convertToEditor(elm, exec_btn_label) {
    theID = elm.id.substring(8);
    if (elm.style.backgroundColor == "red"){
       return convertFromEditor(theID);
    }
    elm.style.backgroundColor = "red";

    newEditor = document.createElement('textarea');
    newEditor.cols = "80";
    newEditor.rows = "10";
    newEditor.id = "code_" + theID;
    inp = document.getElementById("in_" + theID);

    newEditor.style.backgroundColor = "#eff";
    newEditor.style.fontWeight = "bold";

    execButton = document.createElement('button');
    execButton.appendChild(document.createTextNode(exec_btn_label));
    execButton.onclick = function () { push_input(theID) };
    execButton.id = "exec_but_" + theID;
    
    newReturn = document.createElement('br');
    newReturn.id = "br_" + theID;

    outputSpan = document.getElementById("out_"+theID);
    outputSpan.parentNode.appendChild(newEditor);
    outputSpan.parentNode.appendChild(newReturn);
    outputSpan.parentNode.appendChild(execButton);
    
    newEditor.value = document.getElementById("code_sample_" + theID).value;
};

/* The following has been adapted from http://dunnbypaul.net/js_mouse/   
   to make resizable tooltips; references to IE have been removed from original*/
   
var mousex = 0;
var mousey = 0;
var elex = 0;

var dragobj = null;

function falsefunc() { return false; } // used to block cascading events

function getMouseXY(e)
{ 
  if (e)
  { 
      mousex = e.pageX;
      mousey = e.layerY;
  }
};

function grab(context)
{
  document.onmousedown = falsefunc; // in NS this prevents cascading of events, 
  dragobj = context;
  dragobj.style.cursor = "ne-resize";
  document.onmousemove = drag;
  document.onmouseup = drop;
  getMouseXY();
};

function drag(e) // parameter passing is important for NS family 
{
  if (dragobj)
  {
    elex = document.width - mousex;
    dragobj.style.width = (elex).toString(10) + 'px';
    dragobj.style.height = (mousey).toString(10) + 'px';
  }
  getMouseXY(e);
};

function drop()
{
  if (dragobj)
  {
    dragobj = null;
  }
  getMouseXY();
  document.onmousemove = getMouseXY;
  document.onmouseup = null;
  document.onmousedown = null;   // re-enables text selection on NS
};