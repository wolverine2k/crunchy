"""  Crunchy editor plugin.

From some Python code (possibly including a simulated interpreter session)
contained inside a <pre> element, it creates an editor for a user to
enter or modify some code.

This module is meant to be used as an example of how to create a custom
Crunchy plugin; it probably contains more comments than necessary
for people familiar with the Crunchy plugin architecture.
"""

# All plugins should import the crunchy plugin API
import CrunchyPlugin

# Third party modules - included in crunchy distribution
from element_tree import ElementTree, HTMLTreeBuilder
et = ElementTree

# The set of other "widgets/services" provided by this plugin
provides = set(["editor_widget"])
# The set of other "widgets/services" required from other plugins
requires = set(["io_widget", "/exec", "style_pycode"])

def register():
    """The register() function is required for all plugins.
       In this case, we need to register two types of 'actions':
       1. a custom 'vlam handler' designed to tell Crunchy how to
          interpret the special Crunchy markup.
       2. a custom service to insert an editor when requested by this or
          another plugin.
       """
    # 'editor' only appears inside <pre> elements, using the notation
    # <pre title='editor ...'>
    CrunchyPlugin.register_vlam_handler("pre", "editor", insert_editor)
    CrunchyPlugin.register_service(insert_editor_subwidget, "insert_editor_subwidget")

def insert_editor_subwidget(elem, uid, code="\n"):
    """inserts an Elementtree that is an editor,
    used to provide a basic insert_editor_subwidget service
    """
    #### Note: this will need to be updated to include EditArea
    inp = et.SubElement(elem, "textarea")
    inp.attrib["rows"] = "10"
    inp.attrib["cols"] = "80"
    inp.attrib["id"] = "code_" + uid
    inp.text = code

def insert_editor(page, elem, uid, vlam):
    """handles the editor widget"""
    # first we need to make sure that the required javacript code is in the page:
    if not page.includes("exec_included"):
        page.add_include("exec_included")
        page.add_js_code(exec_jscode)
    # then we can go ahead and add html markup, extracting the Python
    # code to be executed in the process
    code, markup = CrunchyPlugin.services.style_pycode(page, elem)
    # reset the original element to use it as a container.  For those
    # familiar with dealing with ElementTree Elements, in other context,
    # note that the style_doctest() method extracted all of the existing
    # text, removing any original markup (and other elements), so that we
    # do not need to save either the "text" attribute or the "tail" one
    # before resetting the element.
    elem.clear()
    elem.tag = "div"
    # determine where the code should appear; we can't have both
    # no-pre and no-copy at the same time
    if not "no-pre" in vlam:
        elem.insert(0, markup)
    elif "no-copy" in vlam:
        code = "\n"
    CrunchyPlugin.services.insert_editor_subwidget(elem, uid, code)
    #some spacing:
    et.SubElement(elem, "br")
    # the actual button used for code execution:
    btn = et.SubElement(elem, "button")
    btn.attrib["onclick"] = "exec_code('%s')" % uid
    btn.text = "Execute"
    et.SubElement(elem, "br")
    # finally, an output subwidget:
    CrunchyPlugin.services.insert_io_subwidget(page, elem, uid)

# we need some unique javascript in the page; note how the
# "/exec" handler referred to above as a required service appears here.
exec_jscode= """
function exec_code(uid){
    code = document.getElementById("code_"+uid).value;
    var j = new XMLHttpRequest();
    j.open("POST", "/exec%s?uid="+uid, false);
    j.send(code);
};
"""%CrunchyPlugin.session_random_id
