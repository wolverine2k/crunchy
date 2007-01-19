"""demo the new server"""

from http_serve import *
import cometIO



code = """
import code
t = code.InteractiveConsole()
t.interact()
print "Interpreter finished"
"""


def handle_default(request):
    request.send_response(200)
    request.end_headers()
    request.wfile.write(def_data)
    
uid = cometIO.do_exec(code)
def_data = """
<html>
<head>
<title>
Crunchy COMET IO demo
</title>
<script type="text/javascript">
var h = new XMLHttpRequest();


function f(){
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
                //alert(h.responseText);
                document.getElementById("out").innerHTML += h.responseText;
                h = new XMLHttpRequest();
                h.onreadystatechange=f;
                h.open("GET", "/comet?uid=%s", true);
                h.send("");
                break;
            case 12029:
                //IE could not connect to server
                status = "NO HTTP RESPONSE";
            default:
                alert(status + ": " + h.responseText);
            }
        }
    };
h.onreadystatechange= f;
h.open("GET", "/comet?uid=%s", true);
h.send("");

function push_keys(event){
    if(event.keyCode != 13) return;
    data = document.getElementById("in").value;
    document.getElementById("in").value = "";
    i = new XMLHttpRequest()
    i.open("POST", "/input?uid=%s", true);
    i.send(data + "\\n");
};
</script>
<style>
.stdout {
    color: blue;
}

.stderr {
    color: red;
}

</style>
</head>
<body>
<pre id="out" style="display:inline;">
</pre><input id="in" type="text" onkeydown="push_keys(event)" style="width:90%%;"></input>
</body>
</html>
""" % (uid,uid,uid)


s = MyHTTPServer(('127.0.0.1', 8002), HTTPRequestHandler)

s.register_default_handler(handle_default)
s.register_handler(cometIO.push_input, "/input")
s.register_handler(cometIO.comet, "/comet")

s.serve_forever()
