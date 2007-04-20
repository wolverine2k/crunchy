"""  Crunchy doctest plugin.

From a sample interpreter session contained inside a <pre> element,
meant to be used as a doctest input, it creates an editor for a user to
enter some code which should satisfy the doctest.

This module is meant to be used as an example of how to create a custom
Crunchy plugin; it probably contains more comments than necessary
for people familiar with the Crunchy plugin architecture.
"""

# All plugins should import the crunchy plugin API

import CrunchyPlugin

# Third party modules - included in crunchy distribution
from element_tree import ElementTree
et = ElementTree

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
    CrunchyPlugin.register_vlam_handler("pre", "doctest", doctest_widget_callback)
    # By convention, the custom handler for "name" will be called via "/name"
    CrunchyPlugin.register_http_handler("/doctest", doctest_runner_callback)


def doctest_runner_callback(request):
    """Handles all execution of doctests. The request object will contain
    all the data in the AJAX message sent from the browser."""
    # note how the code to be executed is not simply the code entered by
    # the user, and obtained as "request.data", but also includes a part
    # (doctest_pycode) defined below used to automatically call the
    # correct method in the doctest module.
    code = request.data + (doctest_pycode % doctests[request.args["uid"]])
    CrunchyPlugin.exec_code(code, request.args["uid"])
    request.send_response(200)
    request.end_headers()

def doctest_widget_callback(page, elem, uid, vlam):
    """Handles embedding suitable code into the page in order to display and
    run doctests"""
    # first we need to make sure that the required javacript code is in the page:
    if not page.includes("doctest_included"):
        page.add_include("doctest_included")
        page.add_js_code(doctest_jscode)
    # next, we style the code, also extracting it in a useful form ...
    doctestcode, markup = CrunchyPlugin.services.style_pycode_nostrip(page, elem)
    # which we store
    doctests[uid] = doctestcode
    # reset the original element to use it as a container.  For those
    # familiar with dealing with ElementTree Elements, in other context,
    # note that the style_doctest() method extracted all of the existing
    # text, removing any original markup (and other elements), so that we
    # do not need to save either the "text" attribute or the "tail" one
    # before resetting the element.
    elem.clear()
    elem.tag = "div"
    # We insert the styled doctest code inside this container element:
    elem.insert(0, markup)
    # call the insert_editor_subwidget service to insert an editor:
    CrunchyPlugin.services.insert_editor_subwidget(elem, uid)
    #some spacing:
    et.SubElement(elem, "br")
    # the actual button used for code execution:
    btn = et.SubElement(elem, "button")
    btn.text = "Run Doctest"
    btn.attrib["onclick"] = "exec_doctest('%s')" % uid
    et.SubElement(elem, "br")
    # finally, an output subwidget:
    CrunchyPlugin.services.insert_io_subwidget(page, elem, uid)

# we need some unique javascript in the page; note how the
# "/doctest" handler mentioned above appears here.
doctest_jscode= """
function exec_doctest(uid){
    code = document.getElementById("code_"+uid).value;
    var j = new XMLHttpRequest();
    j.open("POST", "/doctest?uid="+uid, false);
    j.send(code);
};
"""
# Finally, the special Python code used to call the doctest module,
# mentioned previously
doctest_pycode = """
__teststring = \"\"\"%s\"\"\"
from doctest import DocTestParser as __DocTestParser, DocTestRunner as __DocTestRunner
__test = __DocTestParser().get_doctest(__teststring, globals(), "Crunchy Doctest", "<crunchy>", 0)
__x = __DocTestRunner().run(__test)
print "Your code failed %%s out of %%s tests." %%(__x)
"""
