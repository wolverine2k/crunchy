var interpreters = {}

function get_http()
// get an xmlhttprequest (or equivalent) object
{
    var h;
    if (typeof(XMLHttpRequest) != "undefined") 
    {
        h = new XMLHttpRequest();
    } 
    else 
    {
        try 
        { 
            h = new ActiveXObject("Msxml2.XMLHTTP"); 
        }
        catch (e) 
        {
            try 
            { 
                h = new ActiveXObject("Microsoft.XMLHTTP"); 
            }
            catch (E) 
            { 
                alert("Your browser is not supported, you need an AJAX capable browser."); 
            }
        }
    }
    return h;
};

function load_python_file(obj_id)
{
    e = document.getElementById(obj_id); 
    e.innerHTML = '';   
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
										editAreaLoader.setValue(obj_id, h.responseText);
										var obj = document.getElementById('hidden_load'+obj_id);
										obj.style.visibility = "hidden";
                    break;
                case 12029:
                    //IE could not connect to server
                    status = "NO HTTP RESPONSE";
                default:
                    alert(status + ": " + h.responseText);
                }
            }
        };
    h.open("GET", "/load_python"+session_id+"?"+"path="+path, true);
		h.send('');
}
function save_python_file(path, id)
{
	data = document.getElementById(id).value;
	h = get_http();
	h.open("POST", "/save_python"+session_id, true);
	// Use an unlikely part of a filename (path) as a separator between file
	// path and file content.
	h.send(path+"_::EOF::_"+editAreaLoader.getValue(id));
  var obj = document.getElementById('hidden_save'+id);
	obj.style.visibility = "hidden";
};

function save_and_run(path, id)
{
	data = document.getElementById(id).value;
	h = get_http();
	h.open("POST", "/save_and_run"+session_id, true);
	// Use an unlikely part of a filename (path) as a separator between file
	// path and file content.
	h.send(path+"_::EOF::_"+editAreaLoader.getValue(id));
  var obj = document.getElementById('hidden_save'+id);
	obj.style.visibility = "hidden";
};
// send code to be executed and display the result
//

function exec_by_id(objid)
{
    interpreters[objid] = 1;
    e = document.getElementById(objid + "_output"); 
    e.innerHTML = '';   
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
    h.open("POST", "/execute"+session_id+"?"+objid, true);
    h.send(editAreaLoader.getValue(objid + "_code"));
}

function doctest_by_id(objid)
{
    interpreters[objid] = 1;
    e = document.getElementById(objid + "_output"); 
    e.innerHTML = '';   
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
    h.send(editAreaLoader.getValue(objid + "_code"));
}


function sendNotification(term_id)
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
					alert("Error of unknown origin in code_exec.js, exec_canvas()");
			};
		};
	};
	h.open("POST", "/canvas_exec"+session_id+"?"+canvas_id, true);
	h.send(editAreaLoader.getValue(canvas_id + "_input"));
};

/*------------------------------- interpreter-------------------------------- */
// "waiting" is a translatable string passed as a variable.
function interp_trapkeys(event, interp_id, waiting){
	switch(event.keyCode){
		case 13:
			hide_tipbar(interp_id);
			interp_push(interp_id, waiting);
			break;
		case 48: 	//close )
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

function interp_push(interp_id, waiting){
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
	output.textContent = waiting;
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
    tipbar = document.getElementById(interp_id+"_tipbar");
    hide_tipbar(interp_id);
   
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
                    alert(status + "\n" + h.responseText, false);
            }
        }
    }
    h.open("GET", "/doc"+session_id+"?name="+interp_id+"&line=" + encodeURIComponent(data), true);
    h.send(null);
};

function interp_doc_mac(interp_id) {
    input = document.getElementById(interp_id+"_input");  
    data = input.value + "(";
    tipbar = document.getElementById(interp_id+"_tipbar");
    hide_tipbar(interp_id);
   
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
    tipbar = document.getElementById(interp_id+"_tipbar");
    hide_tipbar(interp_id);
   
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
                    alert(status + "\n" + h.responseText, false);
            }
        }
    }
    h.open("GET", "/dir"+session_id+"?name="+interp_id+"&line=" + encodeURIComponent(data), true);
    h.send(null);
};
function interp_dir_mac(interp_id) {
    input = document.getElementById(interp_id+"_input");    
    data = input.value + ".";
    tipbar = document.getElementById(interp_id+"_tipbar");
    hide_tipbar(interp_id);
   
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
                    alert(status + "\n" + h.responseText, false);
            }
        }
    }
    h.open("GET", "/dir"+session_id+"?name="+interp_id+"&line=" + encodeURIComponent(data), true);
    h.send(null);
};

//---------------------------------------------------------------------

function exec_external(id)
{
	data = document.getElementById(id + "_code").value;
	h = get_http();
	h.open("POST", "/spawn"+session_id, true);
	h.send(editAreaLoader.getValue(id + "_code"));
};
// with terminal/console window: this might make sense only for Windows.
function exec_external_console(id)
{
	h = get_http();
	h.open("POST", "/spawn_console"+session_id, true);
  h.send(editAreaLoader.getValue(id + "_code"));
};
// used with chewy: record changes for individual elements
var changes = '';
function record(id, new_vlam){
document.getElementById('myButton'+id).innerHTML +=' - ok';
changes += id + ';' + new_vlam + ';';
}
// used with chewy: record all the changes done on a given page
function update()
{
if (changes == ''){
alert("No changes have been recorded!");
}
else{
location.href="/update?changed="+changes;
}
}