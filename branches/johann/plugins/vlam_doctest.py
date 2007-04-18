"""Handles all aspects of the crunchy doctest widget.
I have written this code with a huge number of comments to try to explain my 
take on the Plugin API.
This is also the first proper plugin written from scratch using this API.

While this doesn't quite mirror the functionality in the classic version of 
Crunchy, it does provide us with a whole load of examples of the API in action.
"""

#import the crunchy plugin API
from CrunchyPlugin import *

# Third party modules - included in crunchy distribution
from element_tree import ElementTree
et = ElementTree

# we depend on the editor subwidget being provided by other plugins
requires =  set(["editor_widget","io_widget"])

#we need to index doctest code by element uid:
doctests = {}


def register():
    """All of the plugin initialisation code goes in here"""
    # first we register a custom http handler to deal with "Run Doctest" commands
    register_http_handler("/doctest", doctest_runner_callback)
    # and then we register a callback to process the doctest widgets
    register_vlam_handler("pre", "doctest", doctest_widget_callback)

        
def doctest_runner_callback(request):
    """Handles all execution of doctests. The request object will contain 
    all the data in the AJAX message sent from the browser."""
    code = request.data + (doctest_pycode % doctests[request.args["uid"]])
    exec_code(code, request.args["uid"])
    request.send_response(200)
    request.end_headers()
    
def doctest_widget_callback(page, elem, uid):
    """Handles embedding suitable code into the page in order to display and
    run doctests"""
    # first we need to make sure that the required javacript code is in the page:
    if not hasattr(page, "doctest_included"):
        page.doctest_included = True
        page.add_js_code(doctest_jscode)
    #extract the doctest code:
    doctestcode = elem.text
    #and store it:
    doctests[uid] = doctestcode
    #reset the element:
    tail = elem.tail
    elem.clear()
    elem.tail = tail
    elem.tag = "div"
    # and insert the doctest code:
    dtdisplay = et.SubElement(elem, "pre")
    dtdisplay.text = doctestcode
    # call the insert_editor_subwidget service:
    services.insert_editor_subwidget(elem, uid)
    #some spacing:
    et.SubElement(elem, "br")
    # and the actual button:
    btn = et.SubElement(elem, "button")
    btn.text = "Run Doctest"
    btn.attrib["onclick"] = "exec_doctest('%s')" % uid
    et.SubElement(elem, "br")
    # and an output subwidget:
    services.insert_io_subwidget(page, elem, uid)

# we need some javascript in the page:
doctest_jscode= """
function exec_doctest(uid){
    code = document.getElementById("code_"+uid).value;
    var j = new XMLHttpRequest();
    j.open("POST", "/doctest?uid="+uid, false);
    j.send(code);
};
"""

doctest_pycode = """
__teststring = \"\"\"%s\"\"\"
from doctest import DocTestParser as __DocTestParser, DocTestRunner as __DocTestRunner
__test = __DocTestParser().get_doctest(__teststring, globals(), "Crunchy Doctest", "<crunchy>", 0)
__x = __DocTestRunner().run(__test)
print "Your code failed %%s out of %%s tests." %%(__x)
"""
