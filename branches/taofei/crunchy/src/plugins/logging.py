'''
logging.py

deal with logging relate action 
1. enable logging
2. disable logging
3. view log_file
'''
import urllib

# All plugins should import the crunchy plugin API via interface.py
from src.interface import config, translate, plugin, Element, SubElement, fromstring
import src.session as session

requires = set(['add_menu_item'])
provides = set([])

def register():
    '''
    register a tag handler and three http handlers: /set_trusted and /remove_all
    '''

    plugin['register_http_handler'](
                         "/enable_log", enable_log_cb) 
    plugin['register_http_handler'](
                         "/disable_log", disable_log_cb) 
    plugin['register_http_handler'](
                         "/view_log_file", view_log_file_cb) 

    plugin['services'].add_menu_item(logging_menu_items)

def get_logging_menu(page, ele, *dummy):
    ele.insert(-1, menu_html)

def enable_log_cb(request):
    session.enable_log()

def disable_log_cb(request):
    session.disable_log()

def view_log_file_cb(request):
    s = session.get_session()
    if not s['log_flag']:
        return #report error
    log_file = s['log_filename']
    request.send_response(302)
    request.send_header("Location", "/local?url=%s" %(urllib.quote_plus(log_file)))
    request.end_headers()


js = '''
<script type="text/javascript">
function toggle_log_flag(ele)
{
    ele = document.getElementById('log_status');
    if(ele.innerHTML == "Disable Log")
    {
        ele.innerHTML = "Enable Log";
    }
    else
    {
        ele.innerHTML = "Disable Log";
    }
}
</script>
'''

logging_menu_items = [fromstring(x) for x in [
    js,
    '<span class="menu_separator" > </span>',
    '<a id="log_status" href="javascript:toggle_log_flag(this);void(0);">Disable Log</a>',
    '<a href="/view_log_file" >View Log File</a>',
]]


