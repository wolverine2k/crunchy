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
    document.getElementById("help_menu").style.display = "none";
    hide_tooltip();
};

function hide_tooltip() {
    document.getElementById("help_menu_x").style.display = "none";
    document.getElementById("tooltip").style.display = "none";
    document.getElementById("tooltip").innerHTML = " ";
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

    inp = document.getElementById("in_"+uid);
    inp.style.display = 'inline';
    parentElm = inp.parentNode;
    outputSpan = document.getElementById("out_"+theID);
    editor = document.getElementById("code_" + uid);
    outputSpan.parentNode.removeChild(editor);
    exec_button = document.getElementById("exec_but_"+uid);
    outputSpan.parentNode.removeChild(exec_button);
    copy_button = document.getElementById("copy_but_"+uid);
    outputSpan.parentNode.removeChild(copy_button);
};

function convertToEditor(elm, exec_btn_label, copy_btn_label) {
    theID = elm.id.substring(3);

    newEditor = document.createElement('textarea');
    newEditor.cols = "80";
    newEditor.rows = "10";
    newEditor.id = "code_" + theID;
    newEditor.value = elm.value;
    newEditor.style.backgroundColor = "#eff";

    execButton = document.createElement('button');
    execButton.appendChild(document.createTextNode(exec_btn_label));
    execButton.onclick = function () { push_input(theID) };
    execButton.id = "exec_but_" + theID;
    
    copyButton = document.createElement('button');
    copyButton.appendChild(document.createTextNode(copy_btn_label));
    copyButton.onclick = function () { copyCodeSample(theID) };
    copyButton.id = "copy_but_" + theID;  

    parentElm = elm.parentNode;
    elm.style.display = 'none';
    outputSpan = document.getElementById("out_"+theID);
    // remove last prompt
    outputSpan.parentNode.appendChild(newEditor);
    outputSpan.parentNode.appendChild(document.createElement('br'));
    outputSpan.parentNode.appendChild(execButton);
    outputSpan.parentNode.appendChild(copyButton);
};

function copyCodeSample(uid){
    editor = document.getElementById("code_"+ uid);
    //sample = document.getElementById("code_sample_" +uid);
    editor.value = document.getElementById("code_sample_" +uid).value;
};