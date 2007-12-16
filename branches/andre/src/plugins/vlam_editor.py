"""  Crunchy editor plugin.

From some Python code (possibly including a simulated interpreter session)
contained inside a <pre> element, it creates an editor for a user to
enter or modify some code.

This module is meant to be used as an example of how to create a custom
Crunchy plugin; it probably contains more comments than necessary
for people familiar with the Crunchy plugin architecture.
"""

import copy
import os

# All plugins should import the crunchy plugin API
import src.CrunchyPlugin as CrunchyPlugin
import src.configuration as configuration
from src.utilities import extract_log_id
_ = CrunchyPlugin._

# The set of other "widgets/services" provided by this plugin
provides = set(["editor_widget"])
# The set of other "widgets/services" required from other plugins
requires = set(["io_widget", "/exec", "/run_external", "style_pycode",
               "editarea"])

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
    CrunchyPlugin.register_tag_handler("pre", "title", "editor",
                                                        insert_editor)
    CrunchyPlugin.register_service(insert_editor_subwidget,
                                            "insert_editor_subwidget")
    CrunchyPlugin.register_tag_handler("pre", "title", "alternate_python_version",
                                                        insert_alternate_python)
    # shorter name version of the above
    CrunchyPlugin.register_tag_handler("pre", "title", "alt_py",
                                                        insert_alternate_python)

def insert_editor_subwidget(page, elem, uid, code="\n"):
    """inserts an Elementtree that is an editor,
    used to provide a basic insert_editor_subwidget service
    """
    inp = CrunchyPlugin.SubElement(elem, "textarea")
    inp.attrib["rows"] = "10"
    inp.attrib["cols"] = "80"
    editor_id = "code_" + uid
    inp.attrib["id"] = editor_id
    if code == "":
        code = "\n"
    inp.text = code
    CrunchyPlugin.services.enable_editarea(page, elem, editor_id)

def insert_editor(page, elem, uid):
    """handles the editor widget"""
    vlam = elem.attrib["title"]
    log_id = extract_log_id(vlam)
    if log_id:
        t = 'editor'
        configuration.defaults.logging_uids[uid] = (log_id, t)

    # When a security mode is set to "display ...", we only parse the
    # page, but no Python execution from is allowed from that page.
    # If that is the case, we won't include javascript either, to make
    # thus making the source easier to read.
    if 'display' not in configuration.defaults.page_security_level(page.url):
        if not page.includes("exec_included"):
            page.add_include("exec_included")
            page.add_js_code(exec_jscode)
    # then we can go ahead and add html markup, extracting the Python
    # code to be executed in the process
    code, markup, error = CrunchyPlugin.services.style_pycode(page, elem)
    if error is not None:
        markup = copy.deepcopy(elem)
    if log_id:
        configuration.defaults.log[log_id] = [CrunchyPlugin.tostring(markup)]
    # reset the original element to use it as a container.  For those
    # familiar with dealing with ElementTree Elements, in other context,
    # note that the style_doctest() method extracted all of the existing
    # text, removing any original markup (and other elements), so that we
    # do not need to save either the "text" attribute or the "tail" one
    # before resetting the element.
    elem.clear()
    elem.tag = "div"
    elem.attrib["id"] = "div_"+uid
    elem.attrib['class'] = "crunchy"
    # determine where the code should appear; we can't have both
    # no-pre and no-copy at the same time
    if not "no-pre" in vlam:
        elem.insert(0, markup)
        if error is not None:
            try:  # usually the error is a warning meant to be inserted
                elem.insert(0, error)
            except:
                pass
    if (("no-copy" in vlam) and not ("no-pre" in vlam)) or (not code):
        code = "\n"
    CrunchyPlugin.services.insert_editor_subwidget(page, elem, uid, code)
    #some spacing if buttons are needed, they appear below.
    if "external in vlam" or not "no-internal" in vlam:
        CrunchyPlugin.SubElement(elem, "br")
    # the actual buttons used for code execution; we make sure the
    # button for external execution, if required, appear first.
    #
    # note: as the code is written, it is possible that an execution
    # button will NOT be included.  Perhaps the tutorial writer wants
    # the user to only execute code from the "save and run" option
    # of the editor...

    btn = CrunchyPlugin.SubElement(elem, "button")
    # path_label required in all cases to avoid javascript error
    path_label = CrunchyPlugin.SubElement(elem, "span")
    path_label.attrib['id'] = 'path_' + uid
    path_label.text = configuration.defaults.temp_dir + os.path.sep + "temp.py"

    if "external" in vlam:
        btn.attrib["onclick"] = "exec_code_externally('%s')" % uid
        btn.text = _("Execute as external program")
        if log_id:  # override - probably not useful to log
            t = 'run_external_editor'
            configuration.defaults.logging_uids[uid] = (log_id, t)
        path_label.attrib['class'] = 'path_info'
        if not "no-internal" in vlam:
            CrunchyPlugin.SubElement(elem, "br")
            btn2 = CrunchyPlugin.SubElement(elem, "button")
            btn2.attrib["onclick"] = "exec_code('%s')" % uid
            btn2.text = _("Execute as separate thread")
    else:
        path_label.attrib['style'] = 'display:none'  #keep hidden since not required
        btn.attrib["onclick"] = "exec_code('%s')" % uid
        btn.text = _("Execute")
    # leaving some space to start output on next line, below last button
    CrunchyPlugin.SubElement(elem, "br")
    # an output subwidget:
    CrunchyPlugin.services.insert_io_subwidget(page, elem, uid)

def insert_alternate_python(page, elem, uid):
    """handles the python widget"""
    vlam = elem.attrib["title"]
    log_id = extract_log_id(vlam)
    if log_id:
        t = 'editor'
        configuration.defaults.logging_uids[uid] = (log_id, t)

    if 'display' not in configuration.defaults.page_security_level(page.url):
        if not page.includes("exec_included"):
            page.add_include("exec_included")
            page.add_js_code(exec_jscode)

    code, markup, error = CrunchyPlugin.services.style_pycode(page, elem)
    if error is not None:
        markup = copy.deepcopy(elem)
    if log_id:
        configuration.defaults.log[log_id] = [CrunchyPlugin.tostring(markup)]

    elem.clear()
    elem.tag = "div"
    elem.attrib["id"] = "div_"+uid
    elem.attrib['class'] = "crunchy"
    if not "no-pre" in vlam:
        elem.insert(0, markup)
        if error is not None:
            try:  # usually the error is a warning meant to be inserted
                elem.insert(0, error)
            except:
                pass
    if (("no-copy" in vlam) and not ("no-pre" in vlam)) or (not code):
        code = "\n"
    CrunchyPlugin.services.insert_editor_subwidget(page, elem, uid, code)

    form1 = CrunchyPlugin.SubElement(elem, 'form', name='form1_')
    span = CrunchyPlugin.SubElement(form1, 'span')
    span.text = _('Alternate Python path: ')
    span.attrib['class'] = 'alt_python'
    input = CrunchyPlugin.SubElement(form1, 'input', id='input1_'+uid, size='50',
                            value=configuration.defaults.alternate_python_version)
    input.attrib['class'] = 'alt_python'
    CrunchyPlugin.SubElement(elem, "br")

    btn = CrunchyPlugin.SubElement(elem, "button")
    path_label = CrunchyPlugin.SubElement(elem, "span")
    path_label.attrib['id'] = 'path_' + uid
    path_label.text = configuration.defaults.temp_dir + os.path.sep + "temp.py"

    btn.attrib["onclick"] = "exec_code_externally_python_interpreter('%s')" % uid
    btn.text = _("Execute as external program")
    path_label.attrib['class'] = 'path_info'


# we need some unique javascript in the page; note how the
# "/exec"  and /run_external handlers referred to above as required
# services appear here
# with a random session id appended for security reasons.
exec_jscode= """
function exec_code(uid){
    code=editAreaLoader.getValue("code_"+uid);
    if (code == undefined) {
        code = document.getElementById("code_"+uid).value;
    }
    var j = new XMLHttpRequest();
    j.open("POST", "/exec%s?uid="+uid, false);
    j.send(code);
};
function exec_code_externally(uid){
    code=editAreaLoader.getValue("code_"+uid);
    if (code == undefined) {
        code = document.getElementById("code_"+uid).value;
    }
    path = document.getElementById("path_"+uid).innerHTML;
    var j = new XMLHttpRequest();
    j.open("POST", "/save_and_run%s?uid="+uid, false);
    j.send(path+"_::EOF::_"+code);
};
function exec_code_externally_python_interpreter(uid){
    code=editAreaLoader.getValue("code_"+uid);
    if (code == undefined) {
        code = document.getElementById("code_"+uid).value;
    }
    path = document.getElementById("path_"+uid).innerHTML;
    var j = new XMLHttpRequest();
    j.open("POST", "/save_and_run_python_interpreter%s?uid="+uid, false);
    inp = document.getElementById("input1_"+uid).value;
    j.send(inp+"_::EOF::_"+path+"_::EOF::_"+code);
};
"""%(CrunchyPlugin.session_random_id, CrunchyPlugin.session_random_id, CrunchyPlugin.session_random_id)
