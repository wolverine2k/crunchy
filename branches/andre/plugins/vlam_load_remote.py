"""  Crunchy load remote tutorial plugin.

Creates a form allowing to specify the URL of a tutorial to be loaded
by Crunchy.

This module is meant to be used as an example of how to create a custom
Crunchy plugin; it probably contains more comments than necessary
for people familiar with the Crunchy plugin architecture.
"""

# All plugins should import the crunchy plugin API
import CrunchyPlugin

# Third party modules - included in crunchy distribution
from element_tree import ElementTree, HTMLTreeBuilder
et = ElementTree

### The set of other "widgets/services" provided by this plugin
##provides = set(["editor_widget"])
# The set of other "widgets/services" required from other plugins
requires = set(["/remote"])

def register():
    """The register() function is required for all plugins.
       In this case, we need to register a single type of 'action':
          a custom 'vlam handler' designed to tell Crunchy how to
          interpret the special Crunchy markup.
       """
    # 'load_remote' only appears inside <span> elements, using the notation
    # <span title='load_remote'>
    CrunchyPlugin.register_vlam_handler("span", "load_remote", insert_load_remote)

def insert_load_remote(page, parent, uid, vlam):
    print "parent.text = ", parent.text
    form = et.SubElement(parent, 'form', name='url', size='80', method='get',
                       action='/remote')
    input1 = et.SubElement(form, 'input', name='url', size='80',
                           value=parent.text)
    input2 = et.SubElement(form, 'input', type='submit',
                           value='Load remote tutorial')
    input2.attrib['class'] = 'crunchy'
##    """handles the editor widget"""
##    # first we need to make sure that the required javacript code is in the page:
##    if not page.includes("exec_included"):
##        page.add_include("exec_included")
##        page.add_js_code(exec_jscode)
##    # then we can go ahead and add html markup, extracting the Python
##    # code to be executed in the process
##    code, markup = CrunchyPlugin.services.style_pycode(page, elem)
##
##    # reset the original element to use it as a container.  For those
##    # familiar with dealing with ElementTree Elements, in other context,
##    # note that the style_doctest() method extracted all of the existing
##    # text, removing any original markup (and other elements), so that we
##    # do not need to save either the "text" attribute or the "tail" one
##    # before resetting the element.
##    elem.clear()
##    elem.tag = "div"
##    # determine where the code should appear; we can't have both
##    # no-pre and no-copy at the same time
##    if not "no-pre" in vlam:
##        elem.insert(0, markup)
##    elif "no-copy" in vlam:
##        code = "\n"
##    CrunchyPlugin.services.insert_editor_subwidget(page, elem, uid, code)
##    #some spacing:
##    et.SubElement(elem, "br")
##    # the actual button used for code execution:
##    if not "no-internal" in vlam:
##        btn = et.SubElement(elem, "button")
##        btn.attrib["onclick"] = "exec_code('%s')" % uid
##        btn.text = "Execute"
##        et.SubElement(elem, "br")
##    if "external" in vlam:
##        btn = et.SubElement(elem, "button")
##        btn.attrib["onclick"] = "exec_code_externally('%s')" % uid
##        btn.text = "Execute as external program"
##        et.SubElement(elem, "br")
##    # an output subwidget:
##    CrunchyPlugin.services.insert_io_subwidget(page, elem, uid)
##
##
##
### we need some unique javascript in the page; note how the
### "/exec"  and /run_external handlers referred to above as required
### services appear here
### with a random session id appended for security reasons.
##exec_jscode= """
##function exec_code(uid){
##    code=editAreaLoader.getValue("code_"+uid);
##    var j = new XMLHttpRequest();
##    j.open("POST", "/exec%s?uid="+uid, false);
##    j.send(code);
##};
##function exec_code_externally(uid){
##    code=editAreaLoader.getValue("code_"+uid);
##    var j = new XMLHttpRequest();
##    j.open("POST", "/run_external%s?uid="+uid, false);
##    j.send(code);
##};
##"""%(CrunchyPlugin.session_random_id, CrunchyPlugin.session_random_id)
