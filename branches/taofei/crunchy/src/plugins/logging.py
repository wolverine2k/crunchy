'''
logging.py

deal with logging relate action 
1. enable logging
2. disable logging
3. view log_file
'''
import urllib
import os

# All plugins should import the crunchy plugin API via interface.py
from src.interface import config, translate, plugin, Element, SubElement, fromstring
import src.session as session

requires = set(['add_menu_item'])
provides = set([])

def register():
    '''
    register 5 http handlers for log related work
    '''

    plugin['register_http_handler'](
                         "/get_log_flag", get_log_flag_cb) 
    plugin['register_http_handler'](
                         "/enable_log", enable_log_cb) 
    plugin['register_http_handler'](
                         "/disable_log", disable_log_cb) 
    plugin['register_http_handler'](
                         "/view_log_file", view_log_file_cb) 

    plugin['register_http_handler'](
                         "/replay_log", replay_log_cb) 

    plugin['services'].add_menu_item(logging_menu_items)

def get_logging_menu(page, ele, *dummy):
    ele.insert(-1, menu_html)

def get_log_flag_cb(request):
    request.send_response(200)
    request.end_headers()
    request.wfile.write(str(session.get_log_flag()))

def enable_log_cb(request):
    session.enable_log()
    get_log_flag_cb(request)

def disable_log_cb(request):
    session.disable_log()
    get_log_flag_cb(request)

def view_log_file_cb(request):
    s = session.get_session()
    if not s['log_flag']:
        return #report error
    log_file = s['log_filename']
    #always save log before view 
    session.save_log()
        
    request.send_response(302)
    request.send_header("Location", "/local?url=%s" %(urllib.quote_plus(log_file)))
    request.end_headers()

def replay_log_cb(request):
    '''replay user actions according to the log
    '''
    pass


#how to use & in code ? 
#it report error , even put it in <![CDATA[ , it is parsed ...
js = '''
<script type="text/javascript">
//<![CDATA[ 
function on_get_log_flag_response()
{
    if(this.readyState != 4 || this.status != 200)
    {
        return ;
    }
    else
    {
        var ele = document.getElementById('log_status');
        if (this.responseText == "True")
        {
            ele.innerHTML = "Disable Log";
            document.getElementById('view_log_file').style.display = "";
        }
        else
        {
            ele.innerHTML = "Enable Log";
            document.getElementById('view_log_file').style.display = "none";
        }
    }
}

function toggle_log_flag()
{
    var ele = document.getElementById('log_status');
    var j = new XMLHttpRequest();
    j.onreadystatechange = on_get_log_flag_response;
    if(ele.innerHTML == "Disable Log")
    {
        //ele.innerHTML = "Enable Log";
        //document.getElementById('view_log_file').style.display = "none";
        j.open("POST", "/disable_log", true);
        j.send("");
    }
    else
    {
        //ele.innerHTML = "Disable Log";
        //document.getElementById('view_log_file').style.display = "";
        j.open("POST", "/enable_log", true);
        j.send("");
    }
}
//]]>
</script>
'''

js2 = '''
<script type="text/javascript">
//<![CDATA[ 
(function(){
    var j = new XMLHttpRequest();
    j.onreadystatechange = on_get_log_flag_response;
    j.open("GET", "/get_log_flag", true);
    j.send("");
})();
//]]>
</script>
'''
logging_menu_items = [fromstring(x) for x in [
    js,
    '<span class="menu_separator" > </span>',
    '<a id="log_status" href="javascript:toggle_log_flag();void(0);">Disable Log</a>',
    '<a id="view_log_file" href="/view_log_file" >View Log File</a>',
    js2,
]]


