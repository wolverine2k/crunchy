"""  Crunchy doctest plugin.

From a sample interpreter session contained inside a <pre> element,
meant to be used as a doctest input, it creates an editor for a user to
enter some code which should satisfy the doctest.

This module is meant to be used as an example of how to create a custom
Crunchy plugin; it probably contains more comments than necessary
for people familiar with the Crunchy plugin architecture.
"""

# All plugins should import the crunchy plugin API

# All plugins should import the crunchy plugin API via interface.py
from src.interface import config, plugin, Element, SubElement, tostring
from src.utilities import extract_log_id, wrap_in_div

# The set of other "widgets/services" required from other plugins
requires =  set(["editor_widget", "io_widget"])

# each doctest code sample will be kept track via a uid used as a key.
doctests = {}

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
    plugin['register_tag_handler']("pre", "title", "doctest",
                                          doctest_widget_callback)
    # By convention, the custom handler for "name" will be called
    # via "/name"; for security, we add a random session id
    # to the custom handler's name to be executed.
    plugin['register_http_handler'](
                         "/doctest%s"%plugin['session_random_id'],
                                       doctest_runner_callback)
    plugin['add_vlam_option']('no_markup', 'doctest')

def doctest_runner_callback(request):
    """Handles all execution of doctests. The request object will contain
    all the data in the AJAX message sent from the browser."""
    # note how the code to be executed is not simply the code entered by
    # the user, and obtained as "request.data", but also includes a part
    # (doctest_pycode) defined below used to automatically call the
    # correct method in the doctest module.
    code = request.data + (doctest_pycode % doctests[request.args["uid"]])
    plugin['exec_code'](code, request.args["uid"], doctest=True)
    request.send_response(200)
    request.end_headers()

def doctest_widget_callback(page, elem, uid):
    """Handles embedding suitable code into the page in order to display and
    run doctests"""
    vlam = elem.attrib["title"]
    log_id = extract_log_id(vlam)
    if log_id:
        t = 'doctest'
        config[page.username]['logging_uids'][uid] = (log_id, t)

    # When a security mode is set to "display ...", we only parse the
    # page, but no Python execution from is allowed from that page.
    # If that is the case, we won't include javascript either, to make
    # thus making the source easier to read.
    if 'display' not in config[page.username]['page_security_level'](page.url):
        if not page.includes("doctest_included") :
            page.add_include("doctest_included")
            page.add_js_code(doctest_jscode)

    # next, we style the code, also extracting it in a useful form ...
    elem.attrib['title'] = "pycon"
    doctestcode = plugin['services'].style(page, elem)
    elem.attrib['title'] = "vlam"

    if log_id:
        config[page.username]['log'][log_id] = [tostring(markup)]
    # which we store
    doctests[uid] = doctestcode

    wrap_in_div(elem, uid, vlam, "doctest")
    if config[page.username]['popups']:
        # insert popup helper
        img = Element("img", src="/images/help.png",
                title = "cluetip Hello %s! "%page.username + "This is a doctest.",
                rel = "/docs/popups/doctest.html")
        elem.append(img)
        plugin['services'].insert_cluetip(page, img, uid)

    # call the insert_editor_subwidget service to insert an editor:
    plugin['services'].insert_editor_subwidget(page, elem, uid)
    #some spacing:
    SubElement(elem, "br")
    # the actual button used for code execution:
    btn = SubElement(elem, "button")
    btn.text = "Run Doctest"
    btn.attrib["onclick"] = "exec_doctest('%s')" % uid
    if "analyzer_score" in vlam:
        plugin['services'].add_scoring(page, btn, uid)
    if "analyzer_report" in vlam:
        plugin['services'].insert_analyzer_button(page, elem, uid)
    SubElement(elem, "br")
    # finally, an output subwidget:
    plugin['services'].insert_io_subwidget(page, elem, uid)

# we need some unique javascript in the page; note how the
# "/doctest" handler mentioned above appears here, together with the
# random session id.
doctest_jscode = """
function exec_doctest(uid){
    try{
    document.getElementById("kill_image_"+uid).style.display = "block";
    }
    catch(err){;}
    code=editAreaLoader.getValue("code_"+uid);
    var j = new XMLHttpRequest();
    j.open("POST", "/doctest%s?uid="+uid, false);
    j.send(code);
};
""" % plugin['session_random_id']
# Finally, the special Python code used to call the doctest module,
# mentioned previously
doctest_pycode = """
__teststring = \"\"\"%s\"\"\"
from doctest import DocTestParser as __DocTestParser, DocTestRunner as __DocTestRunner
__test = __DocTestParser().get_doctest(__teststring, locals(), "Crunchy Doctest", "<crunchy>", 0)
__x = __DocTestRunner().run(__test, out=doctest_out.write)
doctest_out.write(__x)
"""

#Note: information about doctest_out is found in interpreter.py
