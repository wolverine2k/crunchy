/* comet.js
   basic functionality to be improved upon.
*/
uid_regexp = /^(.*?)\n/;

function runOutput(channel)
{
    var h = new XMLHttpRequest();
    h.onreadystatechange = function(){
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
                //alert(this);
                try{
                    var rheader = h.responseText.match(uid_regexp)[1];
                    var header = rheader.split(" ");
                    var rdata = h.responseText.substr(rheader.length +1);
                    if(header[0] == "STDIN"){
                            document.getElementById("out_"+header[1]).innerHTML += ('<span class="stdin">'+rdata+'</span>');
                    };
                    
                    if(header[0] == "STDOUT"){
                            document.getElementById("out_"+header[1]).innerHTML += ('<span class="stdout">'+rdata+'</span>');
                    };
                    if(header[0] == "STDERR"){
                            document.getElementById("out_"+header[1]).innerHTML += ('<span class="stderr">'+rdata+'</span>');
                    };
                    if(header[0] == "STOP"){
                            document.getElementById("in_"+header[1]).style.display="none";
                            
                    };
                    if(header[0] == "RESET"){
                            document.getElementById("in_"+header[1]).style.display="inline";
                            document.getElementById("out_"+header[1]).innerHTML="";
                            document.getElementById("canvas_"+header[1]).style.display="none";
                    };
                    if(header[0] == "JSCRIPT"){
                        eval(rdata);
                    };
                } catch(e) {
                    //alert("Invalid response from server on /comet, response follows:\\n\\n" + h.responseText);
                    throw e;
                };
                runOutput(channel);
                break;
            default:
                //alert("Output seems to have finished");
            }
        }
    };
    h.open("GET", "/comet?channel="+channel, true);
    h.send("");
};

function push_keys(event, uid){
    if(event.keyCode != 13) return;
    data = document.getElementById("in_"+uid).value;
    document.getElementById("in_"+uid).value = "";
    var i = new XMLHttpRequest()
    i.open("POST", "/input?uid="+uid, true);
    i.send(data + "\n");
};

function exec_code(uid){
    code = document.getElementById("code_"+uid).value;
    var j = new XMLHttpRequest();
    j.open("POST", "/exec?uid="+uid, false);
    j.send(code);
};

function init_interp(uid){
    code = "import interpreter\ninterpreter.BorgConsole().interact()";
    var j = new XMLHttpRequest();
    j.open("POST", "/exec?uid="+uid, false);
    j.send(code);
};
