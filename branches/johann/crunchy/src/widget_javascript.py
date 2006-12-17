"""Javascript code for the various widgets"""

__common = r"""
function get_http()
// get an xmlhttprequest object
{
    var h;
    if (typeof(XMLHttpRequest) != "undefined") 
    {
        h = new XMLHttpRequest();
    } 
    else 
    {
        alert("Your Browser is currently unsupported, you need Firefox 1.5+");
    }
    return h;
};

interpreters = {};

function create_output_widget(objid){
    //create the output widget
    new_output = document.createElement("pre");
    new_output.id = objid + "_output";
    parent = document.getElementById(objid+"_output_container");
    try{
        t = document.getElementById(objid+"_output");
        parent.replaceChild(new_output, t);
        }
    catch(e) {
        //alert(e);
        parent.appendChild(new_output);
        };
    sendNotification(objid);
};
"""

interpreter = r"""
function interp_trapkeys(event, interp_id){
    //alert("trapkeys")
    switch(event.keyCode){
        case 13:
            //tipbar currently disabled :(
            //hide_tipbar(interp_id);
            interp_push(interp_id);
            break;
        case 48:     //close )
        case 8:    // backspace
          //hide_tipbar(interp_id);
          break;
      case 57:  // open paren "("
            interp_doc(interp_id);
            break;
        case 190:  // period "."
            interp_dir(interp_id);
            break;
    
    };
};

function interp_push(interp_id){
    input = document.getElementById(interp_id+"_input");
    outputcont = document.getElementById(interp_id+"_output_container");
    prompt = document.getElementById(interp_id+"_prompt");
    echoprompt = document.createElement("span");
    echoprompt.setAttribute("class", "stdin");
    echoprompt.textContent = prompt.textContent;
    outputcont.appendChild(echoprompt);
    s = document.createElement("span");
    s.setAttribute("class", "stdin");
    s.textContent = input.value;
    outputcont.appendChild(s);
    br = document.createElement("br");
    outputcont.appendChild(br);
    output = document.createElement("div");
    output.setAttribute("class", "interp_output");
    output.textContent = "waiting...";
    outputcont.appendChild(output);
    data = input.value;    
    input.value = "";
    var h = get_http();
    h.onreadystatechange = function() {
        if (h.readyState == 4) {
            try {
                var status = h.status;
            } catch(e) {
                var status = "NO HTTP RESPONSE";
            }
            switch (status) {
                case 200:
                    prompt.textContent= ">>> ";
                    output.textContent = h.responseText;
                    break;
                // Internet Explorer might return 1223 for 204
                case 1223:
                case 204:
                    prompt.textContent= "... ";
                    output.textContent= '';
                    // input.value *should* be blank, but just in case...
                    input.value = "    " + input.value;
                    break;
                case 12029:
                    // Internet Explorer client could not connect to server
                    status = "NO HTTP RESPONSE";
                default:
                    output.textContent = status + "\n" + h.responseText, false;
            }
            input.focus();
        }
    };
    h.open("POST", "/push"+session_id+"?"+interp_id, true);
    h.send(data);
};

function show_tipbar(interp_id){
    tipbar = document.getElementById(interp_id+"_tipbar");
    tipbar.style.display = "block";
};

function hide_tipbar(interp_id){
    tipbar = document.getElementById(interp_id+"_tipbar");
    tipbar.style.display = "none";
    tipbar.innerHTML = " ";
};

function interp_doc(interp_id) {
    input = document.getElementById(interp_id+"_input");
     end = input.selectionEnd;    
    data = input.value.substring(0, end);
    //tipbar = document.getElementById(interp_id+"_tipbar");
    //hide_tipbar(interp_id);
   
    h = get_http();
    h.onreadystatechange = function() {
        if (h.readyState == 4) {
            try {
                var status = h.status;
            } catch(e) {
                var status = "NO HTTP RESPONSE";
            }
            switch (status) {
                case 200:
                    //tipbar.appendChild(document.createTextNode(h.responseText));
                    //show_tipbar(interp_id);
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
                    alert(status + "\n" + h.responseText, false);
            }
        }
    }
    h.open("GET", "/doc"+session_id+"?name="+interp_id+"&line=" + encodeURIComponent(data), true);
    h.send(null);
};

function interp_dir(interp_id) {
    input = document.getElementById(interp_id+"_input");
     end = input.selectionEnd;    
    data = input.value.substring(0, end);
    //tipbar = document.getElementById(interp_id+"_tipbar");
    //hide_tipbar(interp_id);
   
    h = get_http();
    h.onreadystatechange = function() {
        if (h.readyState == 4) {
            try {
                var status = h.status;
            } catch(e) {
                var status = "NO HTTP RESPONSE";
            }
            switch (status) {
                case 200:
                    //tipbar.appendChild(document.createTextNode(h.responseText));
                    //show_tipbar(interp_id);
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
                    alert(status + "\n" + h.responseText, false);
            }
        }
    }
    h.open("GET", "/dir"+session_id+"?name="+interp_id+"&line=" + encodeURIComponent(data), true);
    h.send(null);
};


"""

editor = r"""
function exec_external(id)
{
    data = document.getElementById(id + "_code").value;
    h = get_http();
    h.open("POST", "/spawn"+session_id, true);
    h.send(data);
};
// with terminal/console window: this might make sense only for Windows.
function exec_external_console(id)
{
    data = document.getElementById(id + "_code").value;
    h = get_http();
    h.open("POST", "/spawn_console"+session_id, true);
    h.send(data);
};

function exec_by_id(objid)
{
    codebox = document.getElementById(objid + "_code");
    interpreters[objid] = 1;
    code = codebox.value;
    h = get_http();
    h.onreadystatechange = function()
        {
            if (h.readyState == 4) 
            {
                try
                {
                    var status = h.status;
                }
                catch(e)
                {
                    var status = "NO HTTP RESPONSE";
                }
                switch (status)
                {
                case 200:
                    create_output_widget(objid);
                    break;
                default:
                    alert(status + ": " + h.responseText);
                }
            }
        };
    h.open("POST", "/execute"+session_id+"?"+objid, true);
    h.send(code);
}

function doctest_by_id(objid)
{
    codebox = document.getElementById(objid + "_code");
    interpreters[objid] = 1;
    e = document.getElementById(objid + "_output"); 
    e.innerHTML = '';   
    code = codebox.value;
    h = get_http();
    h.onreadystatechange = function()
        {
            if (h.readyState == 4) 
            {
                try
                {
                    var status = h.status;
                }
                catch(e)
                {
                    var status = "NO HTTP RESPONSE";
                }
                switch (status)
                {
                case 200:
                    //set_element_text(outputspan, h.responseText)
                    setTimeout("sendNotification('" + objid +"')", 500);
                    break;
                case 12029:
                    //IE could not connect to server
                    status = "NO HTTP RESPONSE";
                default:
                    alert(status + ": " + h.responseText);
                }
            }
        };
    h.open("POST", "/doctest"+session_id+"?"+objid, true);
    h.send(code);
}


function sendNotification(term_id)
//used to update the output
{

    var h = get_http();
    var e = document.getElementById(term_id + "_output");
    
    //alert(data);
    h.onreadystatechange=function()
    {
        if (h.readyState == 4)
        {
            try
            {
                var status = h.status;
            }
            catch(e)
            {
                var status = "NO HTTP RESPONSE";
            }
            switch(status)
            {
                case 200:
                    //alert(status)
                    e.innerHTML = e.innerHTML + h.responseText;
                   setTimeout("sendNotification('" + term_id +"')", 500);
                    break;
                case 403:
                default:
                    //e.innerHTML = status + h.responseText;
                    interpreters[term_id] = 0;
            };
        };
    };
    h.open("POST", "/rawio"+session_id+"?"+term_id, true);
    h.send('');
};

/*--------------------------------------------------------------------------------*/

function exec_canvas(canvas_id)
{
    var h = get_http();
    var e = document.getElementById(canvas_id + "_input");
    h.onreadystatechange=function()
    {
        if (h.readyState == 4)
        {
            try
            {
                var status = h.status;
            }
            catch(e)
            {
                var status = "NO HTTP RESPONSE";
            }
            switch(status)
            {
                case 200:
                    eval(h.responseText)
                    break;
                case 400:
                  alert(h.statusText)
                    break;
                default:
                    //e.innerHTML = status + h.responseText;
                    alert("Error of unknown origin in code_exec.js, exec_canvas()");
            };
        };
    };
    h.open("POST", "/canvas_exec"+session_id+"?"+canvas_id, true);
    h.send(e.value);
};

"""
common = __common

def set_sessionid(ses_id):
    """set the session ID so that the javacscript can be used"""
    global common, __common
    common = ("session_id=%s"%ses_id) + __common