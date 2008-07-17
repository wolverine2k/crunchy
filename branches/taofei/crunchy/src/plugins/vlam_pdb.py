"""  Crunchy pdb plugin.

Pdb the code in the pre area

"""

# All plugins should import the crunchy plugin API

# All plugins should import the crunchy plugin API via interface.py
from src.interface import config, plugin, SubElement, tostring
from src.utilities import extract_log_id
import src.session as session
from src.cometIO import raw_push_input

# The set of other "widgets/services" required from other plugins
requires =  set(["editor_widget", "io_widget"])

# each doctest code sample will be kept track via a uid used as a key.
pdb_codes = {}

def register():
    """The register() function is required for all plugins.
       In this case, we need to register two types of 'actions':
       1. a custom 'vlam handler' designed to tell Crunchy how to
          interpret the special Crunchy markup.
       2. a custom http handler to deal with "exec pdb command" commands,
       """
    # 'doctest' only appears inside <pre> elements, using the notation
    # <pre title='doctest ...'>
    plugin['register_tag_handler']("pre", "title", "pdb",
                                          pdb_widget_callback)
    # By convention, the custom handler for "name" will be called
    # via "/name"; for security, we add a random session id
    # to the custom handler's name to be executed.
    plugin['register_http_handler'](
                         "/pdb_next%s"%plugin['session_random_id'],
                         lambda r :pdb_command_callback(r, "next"))
    plugin['register_http_handler'](
                         "/pdb_local_var%s"%plugin['session_random_id'],
                         lambda r :pdb_command_callback(r, "local_var"))
    plugin['register_http_handler'](
                         "/pdb_start%s"%plugin['session_random_id'],
                        pdb_start_callback)

def pdb_start_callback(request):
    code = pdb_pycode % (request.data)
    #(pdb_codes[request.args["uid"]])
    plugin['exec_code'](code, request.args["uid"])
    request.send_response(200)
    request.end_headers()

def pdb_command_callback(request, command = "next"):
    """Handles all pdb command. The request object will contain
    all the data in the AJAX message sent from the browser."""
    # note how the code to be executed is not simply the code entered by
    # the user, and obtained as "request.data", but also includes a part
    # (doctest_pycode) defined below used to automatically call the
    # correct method in the doctest module.
    uid = request.args["uid"]
    if command == "next":
        raw_push_input(uid, "next\n")
    elif command == "local_var":
        raw_push_input(uid, "print(__dict2table(locals()))\n")
    request.send_response(200)
    request.end_headers()

def pdb_widget_callback(page, elem, uid):
    """Handles embedding suitable code into the page in order to display and
    run pdb"""
    vlam = elem.attrib["title"]
    #logging this is meanless
    #log_id = extract_log_id(vlam)
    #if log_id:
    #    t = 'doctest'
    #    session.add_log_id(uid, log_id, t)
        #config['logging_uids'][uid] = (log_id, t)

    # When a security mode is set to "display ...", we only parse the
    # page, but no Python execution from is allowed from that page.
    # If that is the case, we won't include javascript either, to make
    # thus making the source easier to read.
    if 'display' not in config['page_security_level'](page.url):
        if not page.includes("pdb_included") :
            page.add_include("pdb_included")
            page.add_js_code(pdb_jscode)
        #page.add_js_code('init_pdb_interpreter("%s");' % uid)

    # next, we style the code, also extracting it in a useful form ...
    code, markup, dummy = plugin['services'].style_pycode_nostrip(page, elem)
    #if log_id:
    #    session.log(uid, tostring(markup), "crunchy")
        #config['log'][log_id] = [tostring(markup)]
    # which we store
    pdb_codes[uid] = code
    # reset the original element to use it as a container.  For those # familiar with dealing with ElementTree Elements, in other context, # note that the style_pycode_nostrip() method extracted all of the existing
    # text, removing any original markup (and other elements), so that we
    # do not need to save either the "text" attribute or the "tail" one
    # before resetting the element.
    elem.clear()
    elem.tag = "div"
    elem.attrib["id"] = "div_"+uid
    # We insert the styled doctest code inside this container element:
    #elem.insert(0, markup)
    # call the insert_editor_subwidget service to insert an editor:
    plugin['services'].insert_editor_subwidget(page, elem, uid, code)
    #some spacing:
    SubElement(elem, "br")

    btn = SubElement(elem, "button")
    btn.text = "Start PDB"
    btn.attrib["onclick"] = "init_pdb_interpreter('%s')" % uid
    btn.attrib["id"] = "btn_start_pdb_%s" % uid

    btn = SubElement(elem, "button")
    btn.text = "Next Step"
    btn.attrib["onclick"] = "pdb_next_step('%s')" % uid
    btn.attrib["id"] = "btn_next_step_%s" % uid
    btn.attrib["disabled"] = "disabled"

    btn = SubElement(elem, "button")
    btn.text = "Show Local Var"
    btn.attrib["onclick"] = "pdb_command('local_var', '%s')" % uid
    btn.attrib["id"] = "btn_show_local_var_%s" % uid
    btn.attrib["disabled"] = "disabled"

    SubElement(elem, "br")

    # finally, an output subwidget:
    plugin['services'].insert_io_subwidget(page, elem, uid)


class PdbConsole(object):
    '''A pdb console
    a bridge between pdb and crunchy
    '''
    def __init__(self):
        pass

    def start(self, code):
        __debug_string = '''%s'''
        pdb.run(__debug_string %(code))

pdb_jscode = r"""
var random_session_id = '%s';
function pdb_next_step(uid){
    var j = new XMLHttpRequest();
    j.open("POST", "/pdb_next" + random_session_id +"?uid="+uid, false);
    j.send("next\n");
}
function pdb_command(command, uid){
    var j = new XMLHttpRequest();
    j.open("POST", "/pdb_" + command + random_session_id  + "?uid="+uid, false);
    j.send(command + "\n");
}

function init_pdb_interpreter(uid){
        var j = new XMLHttpRequest();
        code = document.getElementById('code_' + uid).value;
        j.open("POST", "/pdb_start" + random_session_id + "?uid="+uid, false);
        j.send(code);
        //document.getElementById('btn_start_pdb_' + uid).disabled= true;
        document.getElementById('btn_next_step_' + uid).disabled= false;
        document.getElementById('btn_show_local_var_' + uid).disabled= false;
};
""" % (plugin['session_random_id'])

pdb_pycode = """
import pdb
def __dict2table(d):
    s = "<table>"
    s += "<thead><tr><th>name</th><th>value</th></tr>"
    for key,item in d.items():
        if key == "__dict2table":
            continue
        s += "<tr><td>" + str(key)  + "</td><td>" + str(item) + "</td></tr>"
    s += "</tbody>"
    s += "</table>"
    return s
def __dict2table(d):
    s = ""
    for key,item in d.items():
        if key == "__dict2table":
            continue
        s += "" + str(key)  + "\\t" + str(item) + "\\n"
    return s

_debug_string = \"\"\"
%s
\"\"\"
pdb.run(_debug_string, locals={'__dict2table': __dict2table})
"""
_pdb_pycode = """
import pdb
import sys
from StringIO import StringIO
old_output = sys.stdout
__debug_string = \"\"\"
%s
\"\"\"
pdb.run(__debug_string)
"""


