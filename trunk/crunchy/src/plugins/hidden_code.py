"""  Crunchy hidden_code plugin.

From a sample interpreter session contained inside a <pre> element,
containing some code to be hidden, it extracts (and save) those hidden
code samples, replacing them by comment.  Prior to execution, it reintroduces
those code samples at the appropriate place.

"""

# All plugins should import the crunchy plugin API

# All plugins should import the crunchy plugin API via interface.py
from src.interface import config, plugin, SubElement, python_version, translate
from src.utilities import wrap_in_div

# The set of other "widgets/services" required from other plugins
requires = set(["editor_widget", "io_widget"])

# each doctest code sample will be kept track via a uid used as a key.
extracted_lines = {}
_ = translate['_']

HIDDEN_CODE_MARKER = "# hidden code"
HIDDEN_CODE_BEGIN = "!hidden_code_begin"
HIDDEN_CODE_END = "hidden_code_end!"


def register():
    """The register() function is required for all plugins.
       In this case, we need to register two types of 'actions':
       1. a custom 'vlam handler' designed to tell Crunchy how to
          interpret the special Crunchy markup.
       2. a custom http handler to deal with "run doctest" commands,
          issued by clicking on a button incorporated in the
          'doctest widget';
       """
    # 'doctest' only appears inside <pre> elements, using the notation
    # <pre title='doctest ...'>
    plugin['register_tag_handler']("pre", "title", "hidden_code",
                                          hidden_code_widget_callback)
    # By convention, the custom handler for "name" will be called
    # via "/name"; for security, we add a random session id
    # to the custom handler's name to be executed.
    plugin['register_http_handler'](
                         "/hidden_code%s" % plugin['session_random_id'],
                                       hidden_code_runner_callback)


def hidden_code_runner_callback(request):
    """Handles all execution of hidden_code samples. The request object will contain
    all the data in the AJAX message sent from the browser."""
    # note how the code to be executed is not simply the code entered by
    # the user, and obtained as "request.data", but also includes a part
    #
#
    # (doctest_pycode) defined below used to automatically call the
 #
    # correct method in the doctest module.
    if python_version >= 3:
        request.data = request.data.decode('utf-8')
    # add back code here
    code = request.data
    _lines = code.split("\n")
    i = 0
    for j, _line in enumerate(_lines):
        if _line == HIDDEN_CODE_MARKER:
            _lines[j] = extracted_lines[request.args["uid"]][i]
            i += 1
    code = "\n".join(_lines)

    plugin['exec_code'](code, request.args["uid"])
    request.send_response(200)
    request.end_headers()


def hidden_code_widget_callback(page, elem, uid):
    """Handles embedding suitable code into the page in order to display and
    run code samples"""
    vlam = elem.attrib["title"]
    extracted_lines[uid] = []
    # When a security mode is set to "display ...", we only parse the
    # page, but no Python execution from is allowed from that page.
    # If that is the case, we won't include javascript either, to make
    # thus making the source easier to read.
    if 'display' not in config[page.username]['page_security_level'](page.url):
        if not page.includes("hidden_code_included"):
            page.add_include("hidden_code_included")
            page.add_js_code(hidden_code_jscode)

    # next, we style the code, also extracting it in a useful form ...
    elem.attrib['title'] = "py"
    complete_code, show_vlam = plugin['services'].style(page, elem, None, vlam)
    #
    _lines = complete_code.split('\n')
    displayed_lines = []
    hidden_lines = []

    hide = False
    for _line in _lines:
        if hide:
            if _line.strip() == HIDDEN_CODE_END:
                hide = False
                extracted_lines[uid].append('\n'.join(hidden_lines))
            else:
                hidden_lines.append(_line)
        else:
            if _line.strip() == HIDDEN_CODE_BEGIN:
                hide = True
                hidden_lines = []
                displayed_lines.append(HIDDEN_CODE_MARKER)
            else:
                displayed_lines.append(_line)

    complete_code = '\n'.join(displayed_lines)

    elem.attrib['title'] = vlam

    wrap_in_div(elem, uid, vlam, "hidden_code", show_vlam)

    # call the insert_editor_subwidget service to insert an editor:
    plugin['services'].insert_editor_subwidget(page, elem, uid, complete_code)
    #some spacing:
    SubElement(elem, "br")
    # the actual button used for code execution:
    btn = SubElement(elem, "button")
    btn.attrib["id"] = "run_code_btn_" + uid
    btn.text = _("Run Code")
    btn.attrib["onclick"] = "exec_hidden_code('%s')" % uid
    SubElement(elem, "br")
    # finally, an output subwidget:
    plugin['services'].insert_io_subwidget(page, elem, uid)

# we need some unique javascript in the page; note how the
# "/hidden_code" handler mentioned above appears here, together with the
# random session id.
hidden_code_jscode = """
function exec_hidden_code(uid){
    try{
    document.getElementById("kill_image_"+uid).style.display = "block";
    }
    catch(err){;}
    code=editAreaLoader.getValue("code_"+uid);
    var j = new XMLHttpRequest();
    j.open("POST", "/hidden_code%s?uid="+uid, false);
    j.send(code);
};

""" % plugin['session_random_id']
